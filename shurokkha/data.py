"""Reproducible requested demand, including requests that might be refused."""
from __future__ import annotations
import numpy as np
import pandas as pd

SEED = 20261004
AGENTS = {"A01": "Campus gate", "A02": "Neighbourhood market", "A03": "Transport hub"}
HOURS = np.arange(9, 21)


def generate_demand(days=154, seed=SEED):
    rng = np.random.default_rng(seed)
    records = []
    for a, agent in enumerate(AGENTS):
        level = [1., 1.25, .85][a]
        for day in range(days):
            date = pd.Timestamp("2026-01-01") + pd.Timedelta(days=day)
            payday = int(date.day <= 5 or date.day >= 28)
            weekend = int(date.dayofweek in (4, 5))
            shock = rng.random() < .07
            daily_noise = rng.lognormal(-.0128, .16)
            for hour in HOURS:
                # Calendar and smooth intraday effects plus independent shocks/noise.
                peak_in = 1 + .8 * np.exp(-((hour-11)/2.3)**2)
                peak_out = 1 + 1.6 * np.exp(-((hour-17)/2.2)**2)
                base_in = 2400 * level * peak_in * (1 + .3*weekend) * daily_noise
                base_out = 2200 * level * peak_out * (1 + .75*payday) * daily_noise
                if shock and hour >= 15:
                    base_out *= rng.uniform(1.5, 2.5)
                amounts = []
                for mean in (base_in, base_out):
                    amounts.append(int(max(0, round(rng.lognormal(np.log(mean)-.08, .4)/100)*100)))
                records.append((agent, date, int(hour), *amounts, payday, weekend, int(shock)))
    return pd.DataFrame(records, columns=["agent", "date", "hour", "cash_in", "cash_out", "payday", "weekend", "shock"])


def events_from_hourly(frame, seed=17):
    """Split hourly totals into requested tickets; every strategy gets same list.

    Assumes artificial 500-2500 taka tickets, shuffled within each hour.
    A final remainder may be smaller. This is not measured customer behaviour.
    """
    rng = np.random.default_rng(seed)
    result = []
    for row in frame.sort_values("hour").itertuples():
        hour_events = []
        for direction in ("cash_in", "cash_out"):
            remaining = int(round(max(0, getattr(row, direction))))
            while remaining > 0:
                amount = min(remaining, int(rng.choice([500, 1000, 1500, 2000, 2500])))
                hour_events.append((int(row.hour), direction, amount))
                remaining -= amount
        rng.shuffle(hour_events)
        result.extend(hour_events)
    return result
