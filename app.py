"""Interactive synthetic agent planning and pre-payment demo."""
from pathlib import Path
import base64
import json
import uuid
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from shurokkha import __version__
from shurokkha.data import generate_demand, events_from_hourly, AGENTS
from shurokkha.forecast import fit_forecaster, forecast_day
from shurokkha.liquidity import Economics, Action, recommend, simulate
from shurokkha.safety import fit_safety, PaymentContext, assess

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Upay Shurokkha | Demo", page_icon="🛡️", layout="wide")
font_data = base64.b64encode((ROOT / "assets/NotoSansBengali.ttf").read_bytes()).decode("ascii")
st.markdown("""<style>
@font-face{font-family:ShurokkhaBangla;src:url(data:font/ttf;base64,{font_data}) format('truetype');font-weight:100 900}
:root{--upay-blue:#126AA7;--upay-blue-dark:#10456E;--upay-gold:#F9BB2B;--upay-ink:#17324B;--upay-paper:#F4F8FC}
html,body,.stApp,[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"],input,textarea,button{
 font-family:"Segoe UI",ShurokkhaBangla,Arial,sans-serif}
.stApp{background:var(--upay-paper);color:var(--upay-ink)}
.block-container{padding-top:2rem;max-width:1050px;padding-bottom:4rem}
h1,h2,h3{letter-spacing:-.025em;color:var(--upay-blue-dark)}
[data-testid="stSidebar"]{background:#FFFFFF;border-right:1px solid #D9E7F2}
[data-testid="stSidebar"] *{color:var(--upay-ink)}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1{color:var(--upay-blue);font-weight:800}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#E8F3FC;border-left:4px solid var(--upay-gold);border-radius:7px}
[data-testid="stMetric"]{background:#FFFFFF;border:1px solid #D9E7F2;border-top:4px solid var(--upay-blue);padding:16px;border-radius:12px}
[data-testid="stMetricValue"]{color:var(--upay-blue-dark)}
[data-testid="stForm"],[data-testid="stExpander"]{background:#FFFFFF;border:1px solid #D9E7F2;border-radius:12px}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{
 background:var(--upay-blue);border-color:var(--upay-blue);color:#FFFFFF;border-radius:9px;font-weight:700}
div.stButton>button[kind="primary"]:hover,div.stFormSubmitButton>button[kind="primary"]:hover{background:var(--upay-blue-dark)}
.hero{background:linear-gradient(115deg,#10456E 0%,#126AA7 100%);border-bottom:5px solid var(--upay-gold);
 color:#FFFFFF;padding:25px 30px;border-radius:16px;margin-bottom:22px}
.hero h1{color:#FFFFFF;font-size:34px;margin:0}.hero p{color:#E7F4FF;margin:8px 0 0}
.eyebrow{color:#FFE199;font-size:12px;font-weight:700;letter-spacing:2px;margin-bottom:9px}
.decision,.risk{padding:20px 24px;border-radius:12px;margin:18px 0;background:#FFFFFF}
.decision{border:1px solid #C8E1F1;border-left:6px solid var(--upay-blue)}
.risk{border:1px solid #F4DC99;border-left:6px solid var(--upay-gold)}
.decision strong,.risk strong{font-size:23px;color:var(--upay-blue-dark)}
.decision p,.risk p{margin:7px 0 0;color:#365570}
</style>""".replace("{font_data}", font_data), unsafe_allow_html=True)


@st.cache_resource
def resources():
    data = generate_demand()
    return fit_forecaster(data), fit_safety()


@st.cache_data
def read_metrics():
    file = ROOT / "artifacts/metrics.json"
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else None


def money(value):
    return f"৳{value:,.0f}"


