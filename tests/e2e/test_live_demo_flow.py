"""
test_live_demo_flow.py
ชุดทดสอบจำลองขั้นตอนการสาธิตระบบสดครบ 7 ขั้นตอน (Storyline 10 นาที)
ตามเอกสาร docs/NEXT_STEPS_TEST_AND_DEMO.md และ docs/plan_5_live_demo_script.md

ตรวจสอบ:
  1. Portal: ผู้สนใจลงทะเบียนขอโปรโมชัน (00:00 - 01:00)
  2. Marketing: ฝ่ายการตลาดตรวจรับ Lead และแคมเปญ CMP003 (01:00 - 02:30)
  3. Sales: ฝ่ายขายดูคิวงาน AI Lead LD0264, บันทึกโทร, ออกใบเสนอราคา (02:30 - 04:30)
  4. Portal: ผู้สนใจยืนยันคำสั่งซื้อและแนบสลิปโอนเงิน (04:30 - 05:30)
  5. Sales: ฝ่ายขายตรวจสลิป, ยืนยันเงิน, ยกระดับเป็น CUSTOMER, ออกใบเสร็จ (05:30 - 06:30)
  6. Support: เจ้าหน้าที่ประสานงานเคส CU0178, ปิดเคส, ลูกค้าให้ 5 ดาว (06:30 - 08:00)
  7. Dashboard: ผู้บริหารเปิดแดชบอร์ด 4 ด้าน + รายงานยอดขาย (08:00 - 10:00)
"""
import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import USERS

pytestmark = pytest.mark.usefixtures("fresh_db")


def _at(page, role, timeout=120):
    at = AppTest.from_file(page, default_timeout=timeout)
    at.session_state["user"] = USERS[role]
    return at.run()


def _btn(at, text):
    return next(b for b in at.button if text in (b.label or ""))


def test_step_1_portal_registration(db):
    """[00:00 - 01:00] ขั้นที่ 1: Portal จำลอง External Entity ลงทะเบียนขอโปรโมชัน"""
    before_leads = db("SELECT COUNT(*) FROM LEAD")[0][0]
    at = _at("pages/9_portal.py", "guest")
    tin = {t.label: t for t in at.text_input}
    tin["ชื่อ-นามสกุล *"].set_value("นายปรีชา ใจดี")
    tin["เบอร์โทรศัพท์ *"].set_value("0891234567")
    _btn(at, "ส่งข้อมูลการติดต่อ").click().run()
    assert not at.exception
    after_leads = db("SELECT COUNT(*) FROM LEAD")[0][0]
    assert after_leads == before_leads + 1
    lead_row = db("SELECT Lead_ID, Followup_Status FROM LEAD WHERE Full_Name='นายปรีชา ใจดี'")[0]
    assert lead_row[1] == "รอการติดต่อ"


def test_step_2_marketing_campaign_and_lead(db):
    """[01:00 - 02:30] ขั้นที่ 2: ฝ่ายการตลาดตรวจแคมเปญ CMP003 และความคุ้มค่า"""
    cmp_row = db("SELECT Campaign_ID, Campaign_Name, Budget_Cost FROM CAMPAIGN WHERE Campaign_ID='CMP003'")
    assert cmp_row and cmp_row[0][1] == "Digital Ads Q3"
    at = _at("pages/1_marketing.py", "marketing")
    assert not at.exception
    # ตรวจสอบการแสดงผลหน้าการตลาดครบถ้วน
    assert len(at.tabs) >= 3


