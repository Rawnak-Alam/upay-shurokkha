import numpy as np
import pytest
from shurokkha.data import generate_demand, events_from_hourly
from shurokkha.liquidity import Action,Economics,simulate,recommend
from shurokkha.forecast import features,FEATURES
from shurokkha.safety import PaymentContext,text_dataset,fit_safety,assess


def test_cash_in_out_signs_and_conservation():
    r=simulate([(9,"cash_in",1000),(10,"cash_out",700)],2000,3000)
    assert (r["cash_final"],r["float_final"])==(2300,2700)
    assert r["served_requests"]==2


def test_refusal_does_not_change_balances_or_earn_commission():
    r=simulate([(9,"cash_out",1001)],1000,500)
    assert r["refused_requests"]==1 and r["cash_final"]==1000 and r["commission"]==0


def test_infeasible_exchange_fails_without_creating_capital():
    r=simulate([],1000,500,Action(9,600))
    assert r["action_failed"] and not r["action_executed"]
    assert r["cash_final"]+r["float_final"]==1500 and r["rebalance_cost"]==0


def test_exchange_cost_only_on_executed_action():
    r=simulate([],1000,2000,Action(9,1000),Economics(fixed_cost=25,variable_cost=.001))
    assert r["rebalance_cost"]==26 and r["net_earnings"]==-26
    assert r["cash_final"]==2000 and r["float_final"]==1000


def test_extreme_cost_selects_no_action():
    f=generate_demand(1).query("agent=='A01'")
    a,_=recommend(f,1000,19000,Economics(fixed_cost=100000),"Lower cost")
    assert a.cash_delta==0


def test_zero_capital_cannot_serve_positive_requests():
    r=simulate([(9,"cash_in",100),(9,"cash_out",100)],0,0)
    assert r["served_requests"]==0 and r["refused_requests"]==2


def test_forecast_features_do_not_use_same_day_targets():
    d=generate_demand(30)
    before=features(d)
    date=d.date.max()
    d.loc[d.date==date,["cash_in","cash_out"]]=1e9
    after=features(d)
    np.testing.assert_array_equal(before.loc[before.date==date,FEATURES],after.loc[after.date==date,FEATURES])


def test_safety_families_are_disjoint():
    df=text_dataset()
    assert df.groupby("family").split.nunique().max()==1


def test_missing_history_does_not_invent_prior_recipient_or_typical_amount():
    context = PaymentContext(amount=20000, usual_amount=1000,
                             new_recipient=True, history_available=False)
    result = assess(fit_safety(), context)
    assert result["level"] == "Insufficient information"
    assert "First payment" not in result["contributions"]
    assert "Unusual amount" not in result["contributions"]


def test_same_seed_same_requested_sequence():
    d=generate_demand(1).query("agent=='A01'")
    assert events_from_hourly(d)==events_from_hourly(d)

@pytest.mark.parametrize("amount",[-1,0,float("nan"),float("inf")])
def test_payment_validation(amount):
    with pytest.raises(ValueError): PaymentContext(amount=amount)
