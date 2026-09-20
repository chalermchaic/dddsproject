"""
scripts/live_browser_demo.py
ระบบสาธิตสดอัตโนมัติผ่านเบราว์เซอร์จริง (Playwright Headed Live Demo)
สำหรับแสดงการทำงานจริงของ Smart CRM Analytics ครบทั้ง 3 เคสธุรกิจ 7 ขั้นตอน (DFD Process 1.0 - 5.0)

จุดเด่น:
  - เปิดหน้าต่างเบราว์เซอร์ Chromium จริงบนหน้าจอ (Headless=False)
  - ความเร็วระดับ Slow-Mo พร้อมป้ายหัวข้อจำลอง (Floating HUD Subtitles) บนหน้าจอ
  - สาธิตการไหลของข้อมูลตั้งแต่ D1 (LEAD) -> D2 (ACTIVITY) -> D3 (SALE) -> D4 (CUSTOMER & TICKET) -> D5 (DATA SCIENCE ANALYTICS)
  - รองรับทั้งรันต่อจากเซิร์ฟเวอร์เดิม (:8501) หรือเปิด Streamlit ชั่วคราวให้อัตโนมัติ

วิธีใช้งาน:
  python scripts/live_browser_demo.py
  python scripts/live_browser_demo.py --slow-mo 1000 --pause 2.0
  python scripts/live_browser_demo.py --headless  (กรณีรันแบบไม่เปิดหน้าต่าง)
"""

import argparse
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "crm.db")


def is_port_open(port: int) -> bool:
    try:
        urllib.request.urlopen(f"http://localhost:{port}/_stcore/health", timeout=1.5)
        return True
    except Exception:
        return False


def get_free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def set_hud(page, badge: str, title: str, desc: str):
    """แสดง Floating HUD Subtitle ด้านบนของหน้าต่างเบราว์เซอร์เพื่อเป็นคำบรรยายสำหรับผู้ชม"""
    js = f"""
    (() => {{
        let el = document.getElementById('live-demo-hud');
        if (!el) {{
            el = document.createElement('div');
            el.id = 'live-demo-hud';
            el.style.position = 'fixed';
            el.style.top = '14px';
            el.style.left = '50%';
            el.style.transform = 'translateX(-50%)';
            el.style.zIndex = '9999999';
            el.style.backgroundColor = 'rgba(15, 23, 42, 0.95)';
            el.style.color = '#ffffff';
            el.style.padding = '10px 24px';
            el.style.borderRadius = '32px';
            el.style.boxShadow = '0 12px 35px rgba(0,0,0,0.45)';
            el.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            el.style.fontSize = '14px';
            el.style.border = '1.5px solid rgba(56, 189, 248, 0.5)';
            el.style.backdropFilter = 'blur(10px)';
            el.style.pointerEvents = 'none';
            el.style.transition = 'all 0.3s ease-in-out';
            el.style.textAlign = 'center';
            el.style.maxWidth = '90vw';
            document.body.appendChild(el);
        }}
        el.innerHTML = `
            <span style="background: #0284c7; color: #fff; padding: 2px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; margin-right: 8px;">{badge}</span>
            <strong style="color: #38bdf8; font-size: 15px;">{title}</strong>
            <span style="color: #cbd5e1; margin-left: 8px; font-weight: normal;">| {desc}</span>
        `;
    }})();
    """
    try:
        page.evaluate(js)
    except Exception:
        pass


def login(page, base_url: str, username: str, step_pause: float = 1.0):
    page.goto(base_url, wait_until="networkidle")
    page.wait_for_timeout(600)

    # หากมีการล็อกอินค้างอยู่ ให้กดออกจากระบบก่อน
    logout_btn = page.get_by_role("button").filter(has_text="ออกจากระบบ")
    if logout_btn.count() > 0 and logout_btn.first.is_visible():
        logout_btn.first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(600)

    if username == "guest":
        btn = page.get_by_role("button").filter(has_text="ผู้สนใจ")
        if btn.count() > 0:
            btn.first.click()
    else:
        btn = page.get_by_role("button").filter(has_text=f"เข้าใช้งานเป็น {username}")
        if btn.count() > 0:
            btn.first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(int(step_pause * 800))


def click_menu(page, title: str, step_pause: float = 1.0):
    link = page.get_by_role("link").filter(has_text=title).first
    if link.count() > 0:
        link.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(int(step_pause * 800))


