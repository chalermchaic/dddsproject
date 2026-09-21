"""
สคริปต์อัตโนมัติบันทึกภาพหน้าจอการทำงานจริง (Real UI Evidence Capture)
ครอบคลุม 14 กิจกรรมย่อยตาม Data Flow Diagram (DFD Process 1.0 - 5.0)
สำหรับประกอบคู่มือการใช้งาน user_manual.docx และเอกสารรายงานโครงงาน

รัน:
    python tests/e2e/capture_manual_evidence.py
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVIDENCE = os.path.join(ROOT, "docs", "evidence")
APP_PORT = 8503


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def shot(page, name: str, wait_ms: int = 600) -> None:
    page.wait_for_timeout(wait_ms)
    out_path = os.path.join(EVIDENCE, f"{name}.png")
    page.screenshot(path=out_path, full_page=True)
    print(f"  📸 บันทึกภาพ: docs/evidence/{name}.png")


def open_menu(page, title: str) -> None:
    page.get_by_role("link", name=title).first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)


def open_tab(page, tab_name: str) -> None:
    page.get_by_role("tab").filter(has_text=tab_name).first.click()
    page.wait_for_timeout(1000)


import re


def login_as(page, base_url: str, username: str) -> None:
    page.goto(base_url, wait_until="networkidle")
    page.wait_for_timeout(800)
    if username == "guest":
        guest_btn = page.get_by_role("button").filter(has_text=re.compile(r"ผู้สนใจ|ลูกค้า"))
        if guest_btn.count() > 0:
            guest_btn.first.click()
        else:
            page.get_by_role("button", name="เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)").click()
    else:
        legacy_btn = page.get_by_role("button", name=f"เข้าใช้งานเป็น {username}")
        if legacy_btn.count() > 0 and legacy_btn.first.is_visible():
            legacy_btn.first.click()
        else:
            user_marker = page.locator(f"[data-user='{username}']")
            if user_marker.count() > 0:
                card = page.locator("[data-testid='stVerticalBlockBorderWrapper']").filter(has=user_marker)
                card.get_by_role("button", name="เข้าสู่ระบบ").first.click()
            else:
                card = page.locator("[data-testid='stVerticalBlockBorderWrapper']").filter(has_text=re.compile(rf"\b{username}\b", re.IGNORECASE))
                card.get_by_role("button", name="เข้าสู่ระบบ").first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)


def run_capture():
    os.makedirs(EVIDENCE, exist_ok=True)

    print("🌱 กำลังเตรียม Seed Data ในฐานข้อมูลจำลอง...")
    subprocess.run([sys.executable, "db/seed_data.py"], cwd=ROOT, check=True,
                   capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})

    port = _free_port()
    base_url = f"http://localhost:{port}"

    print(f"🚀 กำลังเปิด Streamlit Server บนพอร์ต {port}...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.port", str(port), "--server.headless", "true",
         "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "PYTHONUTF8": "1"}
    )

    try:
        # รอเซิร์ฟเวอร์พร้อม
        server_ready = False
        for _ in range(60):
            try:
                if urllib.request.urlopen(base_url + "/_stcore/health", timeout=2).status == 200:
                    server_ready = True
                    break
            except Exception:
                time.sleep(0.5)

        if not server_ready:
            raise RuntimeError("Streamlit Server ไม่ตอบสนองภายในเวลาที่กำหนด")

        print("⚡ เริ่มต้น Playwright Chromium เพื่อบันทึกภาพหลักฐาน...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            # -------------------------------------------------------------
            # 0. หน้าแรก / หน้า Login (Context DFD)
            # -------------------------------------------------------------
            print("\n[0] บันทึกหน้า Login Screen...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1000)
            shot(page, "00_login")

            # -------------------------------------------------------------
            # Process 1.0 — ฝ่ายการตลาด (marketing1)
            # -------------------------------------------------------------
            print("\n[1.0] กระบวนการด้านการตลาด (marketing1)...")
            login_as(page, base_url, "marketing1")
            open_menu(page, "งานการตลาด")

            # 1.1 (ก) ฟอร์มสร้างแคมเปญ
            open_tab(page, "สร้างแคมเปญ")
            page.get_by_label("ชื่อแคมเปญ *").fill("Mid-Year Super Deal 2026")
            page.get_by_label("รายละเอียดโปรโมชัน").fill("แคมเปญกระตุ้นยอดขายกลุ่ม Enterprise รับส่วนลดพิเศษ 15% พร้อมฟรีบริการ Support 1 ปี")
            shot(page, "1_1_campaign_form")

            # 1.1 (ข) บันทึกแคมเปญสำเร็จ + ดูรายการแคมเปญ
            page.get_by_role("button", name="💾 บันทึกแคมเปญ").click()
            page.wait_for_timeout(1200)
            open_tab(page, "แคมเปญทั้งหมด")
            shot(page, "1_1_campaign_saved")

            # 1.2 (ก) ฟอร์มบันทึกผู้สนใจใหม่
            open_tab(page, "บันทึกผู้สนใจใหม่")
            page.get_by_label("ชื่อ-นามสกุล *").fill("คุณวิชิต นรินทรากูล")
            page.get_by_label("เบอร์โทรศัพท์").fill("082-345-6789")
            page.get_by_label("อีเมล").fill("wichit.n@siamgroup.co.th")
            shot(page, "1_2_lead_form")

            # 1.2 (ข) ผลลัพธ์หลังบันทึกผู้สนใจ
            page.get_by_role("button", name="💾 บันทึกผู้สนใจ").click()
            page.wait_for_timeout(1500)
            shot(page, "1_2_lead_saved")

            # -------------------------------------------------------------
            # Process 2.0 & 1.3 & 3.0 — ฝ่ายขาย (sale1)
            # -------------------------------------------------------------
            print("\n[2.0 - 3.0] กระบวนการงานขายและออกเอกสาร (sale1)...")
            login_as(page, base_url, "sale1")

            # 2.1 (ก) คิวติดตามผู้สนใจประจำวัน
            open_menu(page, "ติดตามการขาย")
            open_tab(page, "คิวติดตามวันนี้")
            shot(page, "2_1_todo_queue")

            # 2.1 (ข) คิวงานจัดลำดับด้วย AI (Hot / Warm / Cold)
            open_tab(page, "คิวงานจัดลำดับด้วย AI")
            page.wait_for_timeout(1500)
            shot(page, "2_1_ai_priority")

            # 1.3 & 2.2 แท็บค้นหา & บันทึกกิจกรรม
            open_tab(page, "ค้นหา & บันทึกกิจกรรม")
            page.wait_for_timeout(1200)

            # 1.3 ส่งโปรโมชัน (เปิด expander Process 1.3 ก่อนกดส่ง)
            expander = page.locator("details").filter(has_text="ส่งรายละเอียดโปรโมชัน")
            if expander.count() > 0:
                if expander.first.get_attribute("open") is None:
                    expander.first.locator("summary").click()
                    page.wait_for_timeout(800)
            promo_btn = page.get_by_role("button", name="ส่งข้อมูลโปรโมชัน")
            if promo_btn.count() > 0:
                promo_btn.first.click()
                page.wait_for_timeout(1500)
            # ตรวจสอบว่า expander ยังคงเปิดอยู่เพื่อให้เห็นฟอร์มและข้อความแจ้งผลลัพธ์
            if expander.count() > 0 and expander.first.get_attribute("open") is None:
                expander.first.locator("summary").click()
                page.wait_for_timeout(600)
            shot(page, "1_3_promo_sent")

            # 2.2 (ก) ฟอร์มกรอกกิจกรรม
            act_note = page.get_by_label("บันทึกผลการติดต่อ")
            if act_note.count() > 0:
                act_note.first.fill("โทรประสานงาน นำเสนอโซลูชันระบบ ลูกค้าพึงพอใจและขอดูใบเสนอราคาอย่างเป็นทางการ")
            shot(page, "2_2_activity_form")

            # 2.2 (ข) บันทึกกิจกรรมสำเร็จ และดูไทม์ไลน์
            save_act_btn = page.get_by_role("button", name="💾 บันทึก")
            if save_act_btn.count() > 0:
                save_act_btn.first.click()
                page.wait_for_timeout(1500)
            shot(page, "2_2_activity_timeline")

            # 2.3 ออกใบเสนอราคา (Process 2.3)
            open_menu(page, "ใบเสนอราคา/ชำระเงิน")
            open_tab(page, "ออกใบเสนอราคา")
            page.wait_for_timeout(1000)

            # เลือกสินค้าในฟอร์มออกใบเสนอราคา
            # คลิก multiselect ของสินค้า
            ms = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค้า")
            if ms.count() == 0:
                # ลองค้นหา input multiselect ในหน้า
                ms = page.locator("[aria-label='รายการสินค้า']")
            if ms.count() > 0:
                ms.click()
                page.wait_for_timeout(500)
                # เลือกตัวเลือกแรกที่ปรากฏ
                opt = page.locator("li[role='option']").first
                if opt.count() > 0:
                    opt.click()
                    page.wait_for_timeout(500)
                # ปิด dropdown
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)

            shot(page, "2_3_quotation_form")

            # กดออกใบเสนอราคา (ปุ่มใน pages/3_order_billing.py คือ '🧾 ออกใบเสนอราคา')
            issue_q_btn = page.get_by_role("button", name="🧾 ออกใบเสนอราคา").or_(
                page.get_by_role("button", name="ออกใบเสนอราคา")
            )
            if issue_q_btn.count() > 0:
                issue_q_btn.first.click()
                page.wait_for_timeout(2000)
            shot(page, "2_3_quotation_issued")

            # 3.1 ตรวจสอบคำสั่งซื้อ
            open_tab(page, "รับ & ตรวจคำสั่งซื้อ")
            page.wait_for_timeout(1000)
            shot(page, "3_1_order_review")

            # 3.2 ตรวจสอบการชำระเงิน & สลิป
            open_tab(page, "ตรวจสอบการชำระเงิน")
            page.wait_for_timeout(1000)
            shot(page, "3_2_payment_check")

            # 3.3 ออกใบเสร็จรับเงิน + ยกระดับเป็น CUSTOMER
            open_tab(page, "ออกใบเสร็จ + บันทึกลูกค้า")
            page.wait_for_timeout(1000)
            shot(page, "3_3_receipt_issued")

            # -------------------------------------------------------------
            # Process 4.0 — ฝ่ายบริการลูกค้า (cs1)
            # -------------------------------------------------------------
            print("\n[4.0] กระบวนการบริการลูกค้าและรับแจ้งปัญหา (cs1)...")
            login_as(page, base_url, "cs1")
            open_menu(page, "รับแจ้งปัญหา")

            # 4.1 (ก) ฟอร์มเปิดเคสใหม่
            open_tab(page, "เปิดเคสใหม่")
            page.get_by_label("หัวข้อปัญหา *").fill("ไม่สามารถเปิดดูรายงานสรุปยอดขายรายไตรมาสได้")
            detail_box = page.get_by_label("รายละเอียดจากลูกค้า")
            if detail_box.count() > 0:
                detail_box.fill("ระบบแจ้งเตือนข้อผิดพลาด เกิดปัญหาการประมวลผลข้อมูลขนาดใหญ่ ขอให้ตรวจสอบด่วน")
            shot(page, "4_1_ticket_form")

            # 4.1 (ข) เปิดเคสสำเร็จ
            save_tk_btn = page.get_by_role("button", name="🎫 เปิดเคส").or_(page.get_by_role("button", name="เปิดเคส"))
            if save_tk_btn.count() > 0:
                save_tk_btn.first.click()
                page.wait_for_timeout(1500)
            shot(page, "4_1_ticket_created")

            # 4.2 คิวเคส & สนทนาแก้ไขปัญหา
            open_tab(page, "คิวเคส & สนทนา")
            page.wait_for_timeout(1000)

            # พิมพ์ตอบในช่องแชท (ถ้ามี)
            chat_box = page.get_by_placeholder("พิมพ์ข้อความตอบกลับลูกค้า...").or_(
                page.locator("[data-testid='stChatInputTextArea']")
            )
            if chat_box.count() > 0 and chat_box.first.is_visible():
                chat_box.first.fill("เจ้าหน้าที่กำลังตรวจสอบชุดข้อมูลและดำเนินการรีเซ็ตแคชให้ครับ คาดว่าจะใช้งานได้ปกติใน 15 นาที")
                chat_box.first.press("Enter")
                page.wait_for_timeout(1500)
            shot(page, "4_2_ticket_chat")

            # 4.3 (ก) ปิดเคสสำเร็จ
            upd_btn = page.get_by_role("button", name="💾 อัปเดต")
            if upd_btn.count() > 0 and upd_btn.first.is_visible():
                upd_btn.first.click()
                page.wait_for_timeout(1500)
            shot(page, "4_3_ticket_closed")

            # -------------------------------------------------------------
            # Process 4.3 (ข) & Portal — ผู้สนใจ / ลูกค้า (guest)
            # -------------------------------------------------------------
            print("\n[Portal & 4.3 Rating] มุมมองผู้สนใจและลูกค้าจำลอง (guest)...")
            login_as(page, base_url, "guest")

            # เลือกตัวตนใน Portal เพื่อให้เห็นข้อมูลตัวอย่าง
            lead_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ")
            if lead_sel.count() > 0:
                lead_sel.first.click()
                page.wait_for_timeout(500)
                opt = page.locator("li[role='option']").nth(1)
                if opt.count() > 0:
                    opt.click()
                    page.wait_for_timeout(1000)

            shot(page, "portal_home")

            # ประเมินคะแนนบริการ (แท็บ ⑤ ใบเสร็จ · แจ้งปัญหา · ให้คะแนน)
            open_tab(page, "ให้คะแนน")
            page.wait_for_timeout(1200)

            # ให้คะแนน 5 ดาวถ้ามีปุ่ม
            rate_btn = page.get_by_role("button", name="⭐ ส่งคะแนน").or_(page.get_by_role("button", name="ส่งคะแนน"))
            if rate_btn.count() > 0 and rate_btn.first.is_visible():
                rate_btn.first.click()
                page.wait_for_timeout(1000)
            shot(page, "4_3_rating_given")

            # -------------------------------------------------------------
            # Process 5.0 — รายงานและแดชบอร์ด AI (admin1 / sale1 / marketing1)
            # -------------------------------------------------------------
            print("\n[5.0] แดชบอร์ดวิเคราะห์และรายงานสรุปยอดขาย...")
            login_as(page, base_url, "admin1")
            open_menu(page, "แดชบอร์ดวิเคราะห์")

            # AI Feature 1: Lead Scoring
            open_tab(page, "Lead Scoring")
            page.wait_for_timeout(2000)
            shot(page, "6_1_lead_scoring")

            # AI Feature 2: RFM Segmentation
            open_tab(page, "RFM Segmentation")
            page.wait_for_timeout(1500)
            shot(page, "6_2_rfm")

            # AI Feature 3: Customer Health & Churn
            open_tab(page, "Customer Health & Churn")
            page.wait_for_timeout(1500)
            shot(page, "6_3_churn")

            # Process 5.1: Campaign ROI
            open_tab(page, "Campaign ROI")
            page.wait_for_timeout(2000)
            shot(page, "5_1_6_4_campaign_roi")

            # Process 5.2: รายงานสรุปยอดขาย
            open_tab(page, "รายงานสรุปยอดขาย")
            page.wait_for_timeout(2000)
            shot(page, "5_2_sales_report")

            browser.close()

        print("\n✨ บันทึกภาพหลักฐานจริงครบทุกกิจกรรมเรียบร้อยแล้วใน docs/evidence/")

    finally:
        print("🛑 กำลังปิด Streamlit Server...")
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    run_capture()