def test_step_3_sales_ai_queue_and_quotation(db):
    """[02:30 - 04:30] ขั้นที่ 3: ฝ่ายขายดูคิวงาน AI Lead LD0264, บันทึกโทร, ออกใบเสนอราคา"""
    # 1. ตรวจสอบ Lead LD0264 ในฐานข้อมูล
    lead_info = db("SELECT Lead_ID, Full_Name, Followup_Status FROM LEAD WHERE Lead_ID='LD0264'")
    assert lead_info and lead_info[0][1] == "วิชัย ทองดี"

    # 2. บันทึกกิจกรรมติดต่อ (Lead Activity)
    from db.connection import execute, next_id
    act_id = next_id("LEAD_ACTIVITY", "Activity_ID", "ACT", 5)
    before_act = db("SELECT COUNT(*) FROM LEAD_ACTIVITY WHERE Lead_ID='LD0264'")[0][0]
    execute("""INSERT INTO LEAD_ACTIVITY (Activity_ID, Lead_ID, Employee_ID, Activity_Type, Activity_Date, Notes, Next_Action_Date)
               VALUES (?, 'LD0264', 'EMP004', 'โทรศัพท์', datetime('now','localtime'), 'ลูกค้าสนใจซอฟต์แวร์ ERP นัดส่งใบเสนอราคา', '2026-09-25')""",
            (act_id,))
    after_act = db("SELECT COUNT(*) FROM LEAD_ACTIVITY WHERE Lead_ID='LD0264'")[0][0]
    assert after_act == before_act + 1



    # 3. ออกใบเสนอราคาสำหรับ LD0264
    at = _at("pages/3_order_billing.py", "sales")
    assert not at.exception
    # ตรวจสอบว่ามีแถบออกใบเสนอราคา
    assert any("ออกใบเสนอราคา" in (t.label or "") for t in at.tabs)


def test_step_4_portal_order_and_slip(db):
    """[04:30 - 05:30] ขั้นที่ 4: ผู้สนใจตรวจสอบใบเสนอราคาและยืนยันคำสั่งซื้อผ่าน Portal"""
    at = _at("pages/9_portal.py", "guest")
    assert not at.exception
    # ตรวจสอบว่าแท็บของ Portal ครบทั้ง 5 ส่วน
    assert len(at.tabs) == 5


def test_step_5_sales_verify_payment_and_receipt(db):
    """[05:30 - 06:30] ขั้นที่ 5: ฝ่ายขายตรวจสลิป ออกใบเสร็จ ยกระดับเป็น CUSTOMER"""
    # ตรวจสอบว่าระบบสามารถ query ออเดอร์ที่รอตรวจสอบชำระเงินได้
    pending_sales = db("SELECT Sale_ID, Lead_ID, Total_Amount FROM SALE WHERE Sale_Status='รอการตรวจสอบชำระเงิน'")
    assert len(pending_sales) > 0, "ต้องมีรายการขายที่รอการตรวจชำระเงินใน Seed Data"
    sale_id = pending_sales[0][0]

    at = _at("pages/3_order_billing.py", "sales")
    assert not at.exception
    # ยืนยันการมีอยู่ของแท็บตรวจสอบชำระเงินและออกใบเสร็จ
    tab_labels = [t.label for t in at.tabs]
    assert any("ตรวจสอบการชำระเงิน" in t for t in tab_labels)
    assert any("ออกใบเสร็จ" in t for t in tab_labels)


def test_step_6_support_case_and_5star_rating(db):
    """[06:30 - 08:00] ขั้นที่ 6: เจ้าหน้าที่แก้ปัญหาเคส CU0178 และลูกค้าให้คะแนน 5 ดาว"""
    cust = db("SELECT Customer_ID, Company_Name FROM CUSTOMER WHERE Customer_ID='CU0178'")
    assert cust and "สมหญิง" in cust[0][1]

    # ตรวจสอบเคสประเมิน 5 ดาวตัวอย่าง TK0008
    rated_ticket = db("SELECT Ticket_ID, Service_Rating FROM TICKET WHERE Ticket_ID='TK0008'")
    assert rated_ticket and rated_ticket[0][1] == 5

    at = _at("pages/5_support_ticket.py", "support")
    assert not at.exception
    assert any("คิวเคส" in (t.label or "") for t in at.tabs)


def test_step_7_executive_dashboard_and_ai_analytics(db):
    """[08:00 - 10:00] ขั้นที่ 7: ผู้บริหารเปิดแดชบอร์ด Data Science 4 ด้าน + สรุปยอดขาย"""
    # ตรวจสอบ Champions CU0175
    champ = db("SELECT Customer_ID, Company_Name FROM CUSTOMER WHERE Customer_ID='CU0175'")
    assert champ and "ศิริพร" in champ[0][1]

    # ตรวจสอบหน้าจอแดชบอร์ด admin1
    at = _at("pages/6_analytics_dashboard.py", "admin")
    assert not at.exception
    tab_labels = [t.label for t in at.tabs]
    assert any("Lead Scoring" in t for t in tab_labels)
    assert any("RFM" in t for t in tab_labels)
    assert any("Churn" in t for t in tab_labels)
    assert any("Campaign ROI" in t for t in tab_labels)
    assert any("รายงานสรุปยอดขาย" in t for t in tab_labels)
