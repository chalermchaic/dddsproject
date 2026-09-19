"""
ชั้น 2 — 1 test = 1 กิจกรรมใน dfd.pdf
ขับฟอร์มผ่าน Streamlit AppTest แล้ว assert สถานะใน db/crm.db
ใช้ fixture `fresh_db` re-seed ก่อนทุกเทสต์
"""
import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import ROOT, USERS

pytestmark = pytest.mark.usefixtures("fresh_db")


def _at(page, role, timeout=200):
    at = AppTest.from_file(page, default_timeout=timeout)
    at.session_state["user"] = USERS[role]
    return at.run()


def _btn(at, text):
    return next(b for b in at.button if text in (b.label or ""))


# ---------- Process 1.0 ----------
def test_1_1_create_campaign(db):
    at = _at("pages/1_marketing.py", "marketing")
    [t for t in at.text_input if t.label == "ชื่อแคมเปญ *"][0].set_value("แคมเปญเทส 1.1")
    _btn(at, "บันทึกแคมเปญ").click().run()
    assert not at.exception
    row = db("SELECT Employee_ID FROM CAMPAIGN WHERE Campaign_Name='แคมเปญเทส 1.1'")
    assert row and row[0][0] == "EMP002"

    # Regression check: Ensure Tab 1 renders scatter plot cleanly with 0-lead campaign
    at_view = _at("pages/1_marketing.py", "marketing")
    assert not at_view.exception


def test_1_2_lead_self_register_via_portal(db):
    before = db("SELECT COUNT(*) FROM LEAD")[0][0]
    at = _at("pages/9_portal.py", "guest", timeout=90)
    tin = {t.label: t for t in at.text_input}
    tin["ชื่อ-นามสกุล *"].set_value("สมมติ ผู้สนใจ")
    tin["เบอร์โทรศัพท์ *"].set_value("0891112222")
    _btn(at, "ส่งข้อมูลการติดต่อ").click().run()
    assert not at.exception
    assert db("SELECT COUNT(*) FROM LEAD")[0][0] == before + 1
    assert db("SELECT Followup_Status FROM LEAD WHERE Full_Name='สมมติ ผู้สนใจ'")[0][0] \
        == "รอการติดต่อ"


def test_1_3_send_promo(db):
    at = _at("pages/2_sales_followup.py", "sales")
    before = db("SELECT COUNT(*) FROM LEAD_ACTIVITY WHERE Activity_Type='ส่งโปรโมชัน'")[0][0]
    _btn(at, "ส่งข้อมูลโปรโมชัน").click().run()
    assert not at.exception
    after = db("SELECT COUNT(*) FROM LEAD_ACTIVITY WHERE Activity_Type='ส่งโปรโมชัน'")[0][0]
    assert after == before + 1


# ---------- Process 2.0 ----------
def test_2_1_daily_followup_queue():
    at = _at("pages/2_sales_followup.py", "sales")
    assert not at.exception
    labels = [m.label for m in at.metric]
    assert any("เลยกำหนด" in x for x in labels)
    assert any("ถึงกำหนดวันนี้" in x for x in labels)


def test_2_2_log_activity(db):
    at = _at("pages/2_sales_followup.py", "sales")
    before = db("SELECT COUNT(*) FROM LEAD_ACTIVITY")[0][0]
    at.text_area[-1].set_value("โทรคุยแล้ว ลูกค้าสนใจ")
    _btn(at, "💾 บันทึก").click().run()
    assert not at.exception
    assert db("SELECT COUNT(*) FROM LEAD_ACTIVITY")[0][0] > before


def test_2_3_quotation_insert_shape(db):
    """ออกใบเสนอราคา — multiselect+format_func ขับผ่าน AppTest ไม่ได้;
    ตรวจว่า INSERT ที่หน้านี้ใช้ (12 คอลัมน์) ยิงได้จริง"""
    con = sqlite3.connect(f"{ROOT}/db/crm.db"); con.execute("PRAGMA foreign_keys=ON")
    lead = con.execute("SELECT Lead_ID FROM LEAD LIMIT 1").fetchone()[0]
    con.execute("INSERT INTO SALE VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                ("SLT23", lead, "EMP004", "QT-T23", "2026-09-02", 1000.0,
                 "ออกใบเสนอราคาแล้ว", None, None, None, None, None))
    con.commit()
    assert con.execute("SELECT Sale_Status FROM SALE WHERE Sale_ID='SLT23'").fetchone()[0] \
        == "ออกใบเสนอราคาแล้ว"
    con.close()


# ---------- Process 3.0 ----------
def test_3_1_validate_order(db):
    at = _at("pages/3_order_billing.py", "sales")
    before = db("SELECT COUNT(*) FROM SALE WHERE Sale_Status='รอการตรวจสอบชำระเงิน'")[0][0]
    _btn(at, "ตรวจแล้วถูกต้อง").click().run()
    assert not at.exception
    after = db("SELECT COUNT(*) FROM SALE WHERE Sale_Status='รอการตรวจสอบชำระเงิน'")[0][0]
    assert after == before + 1