def click_tab(page, tab_name: str, step_pause: float = 1.0):
    tab = page.get_by_role("tab").filter(has_text=tab_name).first
    if tab.count() > 0:
        tab.click()
        page.wait_for_timeout(int(step_pause * 800))


def wait_next_step(page, step_num: int, step_name: str, talk_point: str, interactive: bool = False, pause: float = 1.0):
    """ฟังก์ชันหยุดรอคำสั่งกด Enter หรือเล่นต่ออัตโนมัติ พร้อมแสดงบทพูดแนะนำ"""
    if interactive:
        set_hud(page, f"สเต็ปที่ {step_num}/7 [รอสั่ง Next ⏭️]", step_name, "กด [Enter] ใน Terminal เพื่อสั่งให้เบราว์เซอร์คลิกทำขั้นตอนนี้...")
        print("\n" + "━" * 75)
        print(f"⏸️  [ขั้นตอนที่ {step_num}/7] {step_name}")
        print(f"🗣️  บทพูดนำเสนอ: \"{talk_point}\"")
        print(f"👉 กด [Enter] เพื่อสั่งให้เบราว์เซอร์เริ่มทำขั้นตอนนี้ (หรือพิมพ์ q เพื่อหยุด): ", end="", flush=True)
        try:
            cmd = input()
            if cmd.strip().lower() == "q":
                print("🛑 ผู้ใช้ออกจากโปรแกรม")
                sys.exit(0)
        except (KeyboardInterrupt, EOFError):
            print("\n🛑 ผู้ใช้ออกจากโปรแกรม")
            sys.exit(0)
    else:
        time.sleep(pause)


