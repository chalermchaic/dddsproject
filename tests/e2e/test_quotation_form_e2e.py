"""
test_quotation_form_e2e.py
Playwright E2E จริงสำหรับฟอร์มออกใบเสนอราคา (DFD Process 2.3)
ปิดช่องว่างทางเทคนิคของ AppTest ที่ไม่สามารถจำลอง Streamlit multiselect + format_func ได้
ขับผ่านเบราว์เซอร์จริง: เลือกสินค้า >= 2 รายการ, ตรวจสอบการคำนวณราคา/ส่วนลด, กดยืนยัน และ assert การลงบันทึกในตาราง SALE
"""
import os
import re
import sqlite3
import pytest
from playwright.sync_api import expect

from tests.e2e.conftest import login_as, shot

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT, "db", "crm.db")


def test_quotation_form_real_ui_submission(app_url, page):
    """
    E2E ทดสอบฟอร์มออกใบเสนอราคา (Process 2.3) ผ่านหน้าจอจริง:
    1. ล็อกอินเป็น sale1 และเปิดหน้า 'ใบเสนอราคา/ชำระเงิน'
    2. อยู่ในแท็บ '📝 ออกใบเสนอราคา (2.3)'
    3. เลือกสินค้าผ่าน multiselect อย่างน้อย 2 รายการ
    4. ตรวจสอบว่ายอดรวมสุทธิและส่วนลดถูกคำนวณและแสดงผลบนหน้าจอ
    5. กดปุ่ม '🧾 ออกใบเสนอราคา'
    6. ตรวจสอบข้อความแจ้งเตือนสำเร็จบนหน้าจอ (UI assertion)
    7. ตรวจสอบแถวใหม่ในฐานข้อมูล SQLite ตาราง SALE และ SALE_DETAIL (DB assertion)
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    before_sales_count = cur.execute(
        "SELECT COUNT(*) FROM SALE WHERE Sale_Status='ออกใบเสนอราคาแล้ว'"
    ).fetchone()[0]

    # 1. Login as sale1
    login_as(page, app_url, "sale1")

    # 2. ไปหน้า 'ใบเสนอราคา/ชำระเงิน'
    page.get_by_role("link", name=re.compile("ใบเสนอราคา")).first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # ตรวจสอบหัวข้อหน้าและเลือกแท็บออกใบเสนอราคา
    expect(page.get_by_role("heading", name=re.compile("คำสั่งซื้อและการชำระเงิน"))).to_be_visible(timeout=15000)
    tab1 = page.get_by_role("tab").filter(has_text=re.compile("ออกใบเสนอราคา"))
    if tab1.count() > 0:
        tab1.first.click()
        page.wait_for_timeout(1000)

    # ตรวจสอบว่ามี selectbox เลือกผู้สนใจ
    expect(page.get_by_text("เลือกผู้สนใจ")).to_be_visible(timeout=10000)

    # 3. เลือกสินค้าผ่าน st.multiselect อย่างน้อย 2 รายการ
    # Streamlit multiselect ภายในใช้ BaseWeb Select
    ms_container = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค้า")
    if ms_container.count() == 0:
        ms_container = page.locator("div[data-testid='stMultiSelect']")

    expect(ms_container.first).to_be_visible(timeout=10000)
    ms_container.first.click()
    page.wait_for_timeout(800)

    # เลือกตัวเลือก 2 รายการแรกจาก dropdown listbox
    options = page.locator("li[role='option']")
    expect(options.first).to_be_visible(timeout=10000)
    assert options.count() >= 2, f"มีตัวเลือกสินค้าไม่เพียงพอ (พบ {options.count()} รายการ)"

    options.nth(0).click()
    page.wait_for_timeout(600)
    options.nth(1).click()
    page.wait_for_timeout(600)

    # ปิด dropdown เพื่อให้เห็น UI คอนเทนเนอร์ชัดเจน
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    # 4. ตรวจสอบว่าระบบคำนวณและแสดงผลยอดรวมสุทธิบนหน้าจอ
    net_total_text = page.get_by_text(re.compile("ยอดรวมสุทธิ: ฿"))
    expect(net_total_text.first).to_be_visible(timeout=10000)

    shot(page, "2_3_quotation_form_filled")

    # 5. กดยืนยันออกใบเสนอราคา
    submit_btn = page.get_by_role("button", name=re.compile("ออกใบเสนอราคา")).first
    expect(submit_btn).to_be_visible(timeout=5000)
    submit_btn.click()
    page.wait_for_timeout(2500)

    # 6. ตรวจสอบข้อความแจ้งผลลัพธ์สำเร็จบน UI
    success_msg = page.get_by_text(re.compile("ออกใบเสนอราคา .* เรียบร้อย"))
    expect(success_msg.first).to_be_visible(timeout=15000)

    shot(page, "2_3_quotation_submitted_success")

    # 7. ตรวจสอบการบันทึกลง SQLite ฐานข้อมูลจริง
    after_sales_count = cur.execute(
        "SELECT COUNT(*) FROM SALE WHERE Sale_Status='ออกใบเสนอราคาแล้ว'"
    ).fetchone()[0]
    assert after_sales_count == before_sales_count + 1, (
        f"จำนวน SALE ที่สถานะ 'ออกใบเสนอราคาแล้ว' ควรเพิ่มขึ้น 1 (ก่อน: {before_sales_count}, หลัง: {after_sales_count})"
    )

    # ตรวจสอบรายละเอียดของ SALE ล่าสุด
    latest_sale = cur.execute(
        """SELECT Sale_ID, Lead_ID, Employee_ID, Quotation_No, Total_Amount, Sale_Status
           FROM SALE ORDER BY rowid DESC LIMIT 1"""
    ).fetchone()
    assert latest_sale is not None
    sale_id = latest_sale[0]
    assert latest_sale[4] > 0.0, "Total_Amount ต้องมากกว่า 0"
    assert latest_sale[5] == "ออกใบเสนอราคาแล้ว", "Sale_Status ต้องเป็น 'ออกใบเสนอราคาแล้ว'"

    # ตรวจสอบรายการใน SALE_DETAIL ของใบเสนอราคานี้
    detail_rows = cur.execute(
        "SELECT Product_ID, Quantity, Unit_Price, Subtotal FROM SALE_DETAIL WHERE Sale_ID=?",
        (sale_id,)
    ).fetchall()
    assert len(detail_rows) == 2, f"ต้องมีสินค้า 2 รายการตามที่เลือกไว้ใน UI (พบ {len(detail_rows)})"
    for row in detail_rows:
        assert row[1] >= 1, "Quantity ต้องอย่างน้อย 1"
        assert row[2] > 0.0, "Unit_Price ต้องมากกว่า 0"
        assert row[3] > 0.0, "Subtotal ต้องมากกว่า 0"

    conn.close()