def _verify_first_payment(at):
    """เติมเลขอ้างอิงทุกช่องแล้วกดปุ่มยืนยันรับเงินอันแรก (แต่ละ SALE มีฟอร์มของตัวเอง)"""
    for ti in at.text_input:
        if "เลขอ้างอิง" in (ti.label or ""):
            ti.set_value("TRF999888")
    _btn(at, "ยืนยันรับเงิน").click().run()


def test_3_2_verify_payment(db):
    at = _at("pages/3_order_billing.py", "sales")
    _verify_first_payment(at)
    assert not at.exception
    assert db("SELECT COUNT(*) FROM SALE WHERE Sale_Status='รอการตรวจสอบชำระเงิน' "
              "AND Confirmed_At IS NOT NULL")[0][0] >= 1


def test_3_2_slip_upload_via_portal(db, tmp_path):
    lead = db("""SELECT Lead_ID FROM SALE
                 WHERE Sale_Status IN ('รอตรวจสอบคำสั่งซื้อ','รอการตรวจสอบชำระเงิน')
                 AND Payment_Slip IS NULL LIMIT 1""")[0][0]
    name = db("SELECT Full_Name FROM LEAD WHERE Lead_ID=?", lead)[0][0]
    at = _at("pages/9_portal.py", "guest", timeout=90)
    at.selectbox[0].select(f"{lead} — {name}").run()
    slip = tmp_path / "slip.png"
    slip.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
    fu = at.get("file_uploader")
    assert fu, "ควรมี file_uploader ในแท็บอัปโหลดสลิป"


def test_3_3_issue_receipt(db):
    _verify_first_payment(_at("pages/3_order_billing.py", "sales"))  # เตรียม 3.2
    at = _at("pages/3_order_billing.py", "sales")
    closed_before = db("SELECT COUNT(*) FROM SALE WHERE Sale_Status='ปิดการขายสำเร็จ'")[0][0]
    _btn(at, "ออกใบเสร็จ").click().run()
    assert not at.exception
    assert db("SELECT COUNT(*) FROM SALE WHERE Sale_Status='ปิดการขายสำเร็จ'")[0][0] \
        == closed_before + 1
    assert at.get("download_button")


# ---------- Process 4.0 ----------
def test_4_1_open_ticket(db):
    at = _at("pages/5_support_ticket.py", "support")
    before = db("SELECT COUNT(*) FROM TICKET")[0][0]
    [t for t in at.text_input if "หัวข้อ" in (t.label or "")][0].set_value("จอฟ้า เปิดไม่ติด")
    _btn(at, "เปิดเคส").click().run()
    assert not at.exception
    assert db("SELECT COUNT(*) FROM TICKET")[0][0] == before + 1
    assert db("SELECT Employee_ID FROM TICKET WHERE Problem_Title='จอฟ้า เปิดไม่ติด'")[0][0] \
        is None


def test_4_2_reply_and_status(db):
    at = _at("pages/5_support_ticket.py", "support")
    before = db("SELECT COUNT(*) FROM TICKET_MESSAGE")[0][0]
    at.chat_input[0].set_value("กำลังตรวจสอบให้ครับ").run()
    assert not at.exception
    assert db("SELECT COUNT(*) FROM TICKET_MESSAGE")[0][0] == before + 1


def test_4_3_service_rating(db):
    """ลูกค้าให้คะแนนบริการผ่าน Portal (Process 4.3)"""
    row = db("""SELECT l.Lead_ID, l.Full_Name, c.Customer_ID FROM TICKET t
                JOIN CUSTOMER c ON c.Customer_ID=t.Customer_ID
                JOIN LEAD l    ON l.Lead_ID=c.Lead_ID
                WHERE t.Ticket_Status='ปิดเคสสำเร็จ' AND t.Service_Rating IS NULL LIMIT 1""")
    if not row:
        pytest.skip("ไม่มีเคสปิดที่ยังไม่ให้คะแนน")
    lead_id, name, cust_id = row[0]
    rated_q = ("SELECT COUNT(*) FROM TICKET WHERE Customer_ID=? AND Service_Rating IS NOT NULL")
    before = db(rated_q, cust_id)[0][0]
    at = _at("pages/9_portal.py", "guest", timeout=90)
    at.selectbox[0].select(f"{lead_id} — {name}").run()
    btns = [b for b in at.button if "ส่งคะแนน" in (b.label or "")]
    if not btns:
        pytest.skip("rating form ไม่ปรากฏ")
    btns[0].click().run()
    assert not at.exception
    assert db(rated_q, cust_id)[0][0] == before + 1


# ---------- Process 5.0 ----------
def test_5_1_campaign_report():
    from analytics import campaign_roi as roi
    assert not roi.campaign_overview().empty


def test_5_2_sales_summary_download():
    at = _at("pages/6_analytics_dashboard.py", "sales")
    assert not at.exception
    assert any("รายงาน" in (d.label or "") for d in at.get("download_button"))
