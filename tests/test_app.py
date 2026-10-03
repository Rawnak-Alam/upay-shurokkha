from streamlit.testing.v1 import AppTest
from pathlib import Path
APP=Path(__file__).resolve().parents[1]/"app.py"


def test_end_to_end_workspaces():
    at=AppTest.from_file(APP,default_timeout=60).run()
    assert not at.exception
    at.toggle[0].set_value(True).run()
    assert not at.exception and len(at.dataframe)>=1
    at.sidebar.radio[0].set_value('Payment Safety').run()
    at.selectbox[0].set_value('Suspicious account request').run()
    next(b for b in at.button if b.label=='Check payment').click().run()
    assert not at.exception
    assert any(x.label=='Concern index / 100' and int(x.value)>=65 for x in at.metric)
    next(b for b in at.button if b.label=='Request human review').click().run()
    at.sidebar.radio[0].set_value('Case Review').run()
    assert not at.exception
    assert any(m.value=='Review requested' for m in at.metric)
    at.selectbox[1].set_value('More evidence needed').run()
    next(b for b in at.button if b.label=='Save demo review').click().run()
    assert not at.exception
    at.sidebar.radio[0].set_value('Evidence & Guide').run()
    assert not at.exception and len(at.dataframe)>=5


def test_expensive_exchange_and_missing_history():
    at=AppTest.from_file(APP,default_timeout=60).run()
    at.selectbox[2].set_value('High rebalance cost').run()
    assert not at.exception
    assert any('Keep the current balances' in e.value for e in at.info)
    at.sidebar.radio[0].set_value('Payment Safety').run()
    at.selectbox[0].set_value('Limited recipient information').run()
    next(b for b in at.button if b.label=='Check payment').click().run()
    assert not at.exception
    assert any(s.value=='Insufficient information' for s in at.subheader)
    assert next(b for b in at.button if b.label=='Continue simulation').disabled
