"""Run with: python -m streamlit run app.py"""
from pathlib import Path
import json
import base64
import uuid
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shurokkha import __version__
from shurokkha.data import generate_demand,events_from_hourly,AGENTS
from shurokkha.forecast import fit_forecaster,forecast_day
from shurokkha.liquidity import Economics,Action,recommend,simulate
from shurokkha.safety import fit_safety,PaymentContext,assess

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title="Upay Shurokkha | Decision Lab",page_icon="🛡️",layout="wide")
font_data=base64.b64encode((ROOT/"assets/NotoSansBengali.ttf").read_bytes()).decode()
st.markdown(f"<style>@font-face{{font-family:ShurokkhaBengali;src:url(data:font/ttf;base64,{font_data}) format('truetype');font-weight:100 900;}} [data-testid='stMarkdownContainer'] p,[data-testid='stMetricValue']{{font-family:'Source Sans Pro',ShurokkhaBengali,sans-serif;}}</style>",unsafe_allow_html=True)
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1300px}h1,h2,h3{letter-spacing:-.025em}
[data-testid="stSidebar"]{background:#14283e}[data-testid="stSidebar"] *{color:#f3f7fb}
[data-testid="stSidebar"] [data-baseweb="radio"]{background:transparent}
[data-testid="stMetric"]{background:white;border:1px solid #e1e8ed;padding:18px;border-radius:12px}
.hero{background:#14283e;color:white;padding:28px 32px;border-radius:16px;margin-bottom:24px}
.hero h1{color:white;font-size:36px;margin:0}.hero p{color:#cbd9e5;margin:8px 0 0}
.eyebrow{color:#70dec1;font-size:12px;font-weight:700;letter-spacing:2px;margin-bottom:9px}
</style>''',unsafe_allow_html=True)

@st.cache_resource
def resources():
    data=generate_demand()
    return data,fit_forecaster(data),fit_safety()

@st.cache_data
def read_metrics():
    p=ROOT/"artifacts/metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def money(x): return f"৳{x:,.0f}"


def plot_layout(fig,ytitle="BDT"):
    fig.update_layout(template="plotly_white",height=340,margin=dict(l=8,r=8,t=20,b=10),
                      paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h",y=-.2),yaxis_title=ytitle,
                      xaxis=dict(title="Hour of day",tickmode="linear",dtick=2),font=dict(color="#14283e"))
    return fig


def hero(title,subtitle):
    st.markdown(f'<div class="hero"><div class="eyebrow">UPAY SHUROKKHA · PROTOTYPE</div><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.title("Shurokkha")
    st.caption("Safer decisions. Better preparation.")
    page=st.radio("Workspace",["Agent Planning","Payment Safety","Case Review","Evidence & Guide"],label_visibility="collapsed")
    st.divider()
    st.write("Independent hackathon prototype")
    st.caption("All profiles, activity and results are synthetic. No money moves in this app.")
    st.caption(f"Version {__version__} · No API key required")

with st.spinner("Preparing reproducible demo models…"):
    data,forecast_bundle,safety_bundle=resources()

if page=="Agent Planning":
    hero("Prepare for the next customer", "Forecast cash and electronic float. Compare an affordable action with doing nothing.")
    st.caption("Historical replay: predictions use only information available before the selected day. Balances and cost assumptions are editable.")
    c1,c2,c3=st.columns([1.4,1,1.4])
    agent=c1.selectbox("Synthetic agent",list(AGENTS),format_func=lambda a:f"{a} · {AGENTS[a]}")
    dates=sorted(forecast_bundle["test"].date.dt.date.unique())
    date=c2.selectbox("Replay day",dates,index=len(dates)-1)
    scenario=c3.selectbox("Starting scenario",["Cash shortage","Float shortage","Balanced reserves","Low capital","High rebalance cost","Unexpected cash-out surge"])
    defaults={"Cash shortage":(6000,24000,25),"Float shortage":(25000,3000,25),"Balanced reserves":(25000,25000,25),"Low capital":(1000,1000,25),"High rebalance cost":(6000,24000,5000),"Unexpected cash-out surge":(6000,24000,25)}
    d=defaults[scenario]
    with st.expander("Balances, costs and service preference",expanded=True):
        a,b,c,e=st.columns(4)
        cash=a.number_input("Physical cash (BDT)",0.,200000.,float(d[0]),step=1000.,key=f"cash-{scenario}")
        flt=b.number_input("Electronic float (BDT)",0.,200000.,float(d[1]),step=1000.,key=f"float-{scenario}")
        cost=c.number_input("Fixed exchange cost (BDT)",0.,10000.,float(d[2]),step=5.,key=f"cost-{scenario}")
        preference=e.selectbox("Service preference",["Lower cost","Balanced","Higher availability"])
        a,b,c=st.columns(3)
        commission=a.number_input("Assumed commission (%)",0.,5.,.4,step=.05)/100
        var_cost=b.number_input("Assumed exchange cost (%)",0.,5.,.1,step=.05)/100
        capacity=c.number_input("Maximum single exchange (BDT)",0.,100000.,20000.,step=1000.)
        st.caption("Illustrative economics, not upay rates. Fees and commission use a separate operating budget. Preference adds a service value of 0 / 0.001 / 0.004 BDT per refused BDT avoided; it may trade profit for availability.")
    ec=Economics(commission,cost,var_cost,capacity)
    pred=forecast_day(forecast_bundle,agent,date)
    action,candidates=recommend(pred,cash,flt,ec,preference,forecast_bundle["multipliers"])
    row=candidates[(candidates.hour==action.hour)&(candidates.cash_delta==action.cash_delta)].iloc[0]
    no=candidates[candidates.cash_delta==0].iloc[0]
    a,b,c,d=st.columns(4)
    a.metric("Available working capital",money(cash+flt))
    b.metric("Forecast cash-in demand",money(pred.cash_in.sum()))
    c.metric("Forecast cash-out demand",money(pred.cash_out.sum()))
    d.metric("Expected net change",money(row.expected_net-no.expected_net))
    if action.cash_delta>0:
        st.success(f"Suggested action · Before {action.hour:02d}:00, exchange {money(action.cash_delta)} of electronic float for physical cash.")
    elif action.cash_delta<0:
        st.success(f"Suggested action · Before {action.hour:02d}:00, exchange {money(-action.cash_delta)} of physical cash for electronic float.")
    else:
        st.info("Suggested action · Keep the current balances. No tested exchange improves the selected objective.")
    st.caption("Recommendation assumes an available exchange partner and completion before the stated hour. It must be rechecked against actual balances. Future partner availability is not modeled.")
    expected=simulate(events_from_hourly(pred),cash,flt,Action(),ec)
    shortage=[x["hour"] for x in expected["trace"] if x["refused_requests"]]
    if shortage:
        st.warning(f"Without rebalancing, the point-forecast replay first refuses a request around {shortage[0]:02d}:00. This is a scenario result, not a guarantee.")
    left,right=st.columns(2)
    with left:
        st.subheader("Expected demand")
        fig=go.Figure()
        for col,label,color,rgba in [("cash_in","Cash-in","#07866e","rgba(7,134,110,.10)"),("cash_out","Cash-out","#d37b22","rgba(211,123,34,.10)")]:
            fig.add_trace(go.Scatter(mode="lines",x=pred.hour,y=pred[f"{col}_upper"],line=dict(width=0),showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(mode="lines",x=pred.hour,y=pred[f"{col}_lower"],line=dict(width=0),fill="tonexty",fillcolor=rgba,showlegend=False,hoverinfo="skip"))
            fig.add_trace(go.Scatter(mode="lines",x=pred.hour,y=pred[col],name=label,line=dict(color=color,width=3)))
        st.plotly_chart(plot_layout(fig),width="stretch")
        st.caption("Shaded ranges use the 90th percentile of absolute errors on validation data; actual test coverage is shown in Evidence. They are not guaranteed 90% intervals.")
    with right:
        st.subheader("Balances if demand matches forecast")
        planned=simulate(events_from_hourly(pred),cash,flt,action,ec)
        fig=go.Figure()
        for res,prefix,dash in [(expected,"No action","dot"),(planned,"Suggested","solid")]:
            tr=pd.DataFrame(res["trace"])
            for col,label,color in [("physical_cash","cash","#07866e"),("electronic_float","float","#4978c6")]:
                fig.add_trace(go.Scatter(mode="lines",x=tr.hour,y=tr[col],name=f"{prefix}: {label}",line=dict(color=color,dash=dash)))
        st.plotly_chart(plot_layout(fig),width="stretch")
    if row.expected_refused_value>0:
        st.info(f"Some demand remains unserved in the recommendation scenarios: mean {money(row.expected_refused_value)}. Exchanging cash and float cannot create more total working capital.")
    if st.toggle("Reveal actual synthetic day and compare outcomes",value=False):
        actual=forecast_bundle["test"][(forecast_bundle["test"].agent==agent)&(forecast_bundle["test"].date==pd.Timestamp(date))].copy()
        if scenario=="Unexpected cash-out surge":
            actual.loc[actual.hour>=15,"cash_out"]*=2
            st.warning("Stress scenario: cash-out demand doubles after 15:00 without advance notice to the forecast.")
        events=events_from_hourly(actual,seed=17)
        base_pred=forecast_day(forecast_bundle,agent,date,"baseline")
        base_action,_=recommend(base_pred,cash,flt,ec,preference,forecast_bundle["multipliers"])
        table=[]
        for label,act in [("No action",Action()),("Historical forecast + optimizer",base_action),("ML forecast + optimizer",action)]:
            result=simulate(events,cash,flt,act,ec)
            table.append({"Strategy":label,"Served requests":result["served_requests"],"Refused requests":result["refused_requests"],"Net earnings (BDT)":round(result["net_earnings"],2),"Exchange cost (BDT)":round(result["rebalance_cost"],2),"Exchange failed":result["action_failed"]})
        st.dataframe(pd.DataFrame(table),hide_index=True,width="stretch")
        st.caption("Same requested tickets, arrival order, capital and fees for every strategy. Net earnings = assumed commission minus exchange costs; rent, financing and other business costs are outside this simulation.")
    with st.expander("Inspect the recommendation and export"):
        st.dataframe(candidates.head(12),hide_index=True,width="stretch")
        st.download_button("Download forecast CSV",pred.to_csv(index=False),"forecast.csv","text/csv")
        st.download_button("Download proposed action",json.dumps({"agent":agent,"date":str(date),"hour":action.hour,"cash_delta":action.cash_delta,"cash":cash,"float":flt,"assumptions":ec.__dict__,"preference":preference},indent=2),"action.json","application/json")

elif page=="Payment Safety":
    hero("Check before sending", "A concern score with reasons and a next step. All recipients below are fictional.")
    st.info("A score of 82/100 does not mean an 82% chance of fraud. This prototype cannot verify a person's honesty.")
    preset=st.selectbox("Try a scenario",["Ordinary family payment","Suspicious account request","Legitimate large payment","Limited recipient information","Possible account takeover"])
    presets={
        "Ordinary family payment":(1000,1500,False,False,False,0,True,"Sending money to my mother for groceries"),
        "Suspicious account request":(8000,1000,True,False,False,1,True,"A caller says I must pay immediately to reactivate my account"),
        "Legitimate large payment":(12000,1500,True,False,False,0,True,"Paying a large hospital bill after confirming with the billing desk"),
        "Limited recipient information":(1500,1500,True,False,False,0,False,""),
        "Possible account takeover":(20000,1000,True,True,True,0,True,"")}
    p=presets[preset]
    with st.form("payment-input"):
        a,b=st.columns(2)
        amount=a.number_input("Transfer amount (BDT)",1.,200000.,float(p[0]),key=f"amount-{preset}")
        usual=b.number_input("Sender's usual amount (BDT)",1.,200000.,float(p[1]),key=f"usual-{preset}")
        description=st.text_area("Why are you sending? (optional, Bangla / Banglish / English)",p[7],max_chars=2000,key=f"description-{preset}")
        st.caption("Use fictional examples. Text is processed locally in the app and kept only in this browser session's demo case list.")
        with st.expander("Synthetic account evidence",expanded=True):
            a,b,c=st.columns(3)
            new=a.checkbox("First transfer to recipient",p[2],key=f"new-{preset}")
            recovery=b.checkbox("Recent account recovery",p[3],key=f"recovery-{preset}")
            device=c.checkbox("New device",p[4],key=f"device-{preset}")
            cases=a.number_input("Previously reviewed adverse cases",0,5,p[5],key=f"cases-{preset}")
            history=b.checkbox("Recipient history available",p[6],key=f"history-{preset}")
        submitted=st.form_submit_button("Check payment",type="primary")
    if submitted:
        ctx=PaymentContext(amount,usual,new,recovery,device,cases,history,description)
        result=assess(safety_bundle,ctx)
        result["case_id"]="DEMO-"+uuid.uuid4().hex[:6].upper()
        result["scenario"]=preset
        result["customer_action"]="Pending"
        result["review_status"]="Not reviewed"
        st.session_state.setdefault("cases",[]).append(result)
        st.session_state["last_case_id"]=result["case_id"]
    last_id=st.session_state.get("last_case_id")
    result=next((x for x in st.session_state.get("cases",[]) if x["case_id"]==last_id),None)
    if result:
        st.divider()
        st.caption(f"Last submitted check: {result['case_id']} · {result['scenario']} · {money(result['context']['amount'])}. Changed inputs require a new check.")
        a,b=st.columns([1,3])
        a.metric("Concern index / 100",result["score"])
        b.subheader(result["level"])
        for reason in result["reasons"]: b.write("• "+reason)
        if result["limited_information"]: st.warning("Recipient information is limited. A low score cannot establish safety.")
        st.write(result["action"])
        st.write(result["bangla"])
        a,b,c=st.columns(3)
        if a.button("Cancel simulated transfer"):
            result["customer_action"]="Cancelled"; st.success("Simulated transfer cancelled. No money moved.")
        if b.button("Request human review"):
            result["customer_action"]="Review requested"; st.info("Demo case is available in Case Review. No external support request was sent.")
        checked=st.checkbox("I independently verified the recipient and purpose",key=f"verified-{last_id}")
        if c.button("Continue simulation",disabled=not checked):
            result["customer_action"]="Continued after confirmation"; st.success("Simulation completed. No real transaction was created.")
        st.caption("Account/device warnings require provider-approved controls in production. This demo does not authorize payments.")
        with st.expander("Inspect score contributions"):
            st.json(result["contributions"])
            st.caption("The text model output is remapped into a 0–60 contribution; contextual rules add up to a capped total of 100. Thresholds: 35 medium, 65 high. Index weights are design assumptions.")

elif page=="Case Review":
    hero("Inspect evidence before acting", "Human review workspace for this session's synthetic payment checks.")
    cases=st.session_state.get("cases",[])
    if not cases:
        st.info("Run a check in Payment Safety first. Its evidence and customer action will appear here.")
    else:
        case_id=st.selectbox("Case",[x["case_id"] for x in cases])
        case=next(x for x in cases if x["case_id"]==case_id)
        a,b,c=st.columns(3)
        a.metric("Concern index",case["score"]);b.metric("Customer action",case["customer_action"]);c.metric("Level",case["level"])
        st.json({"context":case["context"],"reasons":case["reasons"],"contributions":case["contributions"]})
        status=st.selectbox("Reviewer disposition",["Not reviewed","More evidence needed","Escalate for investigation","Closed: insufficient evidence"],index=["Not reviewed","More evidence needed","Escalate for investigation","Closed: insufficient evidence"].index(case["review_status"]))
        if st.button("Save demo review"):
            case["review_status"]=status;st.success("Review saved in this session.")
        st.download_button("Export synthetic case evidence",json.dumps(case,ensure_ascii=False,indent=2),f"{case_id}.json","application/json")
        if st.button("Clear this session's demo cases"):
            st.session_state["cases"]=[];st.session_state.pop("last_case_id",None);st.rerun()
    st.caption("No authentication or role enforcement is implemented in this public synthetic demo. Production requires access control, audit logs, consent, retention limits and governed evidence access.")

else:
    hero("Evidence, assumptions and limits", "Inspect the results. Reproduce them. Challenge the assumptions.")
    m=read_metrics()
    if m:
        st.subheader("Forecasting on later, unseen days")
        st.dataframe(pd.DataFrame(m["forecast"]["metrics"]),hide_index=True,width="stretch")
        st.caption(f"Training ends {m['forecast']['train_end']}; validation starts {m['forecast']['validation_start']}; test starts {m['forecast']['test_start']}. No test labels used to fit models or set intervals.")
        st.write("Observed interval coverage: cash-in {:.1%}, cash-out {:.1%}.".format(*m["forecast"]["interval_coverage"]))
        st.subheader("Agent outcomes — same demand and starting capital")
        st.dataframe(pd.DataFrame(m["liquidity"]["strategies"]),hide_index=True,width="stretch")
        st.caption(f"Means over {m['liquidity']['agent_days']} synthetic agent-days. Fixed starting cash ৳6,000 + float ৳24,000. Lower-cost preference. All fees are assumptions.")
        st.write(f"ML versus historical forecasting: mean net difference {money(m['liquidity']['ml_vs_historical_mean_net_delta'])} per agent-day; {m['liquidity']['ml_vs_historical_wins']} wins and {m['liquidity']['ml_vs_historical_losses']} losses.")
        st.subheader("Text classification on held-out scenario families")
        st.dataframe(pd.DataFrame(m["safety"]["metrics"]).T,width="stretch")
        st.caption("Only 24 test sentences, eight per language. These results evaluate the text classifier, not the complete concern index or real fraud prevention.")
        st.dataframe(pd.DataFrame(m["safety"]["by_language"]).T,width="stretch")
        with st.expander("Inspect mistakes in held-out text"):
            holdout=pd.read_csv(ROOT/"artifacts/safety_holdout.csv")
            st.dataframe(holdout[holdout.label.astype(bool)!=holdout.model_warning],hide_index=True,width="stretch")
        st.subheader("Stress cases")
        st.dataframe(pd.DataFrame(m["liquidity"]["stress"]),hide_index=True,width="stretch")
        st.download_button("Download complete measured results",json.dumps(m,indent=2),"metrics.json","application/json")
    st.subheader("How to validate")
    st.markdown("""1. Change cash, float and exchange costs in **Agent Planning**. Try zero capital and a very expensive exchange.
2. Reveal actual demand and check whether the recommendation helped or lost money.
3. Try ordinary, suspicious, unusual legitimate and missing-information examples in **Payment Safety**.
4. Review the exact evidence and customer choice in **Case Review**.
5. Run `python -m pytest -q` and `python scripts/evaluate.py` locally to reproduce the checks.""")
    st.subheader("What remains unproven")
    st.write("Demand patterns and commission assumptions are invented for simulation. Real histories may omit refused requests. A small hand-written language dataset cannot cover real scams, dialects, negation or adversarial wording. The model can make false warnings and misses. Scores do not certify recipients. One instantaneous exchange per day is a simplification; no partner capacity, travel delay or financing is modeled.")
    st.write("Phase 2 can replace synthetic data adapters, change cost/capital constraints, add forecast updates or impose new review rules without rewriting the UI. A real pilot requires governed data, role-based access, uncertainty validation and human-approved financial controls.")