def hero(title, subtitle):
    st.markdown(f'<div class="hero"><div class="eyebrow">SHUROKKHA · INDEPENDENT PROTOTYPE</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


with st.sidebar:
    st.title("Shurokkha")
    st.caption("A fictional demonstration")
    page = st.radio("Workspace", ["Agent Planning", "Payment Safety", "Case Review", "Evidence & Guide"], label_visibility="collapsed")
    st.divider()
    st.caption(f"All profiles, transactions and outcomes are synthetic. No upay API or real money. Version {__version__}")

with st.spinner("Preparing demo models…"):
    forecast_bundle, safety_bundle = resources()

if page == "Agent Planning":
    hero("Today's cash & float plan", "Prepare physical cash and electronic balance for expected customers.")
    st.caption("DEMO DATA · upay publicly describes an agent dashboard, item-wise transactions, real-time statements and commissions. No internal records are available here.")
    a, b = st.columns(2)
    agent = a.selectbox("Example agent", list(AGENTS), format_func=lambda x: AGENTS[x])
    scenario = b.selectbox("Example day", ["Cash running low", "Float running low", "Exchange is expensive", "Very little capital"])
    samples = {"Cash running low": (6000, 24000, 25), "Float running low": (25000, 3000, 25),
               "Exchange is expensive": (6000, 24000, 5000), "Very little capital": (1000, 1000, 25)}
    initial_cash, initial_float, cost = samples[scenario]
    a, b = st.columns(2)
    cash = a.number_input("Physical cash counted now (৳)", min_value=0., max_value=200000., value=float(initial_cash),
                          step=1000., key=f"cash-{scenario}")
    flt = b.number_input("Electronic balance shown in wallet (৳)", min_value=0., max_value=200000.,
                         value=float(initial_float), step=1000., key=f"float-{scenario}")
    st.caption("Cash is entered by the agent. The wallet balance is a demo value, not a live upay balance.")
    date = max(forecast_bundle["test"].date.dt.date.unique())
    pred = forecast_day(forecast_bundle, agent, date)
    economics = Economics(fixed_cost=cost)
    action, candidates = recommend(pred, cash, flt, economics, "Lower cost", forecast_bundle["multipliers"])
    selected = candidates[(candidates.hour == action.hour) & (candidates.cash_delta == action.cash_delta)].iloc[0]
    no_action = candidates[candidates.cash_delta == 0].iloc[0]
    a, b, c = st.columns(3)
    a.metric("Physical cash", money(cash))
    b.metric("Electronic float", money(flt))
    c.metric("Expected cash-out", money(pred.cash_out.sum()))
    if action.cash_delta > 0:
        headline = f"Get {money(action.cash_delta)} in cash before {action.hour:02d}:00"
        detail = "Exchange electronic float for physical cash with an available partner."
    elif action.cash_delta < 0:
        headline = f"Add {money(-action.cash_delta)} to float before {action.hour:02d}:00"
        detail = "Exchange physical cash for electronic float with an available partner."
    else:
        headline = "Keep the current balances"
        detail = "No tested exchange improved estimated net earnings at the assumed cost."
    st.markdown(f'<div class="decision"><strong>{headline}</strong><p>{detail}</p></div>', unsafe_allow_html=True)
    base = simulate(events_from_hourly(pred), cash, flt, Action(), economics)
    shortage = [x["hour"] for x in base["trace"] if x["refused_requests"]]
    st.subheader("Why this suggestion?")
    st.write(f"• A forecast from the **fictional agent transaction history** expects {money(pred.cash_in.sum())} cash-in and {money(pred.cash_out.sum())} cash-out requests today.")
    st.write(f"• You supplied {money(cash)} cash and {money(flt)} float. " +
             (f"Without an exchange, the point forecast first misses a request around {shortage[0]:02d}:00." if shortage
              else "The point forecast does not show a shortage without an exchange."))
    st.write(f"• Estimated change in commission after exchange costs: **{money(selected.expected_net - no_action.expected_net)}**.")
    st.caption("This is a scenario, not a guaranteed outcome. Commission and costs are assumed, not upay rates. Confirm balance and partner availability before acting.")
    with st.expander("How does this cash–float exchange work?"):
        st.write("Conversion: **৳1 electronic float ↔ ৳1 physical cash**. It changes the form of the agent's working capital, not its total.")
        st.write(f"Illustrative exchange service cost: **{money(cost)} fixed + 0.1% of the amount exchanged**. "
                 f"For this recommendation, the estimated cost is **{money(cost + abs(action.cash_delta) * economics.variable_cost) if action.cash_delta else money(0)}**.")
        st.write("The assumed commission on served transactions is 0.4%, and the largest single exchange considered is ৳20,000. These figures are prototype assumptions, not published upay fees or commissions.")
    with st.expander("Show forecast and replay"):
        fig = go.Figure()
        for col, label, color in [("cash_in", "Cash-in", "#126AA7"), ("cash_out", "Cash-out", "#E0A11B")]:
            fig.add_trace(go.Scatter(x=pred.hour, y=pred[col], name=label, mode="lines", line=dict(color=color, width=3)))
        fig.update_layout(template="plotly_white", height=300, xaxis_title="Hour", yaxis_title="BDT",
                          margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig, width="stretch")
        if st.toggle("Reveal actual synthetic day"):
            actual = forecast_bundle["test"][(forecast_bundle["test"].agent == agent) &
                                              (forecast_bundle["test"].date == pd.Timestamp(date))]
            events = events_from_hourly(actual, seed=17)
            historical, _ = recommend(forecast_day(forecast_bundle, agent, date, "baseline"), cash, flt,
                                      economics, "Lower cost", forecast_bundle["multipliers"])
            rows = []
            for label, choice in [("No exchange", Action()), ("Historical forecast", historical), ("ML suggestion", action)]:
                result = simulate(events, cash, flt, choice, economics)
                rows.append({"Strategy": label, "Served requests": result["served_requests"],
                             "Refused requests": result["refused_requests"], "Estimated net (৳)": round(result["net_earnings"], 2)})
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
            st.caption("Same fictional requests and starting balances. Net uses assumed commission and exchange cost.")

elif page == "Payment Safety":
    hero("Pause before you send", "Understand the warning and choose the next step.")
    st.caption("DEMO · Concept for a pre-payment step. No real account, identity lookup or recipient verification.")
    scenario = st.selectbox("Try a fictional payment", ["Ordinary family payment", "Urgent account reactivation request",
                                                          "Verified hospital bill", "No prior recipient history"])
    examples = {
        "Ordinary family payment": ("017••• ••432", 1000, 1500, False, True, "Sending money to my mother for groceries"),
        "Urgent account reactivation request": ("018••• ••908", 8000, 1000, True, True, "A caller says I must pay immediately to reactivate my account"),
        "Verified hospital bill": ("019••• ••617", 12000, 1500, True, True, "Paying a large hospital bill after confirming with the billing desk"),
        "No prior recipient history": ("016••• ••235", 1500, 1500, True, False, ""),
    }
    recipient, default_amount, usual, first_time, history, default_reason = examples[scenario]
    st.write(f"**Recipient:** {recipient} · fictional number")
    with st.form("payment-input"):
        amount = st.number_input("Amount to send (৳)", min_value=1., max_value=200000.,
                                 value=float(default_amount), key=f"amount-{scenario}")
        reason = st.text_area("Why are you sending? (optional)", default_reason, max_chars=2000,
                              key=f"reason-{scenario}", help="Bangla, Banglish or English. The model reads only text entered here.")
        submitted = st.form_submit_button("Review before sending", type="primary")
    if submitted:
        context = PaymentContext(amount, usual, first_time, False, False, 0, history, reason)
        result = assess(safety_bundle, context)
        result.update(case_id="DEMO-" + uuid.uuid4().hex[:6].upper(), scenario=scenario, recipient=recipient,
                      customer_action="Pending", review_status="Not reviewed")
        st.session_state.setdefault("cases", []).append(result)
        st.session_state["last_case_id"] = result["case_id"]
    result = next((item for item in st.session_state.get("cases", [])
                   if item["case_id"] == st.session_state.get("last_case_id")), None)
    if result and (result["scenario"] != scenario or result["context"]["amount"] != amount or
                   result["context"]["description"] != reason):
        result = None
        st.info("Payment details changed. Review again to update the suggestion.")
    if result:
        st.markdown(f'<div class="risk"><strong>{result["level"]} · concern index {result["score"]}/100</strong><p>{result["action"]}</p></div>', unsafe_allow_html=True)
        st.caption("Design index, not a fraud probability, recipient reputation score or upay security rating.")
        st.subheader("Why did this appear?")
        for explanation in result["reasons"]:
            st.write("• " + explanation)
        if result["limited_information"]:
            st.warning("No prior recipient history in this fictional profile. Missing information cannot establish safety.")
        if result["score"] >= 35:
            st.info("Call using a number you already trust. Never share your PIN or OTP. For account issues, use official support.")
        else:
            st.info("Check the recipient number and purpose independently before continuing.")
        st.write(result["bangla"])
        with st.expander("Where these signals came from"):
            st.write(f"**You entered:** {money(amount)} and " +
                     (f"“{reason}”." if reason else "no reason. No text signal was used."))
            st.write(f"**Fictional transaction history:** usual transfer {money(usual)}; " +
                     ("first payment to this recipient." if first_time else "recipient seen before."))
            st.write("**Unavailable:** verified complaints, real recipient identity and provider security events. None were used.")
            st.write("The text model uses a small authored dataset. Index weights are assumptions. A warning concerns the request and context; it does not accuse the recipient.")
        a, b, c = st.columns(3)
        if a.button("Cancel demo payment"):
            result["customer_action"] = "Cancelled"
            st.success("Demo payment cancelled. No money moved.")
        if b.button("Request demo review"):
            result["customer_action"] = "Review requested"
            st.info("Visible in Case Review. No external request was sent.")
        checked = st.checkbox("I independently checked the recipient and purpose", key=f"verified-{result['case_id']}")
        if c.button("Continue demo", disabled=not checked):
            result["customer_action"] = "Continued after confirmation"
            st.success("Demo completed. No real transaction was created.")

elif page == "Case Review":
    hero("Review a demo case", "Inspect only the evidence used for this fictional payment.")
    cases = st.session_state.get("cases", [])
    if not cases:
        st.info("Review a fictional payment first. It will appear here.")
    else:
        case_id = st.selectbox("Case", [x["case_id"] for x in cases])
        case = next(x for x in cases if x["case_id"] == case_id)
        a, b, c = st.columns(3)
        a.metric("Concern index", case["score"])
        b.metric("Customer action", case["customer_action"])
        c.metric("Level", case["level"])
        st.write(f"**Scenario:** {case['scenario']} · **Recipient:** {case['recipient']}")
        st.write("**Reasons:** " + " ".join(case["reasons"]))
        with st.expander("Inspect case inputs and score contributions"):
            st.json({"context": case["context"], "contributions": case["contributions"]})
        statuses = ["Not reviewed", "More evidence needed", "Escalate for investigation", "Closed: insufficient evidence"]
        status = st.selectbox("Reviewer disposition", statuses, index=statuses.index(case["review_status"]))
        if st.button("Save demo review"):
            case["review_status"] = status
            st.success("Review saved in this session.")
        st.download_button("Export synthetic case evidence", json.dumps(case, ensure_ascii=False, indent=2),
                           f"{case_id}.json", "application/json")
        if st.button("Clear demo cases"):
            st.session_state["cases"] = []
            st.session_state.pop("last_case_id", None)
            st.rerun()
    st.caption("No real case access or role enforcement. Production requires approved authentication, audit and retention.")

else:
    hero("Evidence & assumptions", "Numbers below come from one repeatable simulation, never upay operations.")
    st.subheader("What could feed a future pilot?")
    st.markdown("""| Input | Source in this demo | Production condition |
|---|---|---|
| Physical cash | Agent enters counted cash | Agent confirmation |
| Electronic balance | Fictional wallet value | Authorized balance access |
| Cash-in / cash-out history | Synthetic item-wise transactions | Governed transaction statements |
| Commission | Assumed 0.4% | Confirm actual applicable terms |
| Payment amount / recipient | Fictional customer flow | Explicit payment inputs |
| Prior recipient / typical amount | Fictional sender history | Consent and authorized history |
| Payment reason | Customer types it | Optional with privacy controls |
| Fraud complaints / device events | **Not used** | Separate approved evidence and validation |""")
    st.caption("The public upay Agent listing mentions item-wise transactions, real-time statements, commission and a dashboard; it does not disclose internal schemas or rates.")
    metrics = read_metrics()
    if metrics:
        with st.expander("Forecast evaluation on later synthetic days"):
            st.dataframe(pd.DataFrame(metrics["forecast"]["metrics"]), hide_index=True, width="stretch")
            st.write("Interval coverage (cash-in, cash-out): {:.1%}, {:.1%}.".format(*metrics["forecast"]["interval_coverage"]))
        with st.expander("Agent outcomes under the same fictional demand"):
            st.dataframe(pd.DataFrame(metrics["liquidity"]["strategies"]), hide_index=True, width="stretch")
            st.caption("63 agent-days. Fixed cash ৳6,000 and float ৳24,000. Costs and commission are assumptions.")
        with st.expander("Text model evaluation and its mistakes"):
            st.dataframe(pd.DataFrame(metrics["safety"]["metrics"]).T, width="stretch")
            st.caption("Only 24 held-out sentences; these results do not validate the combined concern index or real fraud prevention.")
            mistakes = pd.read_csv(ROOT / "artifacts/safety_holdout.csv")
            st.dataframe(mistakes[mistakes.label.astype(bool) != mistakes.model_warning], hide_index=True, width="stretch")
        st.download_button("Download measured simulation results", json.dumps(metrics, indent=2), "metrics.json", "application/json")
    st.subheader("How to demonstrate")
    st.write("Select Cash running low, explain the inputs and action, then reveal the actual synthetic day. Select Exchange is expensive to see no exchange. On Payment Safety, compare Urgent account reactivation with Verified hospital bill and inspect signal sources.")
    st.subheader("Limits")
    st.write("No production data or upay integration. Synthetic demand and invented economic terms cannot establish live benefit. The text classifier can miss or falsely flag a request; the combined concern index is not calibrated. Rebalancing partner availability, time to travel, and real refused demand need a governed pilot.")
    st.caption("Public feature reference: https://play.google.com/store/apps/details?id=bd.com.upay.agent")
