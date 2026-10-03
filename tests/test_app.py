from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def button(at, label):
    return next(item for item in at.button if item.label == label)


def test_simple_agent_and_payment_flows():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert any(m.label == "Physical cash" for m in at.metric)
    at.selectbox[1].set_value("Exchange is expensive").run()
    assert not at.exception
    assert any("Keep the current balances" in x.value for x in at.markdown)
    at.segmented_control[0].set_value("Safety").run()
    at.selectbox[0].set_value("Urgent account reactivation request").run()
    button(at, "Review before sending").click().run()
    assert not at.exception
    assert any("High concern" in x.value for x in at.markdown)
    button(at, "Request demo review").click().run()
    at.segmented_control[0].set_value("Cases").run()
    assert not at.exception
    assert any(m.value == "Review requested" for m in at.metric)
    at.segmented_control[0].set_value("Evidence").run()
    assert not at.exception


def test_missing_history_stays_unknown():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.segmented_control[0].set_value("Safety").run()
    at.selectbox[0].set_value("No prior recipient history").run()
    button(at, "Review before sending").click().run()
    assert not at.exception
    assert any("Insufficient information" in x.value for x in at.markdown)
    assert button(at, "Continue demo").disabled
    assert at.session_state["cases"][-1]["score"] == 0
    assert at.session_state["cases"][-1]["context"]["new_recipient"] is False
