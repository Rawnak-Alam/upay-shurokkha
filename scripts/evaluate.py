"""Rebuild synthetic data and evidence without API keys or downloaded models."""
from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from shurokkha.data import generate_demand,events_from_hourly,AGENTS
from shurokkha.forecast import fit_forecaster,forecast_day
from shurokkha.liquidity import Economics,Action,recommend,simulate
from shurokkha.safety import fit_safety,text_dataset,assess,PaymentContext

ROOT=Path(__file__).resolve().parents[1]

def main():
    t=time.time()
    data=generate_demand()
    f=fit_forecaster(data)
    safety=fit_safety()
    rows=[]
    economics=Economics()
    for (agent,date),actual in f["test"].groupby(["agent","date"]):
        cash,float_balance=6000.,24000.
        events=events_from_hourly(actual,seed=int(date.dayofyear)*7+list(AGENTS).index(agent))
        methods={"No rebalance":Action(),"Fixed 50/50 opening reserve":Action(9,9000)}
        for method,key in [("Historical forecast + optimizer","baseline"),("ML forecast + optimizer","model")]:
            pred=forecast_day(f,agent,date,key)
            action,_=recommend(pred,cash,float_balance,economics,"Lower cost",f["multipliers"])
            methods[method]=action
        for method,action in methods.items():
            r=simulate(events,cash,float_balance,action,economics,False)
            rows.append({"agent":agent,"date":str(date.date()),"strategy":method,"cash_delta":action.cash_delta,"hour":action.hour,**{k:v for k,v in r.items() if k!="trace"}})
    replay=pd.DataFrame(rows)
    summary=replay.groupby("strategy")[["net_earnings","refused_requests","refused_value","shortage_hours","rebalance_cost","action_failed"]].mean().round(3).reset_index()
    pivot=replay.pivot(index=["agent","date"],columns="strategy",values="net_earnings")
    delta=pivot["ML forecast + optimizer"]-pivot["Historical forecast + optimizer"]
    stress=[]
    agent="A01"; date=f["test"].date.max()
    pred=forecast_day(f,agent,date)
    actual=f["test"].query("agent==@agent and date==@date")
    for label,cash,flt,cost,mult in [("Normal capital",6000,24000,25,1),("Low capital",1000,1000,25,1),("Expensive exchange",6000,24000,5000,1),("Unexpected demand shock",6000,24000,25,2)]:
        ec=Economics(fixed_cost=cost)
        a,_=recommend(pred,cash,flt,ec,"Lower cost",f["multipliers"])
        altered=actual.copy(); altered["cash_out"]*=mult
        events=events_from_hourly(altered)
        r=simulate(events,cash,flt,a,ec,False)
        b=simulate(events,cash,flt,Action(),ec,False)
        stress.append({"case":label,"cash_delta":a.cash_delta,"hour":a.hour,"net_delta_vs_no_action":round(r["net_earnings"]-b["net_earnings"],2),"refused_requests":r["refused_requests"],"action_failed":r["action_failed"]})
    out={"data":"Synthetic only; no production inference established","seed":20261004,
         "forecast":{"metrics":f["metrics"],"interval_coverage":f["coverage"],"train_rows":f["train_rows"],"validation_rows":f["validation_rows"],"test_rows":f["test_rows"],"train_end":f["train_end"],"validation_start":f["validation_start"],"test_start":f["test_start"],"scenario_multipliers":f["multipliers"]},
         "liquidity":{"agent_days":len(pivot),"initial_cash":6000,"initial_float":24000,"preference":"Lower cost","economics":economics.__dict__,"strategies":summary.to_dict("records"),"ml_vs_historical_mean_net_delta":float(delta.mean()),"ml_vs_historical_wins":int((delta>.001).sum()),"ml_vs_historical_losses":int((delta<-.001).sum()),"stress":stress},
         "safety":{"metrics":safety["metrics"],"by_language":safety["by_language"],"threshold":safety["threshold"],"train_rows":safety["train_rows"],"validation_rows":safety["validation_rows"],"test_rows":safety["test_rows"],"scope":"Text classifier evaluation only; composite concern index is not calibrated or validated as fraud probability."}}
    (ROOT/"artifacts").mkdir(exist_ok=True)
    (ROOT/"data").mkdir(exist_ok=True)
    data.to_csv(ROOT/"data/synthetic_demand.csv",index=False)
    text_dataset().to_csv(ROOT/"data/synthetic_safety_text.csv",index=False)
    replay.to_csv(ROOT/"artifacts/liquidity_replay.csv",index=False)
    safety["test"].to_csv(ROOT/"artifacts/safety_holdout.csv",index=False)
    (ROOT/"artifacts/metrics.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))
    print(f"Finished in {time.time()-t:.1f}s")

if __name__=="__main__": main()
