"""ชั้น 1 — ทุกหน้า × ทุก role โหลดได้ / role gating ทำงาน / analytics รันได้"""
import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import USERS

PAGE_ROLES = {
    "pages/0_🏠_Home.py":               {"admin", "marketing", "sales", "support"},
    "pages/1_📢_Marketing.py":           {"admin", "marketing"},
    "pages/2_📞_Sales_Followup.py":      {"admin", "sales"},
    "pages/3_🧾_Order_Billing.py":       {"admin", "sales"},
    "pages/4_👤_Customer_Profile.py":    {"admin", "marketing", "sales", "support"},
    "pages/5_🎫_Support_Ticket.py":      {"admin", "support"},
    "pages/6_📊_Analytics_Dashboard.py": {"admin", "marketing", "sales", "support"},
    "pages/9_🌐_Portal.py":             {"guest"},
}
ALL_ROLES = set(USERS)


def test_login_screen_renders():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert not at.exception
    assert len(at.button) >= 10          # 10 employee + 1 guest


@pytest.mark.parametrize("page,roles", PAGE_ROLES.items())
def test_allowed_roles_load(page, roles):
    for role in roles:
        at = AppTest.from_file(page, default_timeout=240)
        at.session_state["user"] = USERS[role]
        at.run()
        assert not at.exception, f"{page} as {role}: {at.exception}"


@pytest.mark.parametrize("page,roles", PAGE_ROLES.items())
def test_denied_roles_blocked(page, roles):
    denied = next(r for r in ALL_ROLES if r not in roles)
    at = AppTest.from_file(page, default_timeout=60)
    at.session_state["user"] = USERS[denied]
    at.run()
    assert not at.exception
    assert list(at.error), f"{page} should block {denied}"


@pytest.mark.parametrize("mod", [
    "analytics.lead_scoring", "analytics.rfm_segmentation",
    "analytics.churn_health", "analytics.campaign_roi"])
def test_analytics_modules_run(mod):
    import importlib
    m = importlib.import_module(mod)
    if hasattr(m, "train"):
        r = m.train("rf")
        assert r.metrics["ROC-AUC"] > 0.6
    elif hasattr(m, "build_rfm"):
        assert not m.build_rfm().empty
    elif hasattr(m, "build_health"):
        assert not m.build_health().empty
    elif hasattr(m, "campaign_overview"):
        assert not m.campaign_overview().empty
