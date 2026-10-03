"""Deterministic balance accounting and constrained action selection."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math
import numpy as np
import pandas as pd
from .data import events_from_hourly

@dataclass(frozen=True)
class Economics:
    commission_rate: float = .004  # illustrative fraction of served value
    fixed_cost: float = 25.
    variable_cost: float = .001
    max_exchange: float = 20000.
    def __post_init__(self):
        for v in asdict(self).values():
            if not math.isfinite(v) or v < 0:
                raise ValueError("Costs, commission and capacity must be finite and nonnegative.")

@dataclass(frozen=True)
class Action:
    hour: int = 9
    cash_delta: float = 0.  # positive: exchange float for physical cash
    def __post_init__(self):
        if self.hour not in range(9, 21) or not math.isfinite(self.cash_delta):
            raise ValueError("Invalid exchange action.")


def simulate(events, cash, float_balance, action=None, economics=None, trace=True):
    economics = economics or Economics()
    action = action or Action()
    if not all(math.isfinite(v) and v >= 0 for v in (cash, float_balance)):
        raise ValueError("Balances must be finite and nonnegative.")
    initial_total = cash + float_balance
    served = refused = 0
    served_value = refused_value = cost = 0.
    executed = failed = False
    hourly = []
    by_hour = {h: [] for h in range(9, 21)}
    for hour, kind, amount in events:
        if hour not in by_hour or kind not in ("cash_in", "cash_out") or not math.isfinite(amount) or amount < 0:
            raise ValueError("Invalid requested transaction.")
        by_hour[hour].append((kind, amount))
    shortage_hours = 0
    for hour in range(9, 21):
        hr_refused = 0
        if hour == action.hour and action.cash_delta:
            d = action.cash_delta
            if abs(d) <= economics.max_exchange and cash+d >= -1e-8 and float_balance-d >= -1e-8:
                cash += d
                float_balance -= d
                cost = economics.fixed_cost + economics.variable_cost*abs(d)
                executed = True
            else:
                failed = True  # Do not execute a now-infeasible instruction.
        for kind, amount in by_hour[hour]:
            available = float_balance if kind == "cash_in" else cash
            if available + 1e-8 >= amount:
                delta = amount if kind == "cash_in" else -amount
                cash += delta
                float_balance -= delta
                served += 1
                served_value += amount
            else:
                refused += 1
                refused_value += amount
                hr_refused += 1
        shortage_hours += int(hr_refused > 0)
        if trace:
            hourly.append({"hour": hour, "physical_cash": cash, "electronic_float": float_balance, "refused_requests": hr_refused})
    assert abs(cash + float_balance - initial_total) < 1e-5
    commission = served_value*economics.commission_rate
    return {"served_requests": served, "refused_requests": refused, "served_value": served_value,
            "refused_value": refused_value, "commission": commission, "rebalance_cost": cost,
            "net_earnings": commission-cost, "shortage_hours": shortage_hours,
            "action_executed": executed, "action_failed": failed, "cash_final": cash,
            "float_final": float_balance, "trace": hourly}


def recommend(forecast, cash, float_balance, economics=None, preference="Balanced", multipliers=(.8,1.,1.2)):
    """Grid-search one exchange at 9, 12 or 15; include no action.

    Three demand scenarios plus differing within-hour ticket orders expose some
    uncertainty. No realized future requests enter this decision.
    """
    economics = economics or Economics()
    total = cash + float_balance
    bound = min(economics.max_exchange, total)
    grid = np.unique(np.r_[np.linspace(-bound,bound,9), 0., float_balance, -cash])
    actions = [Action()] + [Action(h, round(float(d),2)) for h in (9,12,15) for d in grid if d and abs(d)<=bound]
    event_sets = []
    for i,m in enumerate(multipliers):
        f = forecast[["hour","cash_in","cash_out"]].copy()
        f[["cash_in","cash_out"]] *= m
        event_sets.append(events_from_hourly(f, seed=80+i))
    # The value assigned to avoiding a refused taka is a disclosed service preference.
    service_weight = {"Lower cost":0., "Balanced":.001, "Higher availability":.004}[preference]
    rows = []
    for action in actions:
        outcomes = [simulate(e,cash,float_balance,action,economics,False) for e in event_sets]
        if any(x["action_failed"] for x in outcomes):
            continue
        net = float(np.mean([o["net_earnings"] for o in outcomes]))
        refused = float(np.mean([o["refused_value"] for o in outcomes]))
        rows.append({"hour":action.hour,"cash_delta":action.cash_delta,"expected_net":net,
                     "expected_refused_value":refused,"objective":net-service_weight*refused})
    table = pd.DataFrame(rows).sort_values(["objective","cash_delta"],ascending=[False,True],kind="stable")
    best = table.iloc[0]
    no_action = table.loc[table.cash_delta==0].iloc[0]
    # Keep no-action in an objective tie to avoid unnecessary movement.
    if best.objective <= no_action.objective+1e-8:
        best = no_action
    return Action(int(best.hour),float(best.cash_delta)), table.reset_index(drop=True)
