"""
เดินผ่าน UI จริงตามกิจกรรมใน dfd.pdf แล้วเก็บ screenshot ลง docs/evidence/
เน้นเป็น visual evidence — assert เบา ๆ ที่ heading ของหน้า (นิ่งกว่า element ย่อย)
"""
import pytest
from playwright.sync_api import expect

from tests.e2e.conftest import login_as, shot

ROLE_MENU = {
    "admin1":     ["ภาพรวม", "งานการตลาด", "ติดตามการขาย", "รับแจ้งปัญหา", "แดชบอร์ด"],
    "marketing1": ["ภาพรวม", "งานการตลาด", "แดชบอร์ด"],
    "sale1":      ["ภาพรวม", "ติดตามการขาย", "แดชบอร์ด"],
    "cs1":        ["ภาพรวม", "รับแจ้งปัญหา", "แดชบอร์ด"],
}


def open_menu(page, name):
    page.get_by_role("link", name=name).click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2500)


def test_login_screen(app_url, page):
    page.goto(app_url, wait_until="networkidle")
    expect(page.get_by_text("เลือกบัญชีผู้ใช้เพื่อเข้าสู่ระบบ")).to_be_visible(timeout=15000)
    shot(page, "00_login")


@pytest.mark.parametrize("user,items", ROLE_MENU.items())
def test_role_menu(app_url, page, user, items):
    login_as(page, app_url, user)
    for it in items:
        expect(page.get_by_role("link", name=it).first).to_be_visible(timeout=15000)
    shot(page, f"menu_{user}")


def test_marketing_campaign_page(app_url, page):
    login_as(page, app_url, "marketing1")
    open_menu(page, "งานการตลาด")
    expect(page.get_by_role("heading", name="งานการตลาด")).to_be_visible(timeout=20000)
    shot(page, "1_1_marketing")


def test_sales_followup_todo(app_url, page):
    login_as(page, app_url, "sale1")
    open_menu(page, "ติดตามการขาย")
    expect(page.get_by_role("heading", name="ติดตามผู้สนใจ")).to_be_visible(timeout=30000)
    shot(page, "2_1_todo_queue")


def test_order_billing_pipeline(app_url, page):
    login_as(page, app_url, "sale1")
    open_menu(page, "ใบเสนอราคา")
    expect(page.get_by_role("heading", name="คำสั่งซื้อและการชำระเงิน")).to_be_visible(timeout=20000)
    page.get_by_role("tab").filter(has_text="รับ & ตรวจคำสั่งซื้อ").click()
    page.wait_for_timeout(1500)
    shot(page, "3_x_order_pipeline")


def test_support_ticket_queue(app_url, page):
    login_as(page, app_url, "cs1")
    open_menu(page, "รับแจ้งปัญหา")
    expect(page.get_by_role("heading", name="ระบบรับแจ้งปัญหา")).to_be_visible(timeout=20000)
    shot(page, "4_x_support")


def test_analytics_sales_report(app_url, page):
    login_as(page, app_url, "sale1")
    open_menu(page, "แดชบอร์ด")
    expect(page.get_by_role("heading", name="แดชบอร์ดวิเคราะห์ข้อมูล")).to_be_visible(timeout=40000)
    page.get_by_role("tab").filter(has_text="รายงานสรุปยอดขาย").click()
    page.wait_for_timeout(2500)
    shot(page, "5_2_sales_report")


def test_portal_guest(app_url, page):
    login_as(page, app_url, "guest")
    expect(page.get_by_role("heading", name="Portal ผู้สนใจ / ลูกค้า")).to_be_visible(timeout=20000)
    shot(page, "portal_home")
    page.get_by_role("tab").filter(has_text="ลงทะเบียนความสนใจ").click()
    page.wait_for_timeout(1200)
    shot(page, "1_2_portal_register")