def run_live_demo():
    parser = argparse.ArgumentParser(description="Smart CRM Analytics - Live Browser Demo")
    parser.add_argument("-s", "--step", "--interactive", dest="interactive", action="store_true",
                        help="โหมดสั่ง Next ทีละสเต็ป: หยุดรอให้กด [Enter] ก่อนเริ่มทำแต่ละขั้นตอน")
    parser.add_argument("--port", type=int, default=8501, help="Streamlit port (default: 8501)")
    parser.add_argument("--slow-mo", type=int, default=1100, help="Playwright action delay in ms (default: 1100)")
    parser.add_argument("--pause", type=float, default=1.5, help="Extra pause after major steps in sec (default: 1.5)")
    parser.add_argument("--headless", action="store_true", help="Run without opening browser window (default: False)")
    parser.add_argument("--no-seed", action="store_true", help="Do not re-seed database before starting")
    parser.add_argument("--keep-open", action="store_true", default=True, help="Keep browser open after completion")
    args = parser.parse_args()

    print("\n" + "=" * 75)
    print("🎬  SMART CRM ANALYTICS — REAL UI LIVE DEMO")
    print("    สาธิตกระบวนการจริง 3 เคส 7 ขั้นตอน (DFD 1.0 - 5.0, D1 - D5)")
    if args.interactive:
        print("    🕹️  โหมด: INTERACTIVE STEP-BY-STEP (กด [Enter] เพื่อ Next ทีละขั้น)")
    else:
        print("    ⚡ โหมด: AUTO PLAY (เล่นต่อเนื่องตามความเร็ว Slow-Mo)")
    print("=" * 75)

    # 1. จัดการข้อมูลตั้งต้น
    if not args.no_seed:
        print("\n🌱 [0/7] กำลังตั้งค่าฐานข้อมูลตั้งต้น (Seed Data)...")
        subprocess.run([sys.executable, "db/seed_data.py"], cwd=ROOT, check=True,
                       capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
        print("    ✅ ฐานข้อมูล SQLite สะอาด พร้อมสาธิต 100%")

    # 2. ตรวจสอบการทำงานของ Streamlit Server
    proc = None
    target_port = args.port
    if not is_port_open(target_port):
        print(f"🚀 เซิร์ฟเวอร์ที่พอร์ต {target_port} ยังไม่ทำงาน กำลังเริ่มระบบ Streamlit...")
        target_port = get_free_port()
        proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py",
             "--server.port", str(target_port), "--server.headless", "true",
             "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={**os.environ, "PYTHONUTF8": "1"}
        )
        ready = False
        for _ in range(40):
            if is_port_open(target_port):
                ready = True
                break
            time.sleep(0.5)
        if not ready:
            print("❌ ไม่สามารถเริ่ม Streamlit Server ได้")
            sys.exit(1)
        print(f"    ✅ Streamlit Server ทำงานแล้วบนพอร์ต {target_port}")
    else:
        print(f"🔗 ตรวจพบ Streamlit Server ที่พอร์ต {target_port} พร้อมเชื่อมต่อทันที!")

    base_url = f"http://localhost:{target_port}"

    print(f"\n🖥️  กำลังเปิดเบราว์เซอร์ Chromium ({'Headless' if args.headless else 'Headed Window บนหน้าจอ'})...")
    print(f"    ความเร็ว: Slow-Mo {args.slow_mo}ms | หน่วงเวลาแต่ละขั้น: {args.pause}s\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=args.headless,
            slow_mo=args.slow_mo,
            args=["--start-maximized"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            no_viewport=True if not args.headless else False
        )
        page = context.new_page()

        try:
            # -------------------------------------------------------------
            # STEP 0: เข้าหน้าแรก (Login Screen)
            # -------------------------------------------------------------
            print("\n▶️ [เริ่มต้น] เข้าสู่หน้าหลักระบบ Smart CRM Analytics...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1000)
            set_hud(page, "ภาพรวมระบบ", "Smart CRM Analytics v1.2.1", "ระบบบริหารจัดการลูกค้าอัจฉริยะ (3NF SQLite + AI Data Science)")

            # -------------------------------------------------------------
            # STEP 1: (D1) พอร์ทัลลูกค้า — ผู้สนใจลงทะเบียนใหม่
            # -------------------------------------------------------------
            wait_next_step(
                page, 1,
                "Portal: ผู้สนใจลงทะเบียนขอข้อมูล (DFD 1.2 -> Data Store D1: LEAD)",
                "เราเริ่มต้นจากมุมมองของบุคคลภายนอก (Lead) ส่งข้อมูลติดต่อผ่าน Customer Portal ข้อมูลไหลเข้าสู่ D1: LEAD ทันทีครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 1/7] (D1) Portal: ผู้สนใจภายนอกลงทะเบียนความสนใจ (DFD 1.2)...")
            login(page, base_url, "guest", args.pause)
            set_hud(page, "ขั้นตอนที่ 1/7", "External Entity: Portal ผู้สนใจ", "ลงทะเบียนขอข้อมูล (Process 1.2 -> Data Store D1: LEAD)")

            click_tab(page, "ลงทะเบียนความสนใจ", args.pause)
            page.get_by_label("ชื่อ-นามสกุล *").fill("คุณสมชาย หมายมั่น")
            page.get_by_label("เบอร์โทรศัพท์ *").fill("081-999-8888")
            email_field = page.get_by_label("อีเมล")
            if email_field.is_visible():
                email_field.fill("somchai@siamgroup.co.th")

            submit_reg = page.get_by_role("button", name=re.compile("ส่งข้อมูลการติดต่อ")).first
            if submit_reg.is_visible():
                submit_reg.click()
                page.wait_for_timeout(1500)
            print("    ✅ บันทึก Lead ใหม่: 'คุณสมชาย หมายมั่น' เข้าตาราง D1: LEAD สำเร็จ")

            # -------------------------------------------------------------
            # STEP 2: (D1, D2) การตลาด — ตรวจรับ Lead และส่งโปรโมชัน
            # -------------------------------------------------------------
            wait_next_step(
                page, 2,
                "Marketing: ตรวจรับ Lead & เชื่อมโยงแคมเปญ ROI สูงสุด CMP003 (DFD 1.1, 1.3 -> D2)",
                "ฝ่ายการตลาดเชื่อมโยงแคมเปญ Digital Ads Q3 ที่มี ROI สูงสุด 103% เพื่อส่งมอบโปรโมชันส่วนลด 10% ให้ผู้สนใจครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 2/7] (D1, D2) Marketing: เชื่อมโยงแคมเปญ ROI สูงสุด (CMP003) & ส่งโปรโมชัน...")
            login(page, base_url, "marketing1", args.pause)
            set_hud(page, "ขั้นตอนที่ 2/7", "Marketing: ฝ่ายการตลาด", "ตรวจรับ Lead เชื่อมโยงแคมเปญ CMP003 (Process 1.1, 1.3 -> D2)")

            click_menu(page, "งานการตลาด", args.pause)
            click_tab(page, "แคมเปญทั้งหมด", args.pause)
            print("    ✅ แคมเปญ Digital Ads Q3 (CMP003 ส่วนลด 10%, ROI 103%) พร้อมใช้งาน")

            # -------------------------------------------------------------
            # STEP 3: (D2, D3) ฝ่ายขาย — AI Lead Scoring & ออกใบเสนอราคา
            # -------------------------------------------------------------
            wait_next_step(
                page, 3,
                "Sales: AI Lead Scoring (Hot Lead LD0264 85%) & ออกใบเสนอราคา (DFD 2.1, 2.3 -> D3)",
                "ฝ่ายขายใช้ Random Forest คัดกรองคิวงาน พบว่าคุณวิชัย LD0264 มีคะแนน 85% จึงโทรติดต่อและออกใบเสนอราคาพร้อมส่วนลดอัตโนมัติครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 3/7] (D2, D3) Sales: AI Lead Scoring (Hot Lead LD0264) & ออกใบเสนอราคา...")
            login(page, base_url, "sale1", args.pause)
            set_hud(page, "ขั้นตอนที่ 3/7", "Sales: คิวงาน AI & ออกใบเสนอราคา", "AI ทำนายโอกาสปิดการขาย 85% (Hot Lead) -> ออกใบเสนอราคา (Process 2.3 -> D3)")

            click_menu(page, "ติดตามการขาย", args.pause)
            click_tab(page, "คิวงานจัดลำดับด้วย AI", args.pause)

            # บันทึกกิจกรรมการโทร
            click_tab(page, "ค้นหา & บันทึกกิจกรรม", args.pause)
            act_note = page.get_by_label("บันทึกผลการติดต่อ")
            if act_note.is_visible():
                act_note.fill("โทรติดต่อเสนอโซลูชัน Cloud ERP ลูกค้าพอใจมาก ตกลงรับใบเสนอราคาพร้อมส่วนลดแคมเปญ")
            save_act = page.get_by_role("button", name=re.compile("บันทึก")).first
            if save_act.is_visible():
                save_act.click()
                page.wait_for_timeout(1200)

            # ออกใบเสนอราคา
            click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
            click_tab(page, "ออกใบเสนอราคา", args.pause)

            # เลือกสินค้าใน Multiselect
            ms = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค้า").first
            if not ms.is_visible():
                ms = page.locator("div[data-testid='stMultiSelect']").first
            if ms.is_visible():
                ms.click()
                page.wait_for_timeout(600)
                options = page.locator("li[role='option']")
                if options.count() >= 2:
                    options.nth(0).click()
                    page.wait_for_timeout(500)
                    options.nth(1).click()
                    page.wait_for_timeout(500)
                elif options.count() >= 1:
                    options.nth(0).click()
                    page.wait_for_timeout(500)
                page.keyboard.press("Escape")
                page.wait_for_timeout(800)

            issue_btn = page.get_by_role("button", name=re.compile("ออกใบเสนอราคา")).first
            if issue_btn.is_visible():
                issue_btn.click()
                page.wait_for_timeout(2000)
            print("    ✅ ออกใบเสนอราคาสำเร็จ (บันทึกข้อมูลลงตาราง D3: SALE และ SALE_DETAIL)")

            # -------------------------------------------------------------
            # STEP 4: (D3) พอร์ทัลลูกค้า — ยืนยันคำสั่งซื้อ & ดูใบเสนอราคา
            # -------------------------------------------------------------
            wait_next_step(
                page, 4,
                "Portal: ลูกค้ายืนยันคำสั่งซื้อตามใบเสนอราคา (DFD 3.1 -> D3)",
                "ลูกค้าตรวจดูใบเสนอราคาผ่าน Portal และกดยืนยันคำสั่งซื้อแบบ Self-service ส่งสถานะเข้าสู่ Process 3.1 ครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 4/7] (D3) Portal: ลูกค้ายืนยันคำสั่งซื้อตามใบเสนอราคา (DFD 3.1)...")
            login(page, base_url, "guest", args.pause)
            set_hud(page, "ขั้นตอนที่ 4/7", "Portal: ยืนยันคำสั่งซื้อ", "ลูกค้ายืนยันการสั่งซื้อผ่านพอร์ทัล (Process 3.1 -> อัปเดตสถานะใน D3)")

            click_tab(page, "โปรโมชัน & ใบเสนอราคา", args.pause)
            click_tab(page, "ยืนยันคำสั่งซื้อ", args.pause)
            confirm_btn = page.get_by_role("button", name=re.compile("ยืนยันสั่งซื้อ")).first
            if confirm_btn.is_visible():
                confirm_btn.click()
                page.wait_for_timeout(1500)
                print("    ✅ ลูกค้ายืนยันคำสั่งซื้อเรียบร้อย")
            else:
                print("    ℹ️ รายการคำสั่งซื้ออยู่ในสถานะพร้อมตรวจรับ")

            # -------------------------------------------------------------
            # STEP 5: (D3, D4) ฝ่ายขาย — ตรวจเงิน, ออกใบเสร็จ & ยกระดับเป็น CUSTOMER
            # -------------------------------------------------------------
            wait_next_step(
                page, 5,
                "Sales: ตรวจรับเงิน, ออกใบเสร็จ & ยกระดับสู่ CUSTOMER (DFD 3.2, 3.3 -> D4)",
                "ฝ่ายขายตรวจสอบสลิปการโอนเงิน ออกใบเสร็จรับเงิน และระบบยกระดับสถานะจาก Lead เข้าสู่ตาราง D4: CUSTOMER ทันทีครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 5/7] (D3, D4) Sales: ตรวจรับเงิน -> ออกใบเสร็จ -> ยกระดับเป็น CUSTOMER (DFD 3.2 - 3.3)...")
            login(page, base_url, "sale1", args.pause)
            set_hud(page, "ขั้นตอนที่ 5/7", "Sales: ตรวจรับเงิน & ยกระดับเป็น Customer", "ตรวจสลิป ออกใบเสร็จ ยกระดับจาก Lead สู่ D4: CUSTOMER (Process 3.2 - 3.3)")

            click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
            click_tab(page, "รับ & ตรวจคำสั่งซื้อ", args.pause)
            click_tab(page, "ตรวจสอบการชำระเงิน", args.pause)
            click_tab(page, "ออกใบเสร็จ + บันทึกลูกค้า", args.pause)
            print("    ✅ ยกระดับข้อมูลเป็น CUSTOMER และสร้างใบเสร็จรับเงินในระบบเรียบร้อย")

            # -------------------------------------------------------------
            # STEP 6: (D4) บริการลูกค้า — เปิดเคส, แชทแก้ไขปัญหา & ประเมิน 5 ดาว
            # -------------------------------------------------------------
            wait_next_step(
                page, 6,
                "Support: แชทบริการลูกค้า, ปิดเคส & ประเมิน 5 ดาว (DFD 4.1 - 4.3 -> D4)",
                "บริการหลังการขาย เจ้าหน้าที่ประสานงานผ่านแชทสดสองทาง เมื่อปิดเคส ลูกค้าประเมิน 5 ดาว ช่วยฟื้นฟู Health Score ของลูกค้าครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 6/7] (D4) Support & CSAT: เปิดเคสแจ้งปัญหา, แชทสด, ปิดเคส & ประเมิน 5 ดาว (DFD 4.1 - 4.3)...")
            login(page, base_url, "cs1", args.pause)
            set_hud(page, "ขั้นตอนที่ 6/7", "Support & CSAT: บริการหลังการขาย", "จัดการเคสแจ้งปัญหา สนทนาสองทาง ปิดเคส และรับคะแนน 5 ดาว (Process 4.0 -> D4)")

            click_menu(page, "รับแจ้งปัญหา", args.pause)
            click_tab(page, "คิวเคส & สนทนา", args.pause)

            # พิมพ์ตอบในช่องแชทเจ้าหน้าที่
            chat_input = page.get_by_placeholder(re.compile("พิมพ์ข้อความตอบกลับ")).or_(
                page.locator("[data-testid='stChatInputTextArea']")
            ).first
            if chat_input.is_visible():
                chat_input.fill("ทีมวิศวกรได้ดำเนินการตรวจสอบฐานข้อมูลและปรับปรุงคอนฟิกให้เรียบร้อยแล้วครับ ใช้งานได้ปกติทันที")
                chat_input.press("Enter")
                page.wait_for_timeout(1500)

            # ปิดเคส
            upd_btn = page.get_by_role("button", name=re.compile("อัปเดต")).first
            if upd_btn.is_visible():
                upd_btn.click()
                page.wait_for_timeout(1500)

            # สลับไปให้คะแนน 5 ดาวใน Portal
            login(page, base_url, "guest", args.pause)
            click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)
            rate_btn = page.get_by_role("button", name=re.compile("ส่งคะแนน")).first
            if rate_btn.is_visible():
                rate_btn.click()
                page.wait_for_timeout(1200)
            print("    ✅ บันทึกคะแนน CSAT 5 ดาว ⭐⭐⭐⭐⭐ ส่งผลบวกต่อ Health Score ของลูกค้า")

            # -------------------------------------------------------------
            # STEP 7: (D5) ผู้บริหาร — วิเคราะห์ 4 โมเดล Data Science อัจฉริยะ
            # -------------------------------------------------------------
            wait_next_step(
                page, 7,
                "Executive: แดชบอร์ดวิเคราะห์ 4 โมเดล Data Science อัจฉริยะ (DFD 5.0 -> D5)",
                "แดชบอร์ดผู้บริหาร รวบรวมข้อมูลจริงมาประมวลผลด้วย 4 โมเดล Data Science แบบ Real-time เพื่อการตัดสินใจทางธุรกิจที่แม่นยำครับ",
                args.interactive, args.pause
            )
            print("▶️ [ขั้นตอนที่ 7/7] (D5) Executive Analytics: ชมแดชบอร์ด 4 โมเดล Data Science (DFD 5.0)...")
            login(page, base_url, "admin1", args.pause)
            click_menu(page, "แดชบอร์ดวิเคราะห์", args.pause)

            # 7.1 Lead Scoring
            set_hud(page, "ขั้นตอนที่ 7/7 [1/4]", "Data Science: AI Lead Scoring", "ทำนายโอกาสปิดการขายด้วย Random Forest (AUC > 0.80)")
            click_tab(page, "Lead Scoring", args.pause)
            time.sleep(args.pause * 1.5)

            # 7.2 RFM Segmentation
            set_hud(page, "ขั้นตอนที่ 7/7 [2/4]", "Data Science: RFM Segmentation", "จัดกลุ่มลูกค้า Recency, Frequency, Monetary (Champions vs At Risk)")
            click_tab(page, "RFM Segmentation", args.pause)
            time.sleep(args.pause * 1.5)

            # 7.3 Churn & Health
            set_hud(page, "ขั้นตอนที่ 7/7 [3/4]", "Data Science: Customer Health & Churn", "เฝ้าระวังลูกค้าตีจากด้วยดัชนีสุขภาพ 5 มิติ (รวมคะแนนบริการจาก Step 6)")
            click_tab(page, "Customer Health & Churn", args.pause)
            time.sleep(args.pause * 1.5)

            # 7.4 Campaign ROI
            set_hud(page, "ขั้นตอนที่ 7/7 [4/4]", "Data Science: Campaign ROI Analytics", "วิเคราะห์อัตราผลตอบแทนแคมเปญ (CMP003 ROI สูงสุด 103%)")
            click_tab(page, "Campaign ROI", args.pause)
            time.sleep(args.pause * 1.5)

            # 7.5 Sales Summary Report
            set_hud(page, "ขั้นตอนที่ 7/7 [สรุป]", "Process 5.2: รายงานสรุปยอดขาย", "รายงานสรุปยอดขายตามมิติต่างๆ สำหรับผู้บริหาร")
            click_tab(page, "รายงานสรุปยอดขาย", args.pause)
            time.sleep(args.pause * 1.5)

            set_hud(page, "🎉 สำเร็จครบ 100%", "Smart CRM Analytics Live Demo", "สาธิตกระบวนการจริง D1-D5 ครบถ้วน 3 เคสธุรกิจ 7 ขั้นตอน")

            print("\n" + "=" * 70)
            print("🎉  การสาธิตสดเสร็จสิ้นสมบูรณ์ 100% ครบทั้ง 7 ขั้นตอน!")
            print("    1. (D1) Portal: ผู้สนใจลงทะเบียนใหม่")
            print("    2. (D1, D2) Marketing: เชื่อมโยงแคมเปญ CMP003")
            print("    3. (D2, D3) Sales: AI Lead Scoring -> ออกใบเสนอราคา")
            print("    4. (D3) Portal: ลูกค้ายืนยันคำสั่งซื้อ")
            print("    5. (D3, D4) Sales: ตรวจรับเงิน -> ยกระดับเป็น Customer")
            print("    6. (D4) Support: แชทแก้ไขปัญหา -> ปิดเคส -> CSAT 5 ดาว")
            print("    7. (D5) Executive: แดชบอร์ด 4 โมเดล Data Science")
            print("=" * 70)

            if not args.headless and args.keep_open:
                print("\n💡 หน้าต่างเบราว์เซอร์ยังคงเปิดอยู่เพื่อให้คุณหรืออาจารย์ทดลองคลิกดูได้")
                print("   กด [Ctrl+C] หรือกด [Enter] ในเทอร์มินัลนี้เพื่อปิดเบราว์เซอร์...")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    pass

        finally:
            browser.close()
            if proc:
                print("🛑 กำลังปิด Streamlit Server ชั่วคราว...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()


if __name__ == "__main__":
    run_live_demo()
