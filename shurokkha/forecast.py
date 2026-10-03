"""Chronological forecasting with only features available before opening."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from .data import AGENTS

TARGETS = ["cash_in", "cash_out"]
FEATURES = ["hour","dow","payday","weekend","day_index","agent_code"] + [f"{c}_{lag}" for c in TARGETS for lag in (1,7,14)]


def features(data):
    d = data.sort_values(["agent","hour","date"]).copy()
    d["dow"] = d.date.dt.dayofweek
    d["day_index"] = (d.date-pd.Timestamp("2026-01-01")).dt.days
    d["agent_code"] = d.agent.map({a:i for i,a in enumerate(AGENTS)})
    for c in TARGETS:
        for lag in (1,7,14):
            d[f"{c}_{lag}"] = d.groupby(["agent","hour"])[c].shift(lag)
    return d.sort_values(["date","agent","hour"]).dropna(subset=FEATURES).reset_index(drop=True)


def baseline(frame):
    return np.column_stack([(frame[f"{c}_7"]+frame[f"{c}_14"])/2 for c in TARGETS])


def fit_forecaster(data):
    frame = features(data)
    dates = sorted(frame.date.unique())
    test_start, val_start = pd.Timestamp(dates[-21]), pd.Timestamp(dates[-42])
    train = frame[frame.date<val_start]
    val = frame[(frame.date>=val_start)&(frame.date<test_start)]
    test = frame[frame.date>=test_start].copy()
    model = ExtraTreesRegressor(n_estimators=100, min_samples_leaf=8, max_features=.9, random_state=42,n_jobs=1)
    model.fit(train[FEATURES],train[TARGETS])
    vp = np.maximum(0,model.predict(val[FEATURES]))
    residual = np.abs(val[TARGETS].to_numpy()-vp)
    radius = np.quantile(residual,.9,axis=0)
    model_test = np.maximum(0,model.predict(test[FEATURES]))
    base_test = baseline(test)
    metrics=[]
    for name,pred in [("Historical same-weekday average",base_test),("Extra Trees",model_test)]:
        for i,c in enumerate(TARGETS):
            metrics.append({"model":name,"target":c,"MAE_BDT":round(mean_absolute_error(test[c],pred[:,i]),2)})
    coverage = ((test[TARGETS].to_numpy()>=np.maximum(0,model_test-radius))&(test[TARGETS].to_numpy()<=model_test+radius)).mean(axis=0)
    ratios = val[TARGETS].sum(axis=1).to_numpy()/np.maximum(vp.sum(axis=1),1)
    multipliers = tuple(float(x) for x in np.clip(np.quantile(ratios,[.2,.5,.8]),.4,2.5))
    return {"model":model,"frame":frame,"test":test,"radius":radius,"metrics":metrics,
            "coverage":coverage.tolist(),"multipliers":multipliers,
            "train_rows":len(train),"validation_rows":len(val),"test_rows":len(test),
            "validation_start":str(val_start.date()),"test_start":str(test_start.date()),
            "train_end":str(train.date.max().date()),"model_predictions":model_test,"baseline_predictions":base_test}


def forecast_day(bundle, agent, date, method="model"):
    rows = bundle["frame"][(bundle["frame"].agent==agent)&(bundle["frame"].date==pd.Timestamp(date))].sort_values("hour")
    if len(rows)!=12:
        raise ValueError("Select a complete historical replay day with 14 days of prior history.")
    pred = np.maximum(0,bundle["model"].predict(rows[FEATURES])) if method=="model" else baseline(rows)
    out = pd.DataFrame({"hour":rows.hour.to_numpy(),"cash_in":pred[:,0],"cash_out":pred[:,1]})
    for i,c in enumerate(TARGETS):
        out[f"{c}_lower"] = np.maximum(0,pred[:,i]-bundle["radius"][i])
        out[f"{c}_upper"] = pred[:,i]+bundle["radius"][i]
    return out
