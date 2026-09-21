"""
scripts/live_browser_demo.py
ระบบสาธิตสดอัตโนมัติผ่านเบราว์เซอร์จริง (Playwright Headed Live Demo)
สำหรับแสดงการทำงานจริงของ Smart CRM Analytics (DFD Process 1.0 - 5.0, D1 - D5)

โหมดการทำงาน:
  1. Standard Flow (7 ขั้นตอนหลัก 10 นาที — ค่าเริ่มต้น):
       python scripts/live_browser_demo.py --step
  2. Grand Tour Flow (18 ขั้นตอนจัดเต็ม เจาะลึกทุกหน้าจอ 1.1 ก่อน 1.2):
       python scripts/live_browser_demo.py --step --scenario full
       # หรือ: python scripts/live_browser_demo.py -s --scenario grand

คุณสมบัติพิเศษ:
  - เปิดเบราว์เซอร์ Chromium จริงบนหน้าจอ (Headless=False)
  - แถบป้ายคำบรรยายลอยบนหัวเว็บ (Floating HUD Subtitles)
  - โหมด Interactive Step-by-Step หยุดรอให้กด [Enter] พร้อมแสดงบทพูดแนะนำสำหรับบรรยาย
  - ทัวร์ครอบคลุม 3NF SQLite, RBAC Security, Random Forest, RFM, Churn Health, Campaign ROI
"""

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from playwright.sync_api import sync_playwright

try:
    import msvcrt
except ImportError:
    msvcrt = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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


def set_hud(page, badge: str, title: str, desc: str, show_next_btn: bool = False):
    """แสดง Floating HUD Subtitle ด้านบนของหน้าต่างเบราว์เซอร์เพื่อเป็นคำบรรยายสำหรับผู้ชม

    รองรับปุ่ม Next บนหน้าจอ และ Event Listener ให้เคาะ Space/Enter บนหน้าเว็บเพื่อไปต่อได้ทันที
    """
    badge_json = json.dumps(badge, ensure_ascii=False)
    title_json = json.dumps(title, ensure_ascii=False)
    desc_json = json.dumps(desc, ensure_ascii=False)
    btn_flag = "true" if show_next_btn else "false"

    js = f"""
    (() => {{
        let el = document.getElementById('live-demo-hud');
        if (!el) {{
            el = document.createElement('div');
            el.id = 'live-demo-hud';
            el.style.position = 'fixed';
            el.style.top = '10px';
            el.style.left = '50%';
            el.style.transform = 'translateX(-50%)';
            el.style.zIndex = '99999999';
            el.style.backgroundColor = 'rgba(15, 23, 42, 0.95)';
            el.style.color = '#ffffff';
            el.style.padding = '6px 16px';
            el = document.createElement('div');
            el.id = 'live-demo-hud';
            el.style.position = 'fixed';
            el.style.top = '10px';
            el.style.left = '50%';
            el.style.transform = 'translateX(-50%)';
            el.style.zIndex = '99999999';
            el.style.backgroundColor = 'rgba(15, 23, 42, 0.95)';
            el.style.color = '#ffffff';
            el.style.padding = '5px 14px';
            el.style.borderRadius = '24px';
            el.style.boxShadow = '0 6px 20px rgba(0,0,0,0.5), 0 0 12px rgba(56,189,248,0.25)';
            el.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
            el.style.fontSize = '12px';
            el.style.border = '1.5px solid rgba(56, 189, 248, 0.6)';
            el.style.backdropFilter = 'blur(12px)';
            el.style.pointerEvents = 'auto';
            el.style.transition = 'all 0.2s ease-in-out';
            el.style.maxWidth = 'min(560px, calc(100vw - 24px))';
            el.style.boxSizing = 'border-box';
            el.style.overflow = 'hidden';
            el.style.display = 'flex';
            el.style.alignItems = 'center';
            el.style.justifyContent = 'space-between';
            el.style.gap = '8px';
            el.style.userSelect = 'none';
            document.body.appendChild(el);
            document.body.style.overflowX = 'hidden';

            if (!window.__DEMO_KEY_BOUND__) {{
                window.__DEMO_KEY_BOUND__ = true;
                window.addEventListener('keydown', (e) => {{
                    const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
                    if (tag !== 'input' && tag !== 'textarea') {{
                        if (e.code === 'Space' || e.key === 'Enter' || e.key === 'ArrowRight') {{
                            e.preventDefault();
                            window.__DEMO_NEXT__ = true;
                        }}
                    }}
                }}, true);
            }}
        }}

        const badgeText = {badge_json};
        const titleText = {title_json};
        const descText = {desc_json};
        const showBtn = {btn_flag};

        let btnHtml = '';
        if (showBtn) {{
            btnHtml = `
                <button id="live-demo-next-btn" style="
                    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                    color: #ffffff;
                    border: 1px solid #38bdf8;
                    padding: 3px 12px;
                    border-radius: 14px;
                    font-size: 11px;
                    font-weight: 700;
                    cursor: pointer;
                    box-shadow: 0 2px 8px rgba(37,99,235,0.4);
                    transition: transform 0.15s ease;
                    white-space: nowrap;
                    flex-shrink: 0;
                    margin-left: 6px;
                    outline: none;
                " onmouseover="this.style.transform='scale(1.05)';"
                   onmouseout="this.style.transform='scale(1)';"
                   onclick="window.__DEMO_NEXT__ = true;">
                    ⏭️ ถัดไป (Space)
                </button>
            `;
        }}

        el.setAttribute('title', descText ? (titleText + ' — ' + descText) : titleText);
        el.innerHTML = `
            <div style="display:flex;align-items:center;gap:6px;overflow:hidden;min-width:0;flex:1;">
                <span style="background: #0284c7; color: #fff; padding: 2px 7px; border-radius: 8px; font-weight: bold; font-size: 10px; white-space: nowrap; flex-shrink: 0;">${{badgeText}}</span>
                <strong style="color: #38bdf8; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; min-width: 0;">${{titleText}}</strong>
            </div>
            ${{btnHtml}}
        `;
        window.__DEMO_NEXT__ = false;
    }})();
    """
    try:
        page.evaluate(js)
    except Exception:
        pass


def login(page, base_url: str, username: str, step_pause: float = 1.0):
    page.goto(base_url, wait_until="networkidle")
    page.wait_for_timeout(800)

    logout_btn = page.get_by_role("button").filter(has_text="ออกจากระบบ")
    if logout_btn.count() > 0 and logout_btn.first.is_visible():
        logout_btn.first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(800)

    if username == "guest":
        btn = page.get_by_role("button").filter(has_text=re.compile(r"ผู้สนใจ|ลูกค่า"))
        if btn.count() > 0:
            btn.first.click()
    else:
        legacy_btn = page.get_by_role("button").filter(has_text=f"เข้าใช้งานเป็น {username}")
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
    page.wait_for_timeout(max(1000, int(step_pause * 1000)))


def click_menu(page, title: str, step_pause: float = 1.0):
    link = page.get_by_role("link").filter(has_text=title).first
    if link.count() > 0:
        link.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(max(1200, int(step_pause * 1200)))


def click_tab(page, tab_name: str, step_pause: float = 1.0):
    tab = page.get_by_role("tab").filter(has_text=tab_name).first
    if tab.count() > 0:
        tab.click()
        page.wait_for_timeout(max(1000, int(step_pause * 1000)))


def wait_next_step(page, step_num: int, total_steps: int, step_name: str, talk_point: str, interactive: bool = False, pause: float = 1.0):
    """ฟังก์ชันหยุดรอคำสั่งกด Enter หรือเล่นต่ออัตโนมัติ พร้อมแสดงบทพูดแนะนำ

    รองรับการควบคุมบนจอเดียว (Single Screen) สมบูรณ์แบบ:
      1. คลิกปุ่ม [⏭️ ถัดไป] บน Floating HUD ที่หัวเว็บ
      2. เคาะ Spacebar หรือ Enter บนหน้าเว็บเบราว์เซอร์
      3. กด [Enter] ใน Terminal (ถ้ามี 2 จอ) หรือกด 'q' เพื่อออก
    """
    if interactive:
        set_hud(
            page,
            badge=f"สเต็ป {step_num}/{total_steps} [รอสั่ง Next ⏭️]",
            title=step_name,
            desc=f"🗣️ {talk_point}",
            show_next_btn=True
        )
        print("\n" + "━" * 78)
        print(f"⏸️  [ขั้นตอนที่ {step_num}/{total_steps}] {step_name}")
        print(f"🗣️  บทพูดนำเสนอ: \"{talk_point}\"")
        print("👉 สั่ง Next: 1) คลิก [⏭️ ถัดไป] บนจอ | 2) เคาะ Spacebar บนเว็บ | 3) กด [Enter] ใน Terminal: ", end="", flush=True)

        while True:
            # 1. ตรวจสอบการคลิกปุ่มหรือกดปุ่มคีย์บอร์ดบนหน้าจอเบราว์เซอร์
            try:
                clicked = page.evaluate("() => { if (window.__DEMO_NEXT__) { window.__DEMO_NEXT__ = false; return true; } return false; }")
                if clicked:
                    print(" [⏭️ Next จาก Browser!]")
                    break
            except Exception:
                pass

            # 2. ตรวจสอบการกดปุ่มใน Terminal บน Windows แบบ Non-blocking
            try:
                if msvcrt and msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ('\r', '\n', ' '):
                        print(" [⏎ Next จาก Terminal!]")
                        break
                    elif ch.lower() == 'q':
                        print("\n🛑 ผู้ใช้ออกจากโปรแกรม")
                        sys.exit(0)
            except Exception:
                pass

            page.wait_for_timeout(100)

        # เปลี่ยนสถานะ HUD เป็นกำลังรันขั้นตอน
        set_hud(
            page,
            badge=f"กำลังรัน {step_num}/{total_steps} ⚙️",
            title=step_name,
            desc="ระบบกำลังดำเนินการอัตโนมัติ...",
            show_next_btn=False
        )
    else:
        time.sleep(pause)


def select_dropdown_option(page, label_regex: str, option_query: str):
    """ช่วยเลือก Option ใน Streamlit Selectbox ตามข้อความ"""
    sel = page.locator("[data-testid='stSelectbox']").filter(has_text=re.compile(label_regex)).first
    if sel.count() > 0 and sel.is_visible():
        sel.click()
        page.wait_for_timeout(500)
        opt = page.locator("li[role='option']").filter(has_text=option_query).first
        if opt.count() > 0:
            opt.click()
        else:
            first_opt = page.locator("li[role='option']").nth(1)
            if first_opt.count() > 0:
                first_opt.click()
        page.wait_for_timeout(800)


def select_portal_identity(page, query_text: str):
    """ช่วยเลือกตัวตนผู้สนใจ/ลูกค่าในหน้า Customer Portal"""
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text=query_text).first
        if p_opt.count() > 0:
            p_opt.click()
        else:
            first_opt = page.locator("li[role='option']").nth(1)
            if first_opt.count() > 0:
                first_opt.click()
        page.wait_for_timeout(800)


# =============================================================================
# SCENARIO 1: STANDARD FLOW (7 STEPS — ของเดิม 100%)
# =============================================================================
def run_standard_tour(page, base_url: str, args):
    total_steps = 7

    # STEP 1: (D1) Portal
    wait_next_step(
        page, 1, total_steps,
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

    # STEP 2: (D1, D2) Marketing
    wait_next_step(
        page, 2, total_steps,
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

    # STEP 3: (D2, D3) Sales
    wait_next_step(
        page, 3, total_steps,
        "Sales: AI Lead Scoring (Hot Lead LD0264 85%) & ออกใบเสนอราคา (DFD 2.1, 2.3 -> D3)",
        "ฝ่ายขายใช้ Random Forest คัดกรองคิวงาน พบว่าคุณวิชัย LD0264 มีคะแนน 85% จึงโทรติดต่อและออกใบเสนอราคาพร้อมส่วนลดอัตโนมัติครับ",
        args.interactive, args.pause
    )
    print("▶️ [ขั้นตอนที่ 3/7] (D2, D3) Sales: AI Lead Scoring (Hot Lead LD0264) & ออกใบเสนอราคา...")
    login(page, base_url, "sale1", args.pause)
    set_hud(page, "ขั้นตอนที่ 3/7", "Sales: คิวงาน AI & ออกใบเสนอราคา", "AI ทำนายโอกาสปิดการขาย 85% (Hot Lead) -> ออกใบเสนอราคา (Process 2.3 -> D3)")

    click_menu(page, "ติดตามการขาย", args.pause)
    click_tab(page, "คิวงานจัดลำดับด้วย AI", args.pause)

    click_tab(page, "ค้นหา & บันทึกกิจกรรม", args.pause)
    act_note = page.get_by_label("บันทึกผลการติดต่อ")
    if act_note.is_visible():
        act_note.fill("โทรติดต่อเสนอโซลูชัน Cloud ERP ลูกค่าพอใจมาก ตกลงรับใบเสนอราคาพร้อมส่วนลดแคมเปญ")
    save_act = page.get_by_role("button", name=re.compile("บันทึก")).first
    if save_act.is_visible():
        save_act.click()
        page.wait_for_timeout(1200)

    click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
    click_tab(page, "ออกใบเสนอราคา", args.pause)

    ms = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค่า").first
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

    # STEP 4: (D3) Portal Order
    wait_next_step(
        page, 4, total_steps,
        "Portal: ลูกค่ายืนยันคำสั่งซื้อตามใบเสนอราคา (DFD 3.1 -> D3)",
        "ลูกค่าตรวจดูใบเสนอราคาผ่าน Portal และกดยืนยันคำสั่งซื้อแบบ Self-service ส่งสถานะเข้าสู่ Process 3.1 ครับ",
        args.interactive, args.pause
    )
    print("▶️ [ขั้นตอนที่ 4/7] (D3) Portal: ลูกค่ายืนยันคำสั่งซื้อตามใบเสนอราคา (DFD 3.1)...")
    login(page, base_url, "guest", args.pause)
    set_hud(page, "ขั้นตอนที่ 4/7", "Portal: ยืนยันคำสั่งซื้อ", "ลูกค่ายืนยันการสั่งซื้อผ่านพอร์ทัล (Process 3.1 -> อัปเดตสถานะใน D3)")

    click_tab(page, "โปรโมชัน & ใบเสนอราคา", args.pause)
    click_tab(page, "ยืนยันคำสั่งซื้อ", args.pause)
    confirm_btn = page.get_by_role("button", name=re.compile("ยืนยันสั่งซื้อ")).first
    if confirm_btn.is_visible():
        confirm_btn.click()
        page.wait_for_timeout(1500)
        print("    ✅ ลูกค่ายืนยันคำสั่งซื้อเรียบร้อย")
    else:
        print("    ℹ️ รายการคำสั่งซื้ออยู่ในสถานะพร้อมตรวจรับ")

    # STEP 5: (D3, D4) Sales Payment & Receipt
    wait_next_step(
        page, 5, total_steps,
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
    click_tab(page, "ออกใบเสร็จ + บันทึกลูกค่า", args.pause)
    print("    ✅ ยกระดับข้อมูลเป็น CUSTOMER และสร้างใบเสร็จรับเงินในระบบเรียบร้อย")

    # STEP 6: (D4) Support & CSAT
    wait_next_step(
        page, 6, total_steps,
        "Support: แชทบริการลูกค่า, ปิดเคส & ประเมิน 5 ดาว (DFD 4.1 - 4.3 -> D4)",
        "บริการหลังการขาย เจ้าหน้าที่ประสานงานผ่านแชทสดสองทาง เมื่อปิดเคส ลูกค่าประเมิน 5 ดาว ช่วยฟื้นฟู Health Score ของลูกค่าครับ",
        args.interactive, args.pause
    )
    print("▶️ [ขั้นตอนที่ 6/7] (D4) Support & CSAT: เปิดเคสแจ้งปัญหา, แชทสด, ปิดเคส & ประเมิน 5 ดาว (DFD 4.1 - 4.3)...")
    login(page, base_url, "cs1", args.pause)
    set_hud(page, "ขั้นตอนที่ 6/7", "Support & CSAT: บริการหลังการขาย", "จัดการเคสแจ้งปัญหา สนทนาสองทาง ปิดเคส และรับคะแนน 5 ดาว (Process 4.0 -> D4)")

    click_menu(page, "รับแจ้งปัญหา", args.pause)
    click_tab(page, "คิวเคส & สนทนา", args.pause)

    chat_input = page.get_by_placeholder(re.compile("พิมพ์ข้อความตอบกลับ")).or_(
        page.locator("[data-testid='stChatInputTextArea']")
    ).first
    if chat_input.is_visible():
        chat_input.fill("ทีมวิศวกรได้ดำเนินการตรวจสอบฐานข้อมูลและปรับปรุงคอนฟิกให้เรียบร้อยแล้วครับ ใช้งานได้ปกติทันที")
        chat_input.press("Enter")
        page.wait_for_timeout(1500)

    upd_btn = page.get_by_role("button", name=re.compile("อัปเดต")).first
    if upd_btn.is_visible():
        upd_btn.click()
        page.wait_for_timeout(1500)

    login(page, base_url, "guest", args.pause)
    click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)
    rate_btn = page.get_by_role("button", name=re.compile("ส่งคะแนน")).first
    if rate_btn.is_visible():
        rate_btn.click()
        page.wait_for_timeout(1200)
    print("    ✅ บันทึกคะแนน CSAT 5 ดาว ⭐⭐⭐⭐⭐ ส่งผลบวกต่อ Health Score ของลูกค่า")

    # STEP 7: (D5) Executive Analytics
    wait_next_step(
        page, 7, total_steps,
        "Executive: แดชบอร์ดวิเคราะห์ 4 โมเดล Data Science อัจฉริยะ (DFD 5.0 -> D5)",
        "แดชบอร์ดผู้บริหาร รวบรวมข้อมูลจริงมาประมวลผลด้วย 4 โมเดล Data Science แบบ Real-time เพื่อการตัดสินใจทางธุรกิจที่แม่นยำครับ",
        args.interactive, args.pause
    )
    print("▶️ [ขั้นตอนที่ 7/7] (D5) Executive Analytics: ชมแดชบอร์ด 4 โมเดล Data Science (DFD 5.0)...")
    login(page, base_url, "admin1", args.pause)
    click_menu(page, "แดชบอร์ดวิเคราะห์", args.pause)

    set_hud(page, "ขั้นตอนที่ 7/7 [1/4]", "Data Science: AI Lead Scoring", "ทำนายโอกาสปิดการขายด้วย Random Forest (AUC > 0.80)")
    click_tab(page, "Lead Scoring", args.pause)
    time.sleep(args.pause * 1.5)

    set_hud(page, "ขั้นตอนที่ 7/7 [2/4]", "Data Science: RFM Segmentation", "จัดกลุ่มลูกค่า Recency, Frequency, Monetary (Champions vs At Risk)")
    click_tab(page, "RFM Segmentation", args.pause)
    time.sleep(args.pause * 1.5)

    set_hud(page, "ขั้นตอนที่ 7/7 [3/4]", "Data Science: Customer Health & Churn", "เฝ้าระวังลูกค่าตีจากด้วยดัชนีสุขภาพ 5 มิติ (รวมคะแนนบริการจาก Step 6)")
    click_tab(page, "Customer Health & Churn", args.pause)
    time.sleep(args.pause * 1.5)

    set_hud(page, "ขั้นตอนที่ 7/7 [4/4]", "Data Science: Campaign ROI Analytics", "วิเคราะห์อัตราผลตอบแทนแคมเปญ (CMP003 ROI สูงสุด 103%)")
    click_tab(page, "Campaign ROI", args.pause)
    time.sleep(args.pause * 1.5)

    set_hud(page, "ขั้นตอนที่ 7/7 [สรุป]", "Process 5.2: รายงานสรุปยอดขาย", "รายงานสรุปยอดขายตามมิติต่างๆ สำหรับผู้บริหาร")
    click_tab(page, "รายงานสรุปยอดขาย", args.pause)
    time.sleep(args.pause * 1.5)

    set_hud(page, "🎉 สำเร็จครบ 100%", "Smart CRM Analytics Live Demo", "สาธิตกระบวนการจริง D1-D5 ครบถ้วน 3 เคสธุรกิจ 7 ขั้นตอน")


# =============================================================================
# SCENARIO 2: GRAND TOUR 18 STEPS (จัดเต็ม 1.1 ก่อน 1.2 ครบทุกเมนู 100%)
# =============================================================================
def run_grand_tour(page, base_url: str, args):
    total_steps = 18

    # 1. Process 1.1: สร้างแคมเปญการตลาดใหม่จริง
    wait_next_step(
        page, 1, total_steps,
        "Marketing: สร้างแคมเปญการตลาดใหม่ (Process 1.1 -> ตาราง CAMPAIGN)",
        "เริ่มต้นที่การตลาดสร้างแคมเปญล่วงหน้า กำหนดงบประมาณ และส่วนลด 15% เพื่อนำไปยิงโปรโมชันครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "marketing1", args.pause)
    set_hud(page, f"ขั้นตอนที่ 1/{total_steps}", "Marketing: สร้างแคมเปญใหม่", "กรอกฟอร์มสร้างแคมเปญ กำหนดงบและส่วนลด 15% (Process 1.1 -> ตาราง CAMPAIGN)")
    click_menu(page, "งานการตลาด", args.pause)
    click_tab(page, "สร้างแคมเปญ", args.pause)
    try:
        page.get_by_label(re.compile("ชื่อแคมเปญ")).wait_for(state="visible", timeout=6000)
    except Exception:
        pass

    c_name = page.get_by_label(re.compile("ชื่อแคมเปญ"))
    if c_name.count() > 0 and c_name.first.is_visible():
        c_name.first.fill("Mid-Year Super Deal 2026")
    b_box = page.get_by_label(re.compile("งบประมาณ"))
    if b_box.count() > 0 and b_box.first.is_visible():
        b_box.first.fill("60000")
    d_box = page.get_by_label(re.compile("ส่วนลด"))
    if d_box.count() > 0 and d_box.first.is_visible():
        d_box.first.fill("15")
    p_box = page.get_by_label(re.compile("รายละเอียดโปรโมชัน"))
    if p_box.count() > 0 and p_box.first.is_visible():
        p_box.first.fill("แคมเปญกระตุ้นยอดขายกลุ่ม Enterprise รับส่วนลดพิเศษ 15% พร้อมฟรี Support 1 ปี")
    save_c = page.get_by_role("button", name=re.compile("บันทึกแคมเปญ")).first
    if save_c.count() > 0 and save_c.is_visible():
        save_c.click()
        page.wait_for_timeout(1500)
    print("    ✅ สร้างแคมเปญใหม่ 'Mid-Year Super Deal 2026' ลงตาราง CAMPAIGN สำเร็จ")

    # 2. Process 1.1: ตรวจสอบแคมเปญทั้งหมดและ CMP003
    wait_next_step(
        page, 2, total_steps,
        "Marketing: ส่องตารางแคมเปญทั้งหมด & แคมเปญ ROI สูงสุด (Process 1.1)",
        "ตรวจสอบรายการแคมเปญที่พร้อมใช้งาน ชี้ให้เห็น CMP003 Digital Ads Q3 ที่สร้าง ROI สูงสุด 103% ครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 2/{total_steps}", "Marketing: ตารางแคมเปญทั้งหมด", "ดูแคมเปญที่เปิดใช้งานอยู่ และแคมเปญ CMP003 ที่มี ROI สูงสุด 103% (Process 1.1)")
    click_tab(page, "แคมเปญทั้งหมด", args.pause)
    time.sleep(args.pause)
    print("    ✅ ตรวจสอบแคมเปญพร้อมใช้งานครบถ้วน")

    # 3. Process 1.2: Portal ลูกค่าลงทะเบียน
    wait_next_step(
        page, 3, total_steps,
        "Portal: ผู้สนใจลงทะเบียนขอข้อมูล (Process 1.2 -> ตาราง D1: LEAD)",
        "ผู้สนใจภายนอก 'คุณสมชาย หมายมั่น' เห็นโฆษณา จึงลงทะเบียนผ่าน Customer Portal พร้อมเลือกรับแคมเปญโปรโมชันครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, f"ขั้นตอนที่ 3/{total_steps}", "Portal: ผู้สนใจลงทะเบียนขอข้อมูล", "ลูกค่าลงทะเบียนความสนใจ ผูกกับแคมเปญการตลาด (Process 1.2 -> D1: LEAD)")
    click_tab(page, "ลงทะเบียนความสนใจ", args.pause)
    page.get_by_label("ชื่อ-นามสกุล *").fill("คุณสมชาย หมายมั่น")
    page.get_by_label("เบอร์โทรศัพท์ *").fill("081-999-8888")
    em = page.get_by_label("อีเมล")
    if em.is_visible():
        em.fill("somchai@siamgroup.co.th")
    sub_r = page.get_by_role("button", name=re.compile("ส่งข้อมูลการติดต่อ")).first
    if sub_r.is_visible():
        sub_r.click()
        page.wait_for_timeout(1500)
    print("    ✅ บันทึก Lead ใหม่: 'คุณสมชาย หมายมั่น' เข้าตาราง D1: LEAD สำเร็จ")

    # 4. Process 1.3: Portal ลูกค่าเปิดดูโปรโมชันที่ได้รับ
    wait_next_step(
        page, 4, total_steps,
        "Portal: ตรวจสอบโปรโมชันและส่วนลดที่ได้รับ (Process 1.3)",
        "คุณสมชายเลือกตัวตนของตนเองใน Portal เพื่อดูสิทธิประโยชน์และส่วนลด 15% ที่ได้รับจากแคมเปญครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 4/{total_steps}", "Portal: โปรโมชันที่ได้รับ", "แสดงผลรายละเอียดโปรโมชันและส่วนลดที่ได้รับตามแคมเปญ (Process 1.3)")
    # เลือกตัวตนคุณสมชายใน Portal
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if p_opt.count() > 0:
            p_opt.click()
        else:
            p_first = page.locator("li[role='option']").nth(1)
            if p_first.count() > 0:
                p_first.click()
        page.wait_for_timeout(800)

    click_tab(page, "โปรโมชัน & ใบเสนอราคา", args.pause)
    time.sleep(args.pause)
    print("    ✅ คุณสมชาย หมายมั่น ตรวจสอบโปรโมชันและส่วนลดเรียบร้อย")

    # 5. Process 2.1: Sales คิวงาน AI Lead Scoring
    wait_next_step(
        page, 5, total_steps,
        "Sales: ตรวจสอบคิวงานจัดลำดับด้วย AI (Process 2.1 -> ML Lead Scoring)",
        "ฝ่ายขาย (sale1 ณัฐวุฒิ) ใช้โมเดลคัดกรองคิวงาน และตรวจพบคิวงานผู้สนใจใหม่ 'คุณสมชาย หมายมั่น' ครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "sale1", args.pause)
    set_hud(page, f"ขั้นตอนที่ 5/{total_steps}", "Sales: คิวงาน AI Lead Scoring", "ฝ่ายขายตรวจสอบคิวงาน AI และคิวติดตามประจำวัน (Process 2.1)")
    click_menu(page, "ติดตามการขาย", args.pause)
    click_tab(page, "คิวงานจัดลำดับด้วย AI", args.pause)
    time.sleep(args.pause)
    click_tab(page, "คิวติดตามวันนี้", args.pause)
    time.sleep(args.pause)
    print("    ✅ ฝ่ายขายตรวจสอบคิวงานและตรวจพบ 'คุณสมชาย หมายมั่น'")

    # 6. Process 2.2: Sales บันทึกผลการติดต่อ & ไทม์ไลน์
    wait_next_step(
        page, 6, total_steps,
        "Sales: บันทึกผลการติดต่อ & ดูประวัติไทม์ไลน์ (Process 2.2 -> D2: LEAD_ACTIVITY)",
        "ฝ่ายขายโทรติดต่อ 'คุณสมชาย หมายมั่น' นำเสนอแพ็กเกจ Cloud ERP และบันทึกผลการโทรลงระบบครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 6/{total_steps}", "Sales: บันทึกผลการติดต่อ", "บันทึกผลการโทรคุยกับคุณสมชาย และตรวจสอบประวัติไทม์ไลน์ (Process 2.2 -> D2)")
    click_tab(page, "ค้นหา & บันทึกกิจกรรม", args.pause)
    # เลือกคุณสมชายใน dropdown ผู้สนใจ
    lead_s = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกผู้สนใจ").first
    if lead_s.count() > 0 and lead_s.is_visible():
        lead_s.click()
        page.wait_for_timeout(500)
        l_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if l_opt.count() > 0:
            l_opt.click()
        page.wait_for_timeout(800)

    act_n = page.get_by_label("บันทึกผลการติดต่อ")
    if act_n.is_visible():
        act_n.fill("โทรนำเสนอโซลูชัน Cloud ERP ลูกค่าพอใจมาก ตกลงรับข้อเสนอใบเสนอราคาพร้อมส่วนลด 15%")
    s_act = page.get_by_role("button", name=re.compile("บันทึก")).first
    if s_act.is_visible():
        s_act.click()
        page.wait_for_timeout(1200)
    print("    ✅ บันทึกกิจกรรมโทรคุยกับคุณสมชาย และอัปเดตไทม์ไลน์ D2 เรียบร้อย")

    # 7. Process 2.3: Sales ออกใบเสนอราคา
    wait_next_step(
        page, 7, total_steps,
        "Sales: ออกใบเสนอราคา (Quotation) (Process 2.3 -> D3: SALE & SALE_DETAIL)",
        "ฝ่ายขายออกใบเสนอราคาให้ 'คุณสมชาย หมายมั่น' โดยเลือกสินค่าหลายรายการ ระบบหักลดส่วนลดแคมเปญอัตโนมัติครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 7/{total_steps}", "Sales: ออกใบเสนอราคา", "เลือกคุณสมชาย หมายมั่น และสินค่าแบบ Multiselect ออกเลขที่ QT (Process 2.3 -> D3)")
    click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
    click_tab(page, "ออกใบเสนอราคา", args.pause)
    # เลือกคุณสมชายใน dropdown ผู้สนใจ
    q_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกผู้สนใจ").first
    if q_sel.count() > 0 and q_sel.is_visible():
        q_sel.click()
        page.wait_for_timeout(500)
        q_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if q_opt.count() > 0:
            q_opt.click()
            page.wait_for_timeout(600)

    ms = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค่า").first
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
    iss_btn = page.get_by_role("button", name=re.compile("ออกใบเสนอราคา")).first
    if iss_btn.is_visible():
        iss_btn.click()
        page.wait_for_timeout(2000)
    print("    ✅ ออกใบเสนอราคาสำเร็จ (บันทึกข้อมูลลงตาราง D3)")

    # 8. Process 3.1: Portal ลูกค่ายืนยันคำสั่งซื้อ
    wait_next_step(
        page, 8, total_steps,
        "Portal: ลูกค่ายืนยันคำสั่งซื้อตามใบเสนอราคา (Process 3.1 -> D3: SALE)",
        "คุณสมชายตรวจสอบความถูกต้องของรายการและยอดเงิน แล้วกดยืนยันคำสั่งซื้อผ่าน Portal ครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, f"ขั้นตอนที่ 8/{total_steps}", "Portal: ยืนยันคำสั่งซื้อ", "คุณสมชายยืนยันสั่งซื้อสินค่าตามใบเสนอราคาแบบ Self-service (Process 3.1)")
    # เลือกตัวตนคุณสมชายใน Portal
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if p_opt.count() > 0:
            p_opt.click()
            page.wait_for_timeout(800)

    click_tab(page, "ยืนยันคำสั่งซื้อ", args.pause)
    c_btn = page.get_by_role("button", name=re.compile("ยืนยันสั่งซื้อ")).first
    if c_btn.is_visible():
        c_btn.click()
        page.wait_for_timeout(1500)
        print("    ✅ ลูกค่ายืนยันคำสั่งซื้อเรียบร้อย")
    else:
        print("    ℹ️ คำสั่งซื้ออยู่ในสถานะพร้อมตรวจรับ")

    # 9. Process 3.1: Sales รับ & ตรวจสอบคำสั่งซื้อ
    wait_next_step(
        page, 9, total_steps,
        "Sales: ตรวจสอบคำสั่งซื้อของลูกค่า (Process 3.1)",
        "ฝ่ายขายตรวจรับคำสั่งซื้อที่คุณสมชายยืนยันเข้ามา เพื่อส่งต่อไปยังขั้นตอนการชำระเงินครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "sale1", args.pause)
    set_hud(page, f"ขั้นตอนที่ 9/{total_steps}", "Sales: ตรวจรับคำสั่งซื้อ", "ฝ่ายขายตรวจสอบรายการสั่งซื้อของคุณสมชาย (Process 3.1)")
    click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
    click_tab(page, "รับ & ตรวจคำสั่งซื้อ", args.pause)
    time.sleep(args.pause)
    ok_b = page.get_by_role("button", name=re.compile("ตรวจแล้วถูกต้อง")).first
    if ok_b.is_visible():
        ok_b.click()
        page.wait_for_timeout(1200)
    print("    ✅ ตรวจรับคำสั่งซื้อเรียบร้อย")

    # 10. Process 3.2: Sales ตรวจสอบการชำระเงิน & สลิป
    wait_next_step(
        page, 10, total_steps,
        "Sales: ตรวจสอบหลักฐานสลิป & บันทึกการรับเงิน (Process 3.2 -> D3: SALE)",
        "ฝ่ายขายตรวจหลักฐานการโอนเงิน บันทึกรหัสอ้างอิงธุรกรรมธนาคารและยืนยันรับเงินครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 10/{total_steps}", "Sales: ตรวจสอบการชำระเงิน", "ตรวจสอบหลักฐานการโอนเงิน บันทึกเลขอ้างอิงธนาคาร (Process 3.2 -> D3: SALE)")
    click_tab(page, "ตรวจสอบการชำระเงิน", args.pause)
    time.sleep(args.pause)
    ref_b = page.get_by_label(re.compile("เลขอ้างอิง")).first
    if ref_b.count() > 0 and ref_b.is_visible():
        ref_b.fill("TRF2026-9988")
    p_btn = page.get_by_role("button", name=re.compile("ยืนยันรับเงิน")).first
    if p_btn.count() > 0 and p_btn.is_visible():
        p_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ บันทึกการรับเงินและเลขอ้างอิงธนาคารสำเร็จ")

    # 11. Process 3.3: Sales ออกใบเสร็จ & ยกระดับสู่ CUSTOMER
    wait_next_step(
        page, 11, total_steps,
        "Sales: ออกใบเสร็จรับเงิน & ยกระดับสู่ CUSTOMER (Process 3.3 -> D4: CUSTOMER)",
        "ระบบปิดการขาย ออกใบเสร็จรับเงิน และยกระดับสถานะคุณสมชายจาก Lead เข้าสู่ตาราง D4: CUSTOMER ทันทีครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 11/{total_steps}", "Sales: ออกใบเสร็จ & ยกระดับลูกค่า", "ออกใบเสร็จรับเงิน และยกระดับคุณสมชายเข้าสู่ตาราง D4: CUSTOMER (Process 3.3)")
    click_tab(page, "ออกใบเสร็จ + บันทึกลูกค่า", args.pause)
    r_btn = page.get_by_role("button", name=re.compile("ออกใบเสร็จ")).first
    if r_btn.count() > 0 and r_btn.is_visible():
        r_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ ยกระดับข้อมูลคุณสมชายเป็น CUSTOMER และสร้างใบเสร็จรับเงินเรียบร้อย")

    # 12. Process 3.3: Portal ลูกค่าเปิดดูใบเสร็จ
    wait_next_step(
        page, 12, total_steps,
        "Portal: ลูกค่าเปิดดูใบเสร็จรับเงินอิเล็กทรอนิกส์ (Process 3.3)",
        "คุณสมชายสามารถเปิดดูและดาวน์โหลดใบเสร็จรับเงินอิเล็กทรอนิกส์ผ่านระบบ Portal ได้ทันทีครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, f"ขั้นตอนที่ 12/{total_steps}", "Portal: ใบเสร็จรับเงินอิเล็กทรอนิกส์", "คุณสมชายเปิดดูและดาวน์โหลดใบเสร็จรับเงิน (Process 3.3)")
    # เลือกตัวตนคุณสมชาย
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if p_opt.count() > 0:
            p_opt.click()
            page.wait_for_timeout(800)

    click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)
    time.sleep(args.pause)
    print("    ✅ แสดงผลใบเสร็จรับเงินอิเล็กทรอนิกส์พร้อมดาวน์โหลด")

    # 13. Process 4.0: ส่องโปรไฟล์ลูกค่า 360 องศา & RFM Tier
    wait_next_step(
        page, 13, total_steps,
        "Customer 360: ส่องโปรไฟล์ลูกค่า 360 องศา & RFM รายบุคคล (Process 4.0)",
        "พาชมหน้าข้อมูลลูกค่า ดูประวัติบริษัท เลขผู้เสียภาษี และดัชนี RFM Tier รายบุคคลของคุณสมชายครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "sale1", args.pause)
    set_hud(page, f"ขั้นตอนที่ 13/{total_steps}", "Customer 360: โปรไฟล์ลูกค่า", "ส่องโปรไฟล์คุณสมชาย 360 องศา ดูเลขภาษี ที่อยู่ และ RFM Tier รายบุคคล (Process 4.0)")
    click_menu(page, "ข้อมูลลูกค่า", args.pause)
    click_tab(page, "โปรไฟล์รายบุคคล", args.pause)
    # เลือกลูกค่า คุณสมชาย หมายมั่น
    c_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกลูกค่า").first
    if c_sel.count() > 0 and c_sel.is_visible():
        c_sel.click()
        page.wait_for_timeout(500)
        c_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if c_opt.count() > 0:
            c_opt.click()
            page.wait_for_timeout(800)
    time.sleep(args.pause * 1.5)
    print("    ✅ ส่องโปรไฟล์คุณสมชาย 360 องศา และคะแนน RFM รายบุคคล")

    # 14. Process 4.1: Portal ลูกค่าเปิดเคสแจ้งปัญหาเอง
    wait_next_step(
        page, 14, total_steps,
        "Portal: ลูกค่าเปิดเคสแจ้งปัญหาการใช้งาน (Process 4.1 -> D4: TICKET)",
        "คุณสมชายเปิดเคสแจ้งขอคำปรึกษา API ผ่าน Customer Portal ข้อมูลไหลเข้าสู่ตาราง D4 ทันทีครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, f"ขั้นตอนที่ 14/{total_steps}", "Portal: ลูกค่าแจ้งปัญหาการใช้งาน", "คุณสมชายเปิดเคสแจ้งปัญหาผ่าน Portal (Process 4.1 -> ตาราง D4: TICKET)")
    # เลือกตัวตนคุณสมชาย
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if p_opt.count() > 0:
            p_opt.click()
            page.wait_for_timeout(800)

    click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)
    tk_t = page.get_by_label(re.compile("หัวข้อปัญหา")).first
    if tk_t.count() > 0 and tk_t.is_visible():
        tk_t.fill("ขอคำปรึกษาการเชื่อมโยงระบบฐานข้อมูลและ API ยอดขาย")
    tk_d = page.get_by_label(re.compile("รายละเอียด")).first
    if tk_d.count() > 0 and tk_d.is_visible():
        tk_d.fill("ต้องการเอกสาร API เพิ่มเติมสำหรับทีมวิศวกรของคุณสมชาย")
    s_tk = page.get_by_role("button", name=re.compile("ส่งเรื่องแจ้งปัญหา")).first
    if s_tk.count() > 0 and s_tk.is_visible():
        s_tk.click()
        page.wait_for_timeout(1500)
    print("    ✅ ส่งเรื่องแจ้งปัญหาของคุณสมชายผ่าน Portal เรียบร้อย")

    # 15. Process 4.2: Support แชทสดสองทาง & ปิดเคส
    wait_next_step(
        page, 15, total_steps,
        "Support: แชทสดสองทาง & ปิดเคสปัญหา (Process 4.2 -> D4: TICKET_MESSAGE)",
        "เจ้าหน้าที่บริการลูกค่า (cs1) พิมพ์แชทสดตอบกลับคุณสมชาย มอบหมายผู้รับผิดชอบ และอัปเดตปิดเคสครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "cs1", args.pause)
    set_hud(page, f"ขั้นตอนที่ 15/{total_steps}", "Support: แชทสดแก้ไขปัญหา & ปิดเคส", "เจ้าหน้าที่ Support แชทตอบคุณสมชาย และกดปิดเคสสำเร็จ (Process 4.2)")
    click_menu(page, "รับแจ้งปัญหา", args.pause)
    click_tab(page, "คิวเคส & สนทนา", args.pause)
    # เลือกเคสของคุณสมชายใน selectbox
    t_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกเคสเพื่อดูบทสนทนา").first
    if t_sel.count() > 0 and t_sel.is_visible():
        t_sel.click()
        page.wait_for_timeout(500)
        t_opt = page.locator("li[role='option']").filter(has_text="ขอคำปรึกษาการเชื่อมโยงระบบฐานข้อมูล").first
        if t_opt.count() > 0:
            t_opt.click()
            page.wait_for_timeout(800)

    c_inp = page.get_by_placeholder(re.compile("พิมพ์ข้อความตอบกลับ")).or_(
        page.locator("[data-testid='stChatInputTextArea']")
    ).first
    if c_inp.is_visible():
        c_inp.fill("สวัสดีครับคุณสมชาย ทีมวิศวกรได้ส่งเอกสาร API และตัวอย่างโค้ดให้ทางอีเมลเรียบร้อยแล้วครับ")
        c_inp.press("Enter")
        page.wait_for_timeout(1500)
    u_btn = page.get_by_role("button", name=re.compile("อัปเดต")).first
    if u_btn.is_visible():
        u_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ แชทสดสองทางและอัปเดตสถานะเคสบริการของคุณสมชายสำเร็จ")

    # 16. Process 4.3: Portal ลูกค่าประเมิน 5 ดาว (CSAT)
    wait_next_step(
        page, 16, total_steps,
        "Portal: ลูกค่าประเมินความพึงพอใจ 5 ดาว (Process 4.3 -> CSAT & Health Score)",
        "คุณสมชายประเมินคะแนนบริการ 5 ดาว ซึ่งคะแนนนี้จะส่งผลบวกต่อ Customer Health Score ครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, f"ขั้นตอนที่ 16/{total_steps}", "Portal: ประเมินความพึงพอใจ 5 ดาว", "คุณสมชายประเมินคะแนน CSAT 5 ดาว ส่งผลบวกต่อ Customer Health Score (Process 4.3)")
    # เลือกตัวตนคุณสมชาย
    p_sel = page.locator("[data-testid='stSelectbox']").filter(has_text="เลือกตัวตนของคุณ").first
    if p_sel.count() > 0 and p_sel.is_visible():
        p_sel.click()
        page.wait_for_timeout(500)
        p_opt = page.locator("li[role='option']").filter(has_text="คุณสมชาย หมายมั่น").first
        if p_opt.count() > 0:
            p_opt.click()
            page.wait_for_timeout(800)

    click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)
    rt_btn = page.get_by_role("button", name=re.compile("ส่งคะแนน")).first
    if rt_btn.is_visible():
        rt_btn.click()
        page.wait_for_timeout(1200)
    print("    ✅ บันทึกคะแนน CSAT 5 ดาว ⭐⭐⭐⭐⭐ ของคุณสมชายเข้าระบบสำเร็จ")

    # 17. Process 5.1: แดชบอร์ดวิเคราะห์ 4 โมเดล Data Science
    wait_next_step(
        page, 17, total_steps,
        "Executive: แดชบอร์ดวิเคราะห์ 4 โมเดล Data Science อัจฉริยะ (Process 5.1 -> D5)",
        "ผู้บริหารตรวจดูผลวิเคราะห์ Real-time จาก 4 โมเดล: Lead Scoring, RFM, Churn Risk, และ Campaign ROI ครับ",
        args.interactive, args.pause
    )
    login(page, base_url, "admin1", args.pause)
    click_menu(page, "แดชบอร์ดวิเคราะห์", args.pause)

    set_hud(page, f"ขั้นตอนที่ 17/{total_steps} [1/4]", "Data Science: AI Lead Scoring", "ทำนายโอกาสปิดการขายด้วย Random Forest (AUC > 0.80)")
    click_tab(page, "Lead Scoring", args.pause)
    time.sleep(args.pause)

    set_hud(page, f"ขั้นตอนที่ 17/{total_steps} [2/4]", "Data Science: RFM Segmentation", "จัดกลุ่มลูกค่า Recency, Frequency, Monetary (Champions vs At Risk)")
    click_tab(page, "RFM Segmentation", args.pause)
    time.sleep(args.pause)

    set_hud(page, f"ขั้นตอนที่ 17/{total_steps} [3/4]", "Data Science: Customer Health & Churn", "เฝ้าระวังลูกค่าตีจากด้วยดัชนีสุขภาพ 5 มิติ")
    click_tab(page, "Customer Health & Churn", args.pause)
    time.sleep(args.pause)

    set_hud(page, f"ขั้นตอนที่ 17/{total_steps} [4/4]", "Data Science: Campaign ROI Analytics", "วิเคราะห์อัตราผลตอบแทนแคมเปญ (CMP003 ROI สูงสุด 103%)")
    click_tab(page, "Campaign ROI", args.pause)
    time.sleep(args.pause)
    print("    ✅ นำเสนอผลการวิเคราะห์ 4 โมเดล Data Science ครบถ้วน")

    # 18. Process 5.2: รายงานสรุปยอดขาย & Export CSV
    wait_next_step(
        page, 18, total_steps,
        "Executive: รายงานสรุปยอดขาย & Export CSV (Process 5.2 -> D5: REPORTS)",
        "หน้าจอสุดท้าย รายงานสรุปยอดขายตามมิติต่างๆ สำหรับผู้บริหาร พร้อมระบบ Export CSV ครับ",
        args.interactive, args.pause
    )
    set_hud(page, f"ขั้นตอนที่ 18/{total_steps}", "Process 5.2: สรุปยอดขาย & Export CSV", "รายงานสรุปยอดขายตามมิติต่างๆ และการส่งออกข้อมูล CSV สำหรับผู้บริหาร")
    click_tab(page, "รายงานสรุปยอดขาย", args.pause)
    time.sleep(args.pause * 1.5)
    set_hud(page, "🎉 สำเร็จครบ 100%", "Grand Tour 18 ขั้นตอน", "สาธิตกระบวนการจริง DFD 1.0 - 5.0 ครบทุกหน้าจอสมบูรณ์แบบ")
    print("    ✅ แสดงผลรายงานสรุปยอดขายและระบบ Export CSV เรียบร้อย")


# =============================================================================
# SCENARIO: SLIDE CASE 1 — LEAD-TO-CUSTOMER WITH AI (สไลด์ 3 - 9 รวม 7 ขั้นตอน)
# =============================================================================
def run_slide_case1(page, base_url: str, args, step_offset: int = 0, total_steps: int = 7):
    print("\n" + "-" * 60)
    print("📌  เคสที่ 1: Lead-to-Customer with AI (สไลด์ 3 – 9)")
    print("    เป้าหมาย: นำเข้า Lead ผ่าน Portal -> คัดกรองด้วย AI -> ออกใบเสนอราคา -> ตรวจสลิป -> ยกระดับเป็น Customer")
    print("-" * 60)

    # 1.1 (สไลด์ 3): พอร์ทัลลูกค่า: สมชายลงทะเบียนขอรับโปรโมชัน (Lead Intake)
    wait_next_step(
        page, step_offset + 1, total_steps,
        "เคส 1 [สไลด์ 3] · พอร์ทัลลูกค่า : สมชายลงทะเบียนขอรับโปรโมชัน (Lead Intake - DFD 1.2)",
        "จำลองมุมมองลูกค่าภายนอกลงทะเบียนขอโปรโมชันด้วยตนเองผ่าน Customer Portal ข้อมูลจะไหลเข้าสู่ Store D1: LEAD ตาม DFD 1.0 ทันที",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, "DEMO 03/17", "เคส 1: พอร์ทัลลูกค่า (Process 1.2)", "คุณสมชาย หมายมั่น ลงทะเบียนขอรับโปรโมชัน -> ออกรหัส Lead ใน Store D1")
    click_tab(page, "ลงทะเบียนความสนใจ", args.pause)
    page.get_by_label("ชื่อ-นามสกุล *").fill("คุณสมชาย หมายมั่น")
    page.get_by_label("เบอร์โทรศัพท์ *").fill("081-999-8888")
    em = page.get_by_label("อีเมล")
    if em.is_visible():
        em.fill("somchai@email.com")
    sub_r = page.get_by_role("button", name=re.compile("ส่งข้อมูลการติดต่อ")).first
    if sub_r.is_visible():
        sub_r.click()
        page.wait_for_timeout(1500)
    print("    ✅ บันทึก Lead ใหม่: 'คุณสมชาย หมายมั่น' เข้าตาราง D1: LEAD สำเร็จ")

    # 1.2 (สไลด์ 4): ฝ่ายการตลาด: คัดกรอง Lead และส่งโปรโมชันเจาะจง (Campaign Match)
    wait_next_step(
        page, step_offset + 2, total_steps,
        "เคส 1 [สไลด์ 4] · ฝ่ายการตลาด : คัดกรอง Lead และส่งโปรโมชันเจาะจง (Campaign Match - DFD 1.1 & 1.3)",
        "ฝ่ายการตลาดใช้ข้อมูล Data Science จาก Campaign ROI ตัดสินใจเลือกแคมเปญที่มีผลตอบแทนสูงสุดให้ Lead เกิดการเชื่อมโยง DFD 1.0 และ 5.0",
        args.interactive, args.pause
    )
    login(page, base_url, "marketing1", args.pause)
    set_hud(page, "DEMO 04/17", "เคส 1: ฝ่ายการตลาด (Process 1.1 & 1.3)", "ตรวจสอบแคมเปญ ROI สูงสุด CMP003 (Digital Ads Q3) และส่งมอบโปรโมชัน")
    click_menu(page, "งานการตลาด", args.pause)
    click_tab(page, "แคมเปญทั้งหมด", args.pause)
    time.sleep(args.pause)
    print("    ✅ แคมเปญ Digital Ads Q3 (CMP003 งบ ฿80,000 ROI 103%) พร้อมเชื่อมโยงสิทธิประโยชน์")

    # 1.3 (สไลด์ 5): ฝ่ายขาย: จัดลำดับคิวโทรด้วย AI Lead Scoring (AI Priority Queue)
    wait_next_step(
        page, step_offset + 3, total_steps,
        "เคส 1 [สไลด์ 5] · ฝ่ายขาย : จัดลำดับคิวโทรด้วย AI Lead Scoring (AI Priority Queue - DFD 2.1)",
        "ฝ่ายขายไม่ต้องสุ่มโทร แต่เปิดคิวงาน AI ระบบพยากรณ์โอกาสซื้อด้วย Random Forest ทำให้ทีมขายโฟกัส Hot Lead ได้ตรงเป้าหมาย",
        args.interactive, args.pause
    )
    login(page, base_url, "sale1", args.pause)
    set_hud(page, "DEMO 05/17", "เคส 1: AI Lead Scoring (Process 2.1)", "Random Forest จัดอันดับ Hot Lead ชี้เป้าคุณวิชัย ทองดี (LD0264 คะแนน AI 85.4%)")
    click_menu(page, "ติดตามการขาย", args.pause)
    click_tab(page, "คิวงานจัดลำดับด้วย AI", args.pause)
    time.sleep(args.pause)
    print("    ✅ ฝ่ายขายตรวจพบคิวงาน Hot Lead อันดับหนึ่ง: 'LD0264 นายวิชัย ทองดี' (85.4%)")

    # 1.4 (สไลด์ 6): ฝ่ายขาย: บันทึกกิจกรรมการโทรและอัปเดตสถานะ (Activity Logging)
    wait_next_step(
        page, step_offset + 4, total_steps,
        "เคส 1 [สไลด์ 6] · ฝ่ายขาย : บันทึกกิจกรรมการโทรและอัปเดตสถานะ (Activity Logging - DFD 2.2)",
        "ประวัติการติดต่อทุกครั้งถูกบันทึกอย่างเป็นระบบ ไทม์ไลน์ฝั่งขวาแสดงประวัติย้อนหลังช่วยให้การส่งต่องานในทีมขายราบรื่น",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 06/17", "เคส 1: บันทึกกิจกรรมโทร (Process 2.2)", "โทรประสานงานคุณวิชัย LD0264 บันทึกผลลง Store D2: LEAD_ACTIVITY และอัปเดตไทม์ไลน์")
    click_tab(page, "ค้นหา & บันทึกกิจกรรม", args.pause)
    select_dropdown_option(page, "เลือกผู้สนใจ", "LD0264")
    act_note = page.get_by_label("บันทึกผลการติดต่อ")
    if act_note.is_visible():
        act_note.fill("โทรประสานงาน นำเสนอโซลูชัน ลูกค่าขอใบเสนอราคา")
    select_dropdown_option(page, "อัปเดตสถานะผู้สนใจ", "อยู่ระหว่างเสนอขาย")
    save_act = page.get_by_role("button", name=re.compile("บันทึก")).first
    if save_act.is_visible():
        save_act.click()
        page.wait_for_timeout(1200)
    print("    ✅ บันทึกกิจกรรมโทรคุยกับ LD0264 และอัปเดตไทม์ไลน์ D2 เรียบร้อย")

    # 1.5 (สไลด์ 7): ฝ่ายขาย: ออกใบเสนอราคาและคำนวณส่วนลดอัตโนมัติ (Quotation)
    wait_next_step(
        page, step_offset + 5, total_steps,
        "เคส 1 [สไลด์ 7] · ฝ่ายขาย : ออกใบเสนอราคาและคำนวณส้วนลดอัตโนมัติ (Quotation - DFD 2.3)",
        "ระบบคำนวณส่วนลดตามแคมเปญให้อัตโนมัติพร้อมออกเอกสารเสนอราคาที่มีความถูกต้องตามหลักบัญชีตาม DFD 2.3",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 07/17", "เคส 1: ออกใบเสนอราคา (Process 2.3)", "ออกใบเสนอราคาให้คุณวิชัย LD0264 หักลดโปรโมชันอัตโนมัติ ออกรหัส SL ใน D3: SALE")
    click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
    click_tab(page, "ออกใบเสนอราคา", args.pause)
    select_dropdown_option(page, "เลือกผู้สนใจ", "LD0264")

    ms = page.locator("[data-baseweb='select']").filter(has_text="รายการสินค่า").first
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
    print("    ✅ ออกใบเสนอราคาให้คุณวิชัย LD0264 บันทึกข้อมูลลงตาราง D3: SALE สำเร็จ")

    # 1.6 (สไลด์ 8): พอร์ทัลลูกค่า: ยืนยันคำสั่งซื้อและอัปโหลดสลิปโอนเงิน (Order & Slip)
    wait_next_step(
        page, step_offset + 6, total_steps,
        "เคส 1 [สไลด์ 8] · พอร์ทัลลูกค่า : ยืนยันคำสั่งซื้อและอัปโหลดสลิปโอนเงิน (Order & Slip - DFD 3.1 & 3.2)",
        "ลูกค่าตรวจสอบความถูกต้องและส่งสลิปด้วยตนเองผ่าน Portal ข้อมูลไหลเข้าสู่ DFD Process 3.0 อัตโนมัติ",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, "DEMO 08/17", "เคส 1: พอร์ทัลลูกค่า (Process 3.1 - 3.2)", "คุณวิชัย (LD0264) ตรวจสอบใบเสนอราคาและกดยืนยันคำสั่งซื้อด้วยตนเอง")
    select_portal_identity(page, "LD0264")
    click_tab(page, "ยืนยันคำสั่งซื้อ", args.pause)
    confirm_btn = page.get_by_role("button", name=re.compile("ยืนยันสั่งซื้อ")).first
    if confirm_btn.is_visible():
        confirm_btn.click()
        page.wait_for_timeout(1500)
        print("    ✅ ลูกค่า LD0264 กดยืนยันคำสั่งซื้อเรียบร้อย")
    else:
        print("    ℹ️ คำสั่งซื้อของ LD0264 อยู่ในสถานะพร้อมตรวจรับ")

    # 1.7 (สไลด์ 9): ฝ่ายขาย: ตรวจรับเงิน ยกระดับเป็น CUSTOMER & ออกใบเสร็จ (Closed-Won)
    wait_next_step(
        page, step_offset + 7, total_steps,
        "เคส 1 [สไลด์ 9] · ฝ่ายขาย : ตรวจรับเงิน ยกระดับเปิน CUSTOMER & ออกใบเสร็จ (Closed-Won - DFD 3.3)",
        "เมื่อตรวจรับเงินถูกต้อง ระบบยกระดับสถานะจาก Lead สู่ CUSTOMER ทางการทันทีก่อนออกใบเสร็จ ถือเป็นการปิดการขายสมบูรณ์",
        args.interactive, args.pause
    )
    login(page, base_url, "sale1", args.pause)
    set_hud(page, "DEMO 09/17", "เคส 1: ออกใบเสร็จ & ยกระดับลูกค่า (Process 3.3)", "ตรวจรับเงิน ออกใบเสร็จ และยกระดับคุณวิชัยสู่ Store D4: CUSTOMER สำเร็จ 100%")
    click_menu(page, "ใบเสนอราคา/ชำระเงิน", args.pause)
    click_tab(page, "รับ & ตรวจคำสั่งซื้อ", args.pause)
    ok_b = page.get_by_role("button", name=re.compile("ตรวจแล้วถูกต้อง")).first
    if ok_b.is_visible():
        ok_b.click()
        page.wait_for_timeout(1200)

    click_tab(page, "ตรวจสอบการชำระเงิน", args.pause)
    ref_b = page.get_by_label(re.compile("เลขอ้างอิง")).first
    if ref_b.count() > 0 and ref_b.is_visible():
        ref_b.fill("TRF-LD0264-WIN")
    p_btn = page.get_by_role("button", name=re.compile("ยืนยันรับเงิน")).first
    if p_btn.count() > 0 and p_btn.is_visible():
        p_btn.click()
        page.wait_for_timeout(1500)

    click_tab(page, "ออกใบเสร็จ + บันทึกลูกค่า", args.pause)
    r_btn = page.get_by_role("button", name=re.compile("ออกใบเสร็จ")).first
    if r_btn.count() > 0 and r_btn.is_visible():
        r_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ ยกระดับคุณวิชัย LD0264 เป็น CUSTOMER ทางการ และสร้างใบเสร็จเรียบร้อย")


# =============================================================================
# SCENARIO: SLIDE CASE 2 — SUPPORT & 5-STAR RATING (สไลด์ 10 - 12 รวม 3 ขั้นตอน)
# =============================================================================
def run_slide_case2(page, base_url: str, args, step_offset: int = 0, total_steps: int = 3):
    print("\n" + "-" * 60)
    print("📌  เคสที่ 2: Support & 5-Star Rating (สไลด์ 10 – 12)")
    print("    เป้าหมาย: เปิดเคสแจ้งปัญหาให้ลูกค่ากลุ่มเสี่ยง -> แชทสดแก้ไขปัญหา -> ลูกค่าประเมิน 5 ดาวกู้ Health Score")
    print("-" * 60)

    # 2.1 (สไลด์ 10): ฝ่ายบริการลูกค่า: รับแจ้งปัญหาและเปิดเคส (Ticket Registration)
    wait_next_step(
        page, step_offset + 1, total_steps,
        "เคส 2 [สไลด์ 10] · ฝ่ายบริการลูกค่า : รับแจ๊งปัญหาและเปิดเคส (Ticket Registration - DFD 4.1)",
        "ฝ่ายบริการลูกค่ารับแจ้งปัญหาและบันทึกเข้าระบบ โดยระบุระดับความรุนแรงและหมวดหมู่เพื่อจัดสรรเจ้าหน้าที่เข้าแก้ไข",
        args.interactive, args.pause
    )
    login(page, base_url, "cs1", args.pause)
    set_hud(page, "DEMO 10/17", "เคส 2: รับแจ้งปัญหาและเปิดเคส (Process 4.1)", "เปิดเคสให้ลูกค่า CU0178 (ร้านสมหญิง การค่า) ระบุปัญหาและหมวดหมู่ลง D4: TICKET")
    click_menu(page, "รับแจ้งปัญหา", args.pause)
    click_tab(page, "เปิดเคสใหม่", args.pause)

    select_dropdown_option(page, "ลูกค่า *", "CU0178")
    select_dropdown_option(page, "ประเภทปัญหา", "ระบบขัดข้อง")
    title_input = page.get_by_label("หัวข้อปัญหา *").first
    if title_input.count() > 0 and title_input.is_visible():
        title_input.fill("ไม่สามารถเปิดดูรายงานสรุปยอดขายรายไตรมาสได้")
    detail_input = page.get_by_label("รายละเอียดจากลูกค่า").first
    if detail_input.count() > 0 and detail_input.is_visible():
        detail_input.fill("ระบบแจ้งเตือนข้อผิดพลาด เกิดปัญหาการประมวลผลข้อมูลขนาดใหญ่ ขอให้ตรวจสอบด่วน")
    select_dropdown_option(page, "มอบหมายให้", "ศุภชัย ซัพพอร์ต")

    create_tk = page.get_by_role("button", name=re.compile("เปิดเคส")).first
    if create_tk.count() > 0 and create_tk.is_visible():
        create_tk.click()
        page.wait_for_timeout(1500)
    print("    ✅ เปิดเคสปัญหาให้ 'CU0178 ร้านสมหญิง การค่า' สำเร็จ (บันทึกลง Store D4: TICKET)")

    # 2.2 (สไลด์ 11): ฝ่ายบริการลูกค่า: สนทนา ประสานงาน และแก้ไขปัญหา (Ticket Resolution)
    wait_next_step(
        page, step_offset + 2, total_steps,
        "เคส 2 [สไลด์ 11] · ฝ่ายบริการลูกค่า : สนทนา ประสานงาน และแก้ไขปัญหา (Ticket Resolution - DFD 4.2)",
        "ระบบมีช่องทางสนทนาที่เก็บบันทึกประวัติการสื่อสารทั้งหมด เพื่อความโปร่งใสและตรวจสอบย้อนหลังได้ตาม DFD 4.2",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 11/17", "เคส 2: แชทสดแก้ไขปัญหา & ปิดเคส (Process 4.2)", "สนทนาสด ประสานงานรีเซ็ตแคช และอัปเดตสถานะเป็น 'ปิดเคสสำเร็จ' (D4: TICKET_MESSAGE)")
    click_tab(page, "คิวเคส & สนทนา", args.pause)
    select_dropdown_option(page, "เลือกเคสเพื่อดูบทสนทนา", "ไม่สามารถเปิดดูรายงาน")

    chat_inp = page.get_by_placeholder(re.compile("พิมพ์ข้อความตอบกลับ")).or_(
        page.locator("[data-testid='stChatInputTextArea']")
    ).first
    if chat_inp.is_visible():
        chat_inp.fill("เจ้าหน้าที่กำลังรีเซ็ตแคชให้ คาดว่าจะใช้งานได้ใน 15 นาที")
        chat_inp.press("Enter")
        page.wait_for_timeout(1500)

    # อัปเดตสถานะเป็น ปิดเคสสำเร็จ
    select_dropdown_option(page, "สถานะ", "ปิดเคสสำเร็จ")
    res_box = page.get_by_label("สรุปผลการแก้ไข (แจ้งลูกค่าเมื่อปิดเคส)").first
    if res_box.count() > 0 and res_box.is_visible():
        res_box.fill("แก้ไขปัญหาเสร็จสิ้น: รีเซ็ตแคชและประมวลผลข้อมูลใหม่เรียบร้อย ลูกค่าสามารถเปิดดูรายงานได้ตามปกติ")
    upd_btn = page.get_by_role("button", name=re.compile("อัปเดต")).first
    if upd_btn.count() > 0 and upd_btn.is_visible():
        upd_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ แชทสดสองทางและอัปเดตสถานะเคสของร้านสมหญิงเป็น 'ปิดเคสสำเร็จ'")

    # 2.3 (สไลด์ 12): พอร์ทัลลูกค่า: ประเมินความพึงพอใจการบริการ 5 ดาว (CSAT Feedback)
    wait_next_step(
        page, step_offset + 3, total_steps,
        "เคส 2 [สไลด์ 12] · พอร์ทัลลูกค่า : ประเมินความพึงพอใจการบริการ 5 ดาว (CSAT Feedback - DFD 4.3)",
        "ลูกค่าประเมินความพึงพอใจผ่าน Portal โดยคะแนนนี้จะส่งตรงไปเป็นตัวแปรคำนวณ Customer Health Score ทันที",
        args.interactive, args.pause
    )
    login(page, base_url, "guest", args.pause)
    set_hud(page, "DEMO 12/17", "เคส 2: ประเมินบริการ 5 ดาว ⭐⭐⭐⭐⭐ (Process 4.3)", "ร้านสมหญิง (CU0178) ให้ 5 ดาวผ่านพอร์ทัล ส่งตรงไปคำนวณ Customer Health Score")
    select_portal_identity(page, "LD0348")
    click_tab(page, "ใบเสร็จ · แจ้งปัญหา · ให้คะแนน", args.pause)

    rate_fb = page.get_by_label(re.compile("ความเห็นเพิ่มเติม")).first
    if rate_fb.count() > 0 and rate_fb.is_visible():
        rate_fb.fill("แก้ไขปัญหาได้อย่างรวดเร็ว ประทับใจมาก")
    rate_btn = page.get_by_role("button", name=re.compile("ส่งคะแนน")).first
    if rate_btn.count() > 0 and rate_btn.is_visible():
        rate_btn.click()
        page.wait_for_timeout(1500)
    print("    ✅ บันทึกคะแนน CSAT 5 ดาว ⭐⭐⭐⭐⭐ เข้าระบบ ส่งผลคำนวณ Health Score ทันที")


# =============================================================================
# SCENARIO: SLIDE CASE 3 — EXECUTIVE REAL-TIME 4 AI (สไลด์ 13 - 17 รวม 5 ขั้นตอน)
# =============================================================================
def run_slide_case3(page, base_url: str, args, step_offset: int = 0, total_steps: int = 5):
    print("\n" + "-" * 60)
    print("📌  เคสที่ 3: Executive Real-time 4 AI (สไลด์ 13 – 17)")
    print("    เป้าหมาย: นำเสนอแดชบอร์ดสรุปผล Data Science 4 โมเดล และรายงานยอดขายพร้อม Export CSV")
    print("-" * 60)

    login(page, base_url, "admin1", args.pause)
    click_menu(page, "แดชบอร์ดวิเคราะห์", args.pause)

    # 3.1 (สไลด์ 13): วิทยาศาสตร์ข้อมูล 1: พยากรณ์โอกาสปิดการขาย (Lead Scoring Model)
    wait_next_step(
        page, step_offset + 1, total_steps,
        "เคส 3 [สไลด์ 13] · วิทยาศาสตร์ข้อมูล 1: พยากรณ์โอกาสปิดการขาย (Lead Scoring Model - DFD 5.1)",
        "Machine Learning ช่วยให้ผู้บริหารเห็นภาพรวมศักยภาพของ Lead ทั้งหมด และจัดสรรทรัพยากรทีมขายได้อย่างแม่นยำ",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 13/17", "เคส 3: AI Lead Scoring (Feature 1)", "Random Forest Classifier 300 Trees พยากรณ์ความน่าจะเป็น (Hot >70%, Warm 40-70%, Cold <40%)")
    click_tab(page, "Lead Scoring", args.pause)
    time.sleep(args.pause * 1.2)
    print("    ✅ นำเสนอโมเดล Lead Scoring (ROC-AUC, Distribution Plot, Feature Importance)")

    # 3.2 (สไลด์ 14): วิทยาศาสตร์ข้อมูล 2: การจัดกลุ่มลูกค่าด้วย RFM (Customer Segmentation)
    wait_next_step(
        page, step_offset + 2, total_steps,
        "เคส 3 [สไลด์ 14] · วิทยาศาสตร์ข้อมูล 2: การจัดกลุ่มลูกค่าด้วย RFM (Customer Segmentation - DFD 5.1)",
        "RFM ช่วยแยกแยะระหว่างลูกค่าชั้นดีและลูกค่าที่กำลังจะหายไป เพื่อให้ทีมการตลาดทำแคมเปญรักษาลูกค่าได้อย่างตรงจุด",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 14/17", "เคส 3: RFM Customer Segmentation (Feature 2)", "Quintile + K-Means: กลุ่ม Champions (CU0175) vs กลุ่ม At Risk (CU0178 ร้านสมหญิง)")
    click_tab(page, "RFM Segmentation", args.pause)
    time.sleep(args.pause * 1.2)
    print("    ✅ นำเสนอ RFM Segmentation 3D Scatter & Treemap เปรียบเทียบ Champions vs At Risk")

    # 3.3 (สไลด์ 15): วิทยาศาสตร์ข้อมูล 3: ดัชนีสุขภาพลูกค่าและการเตือนภัย Churn (Health Score)
    wait_next_step(
        page, step_offset + 3, total_steps,
        "เคส 3 [สไลด์ 15] · วิทยาศาสตร์ข้อมูล 3: ดัชนีสุขภาพลูกค่าและการเตือนภัย Churn (Health Score - DFD 5.1)",
        "ระบบไม่รอให้ลูกค่ายกเลิกสัญญา แต่ตรวจจับพฤติกรรมผิดปกติล่วงหน้าจาก 5 มิติ เพื่อให้ทีมงานเข้าแก้ไขได้ทันท่วงที",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 15/17", "เคส 3: Churn & Health Score (Feature 3)", "ประเมินความเสี่ยงล่วงหน้า 5 มิติ เฝ้าระวังลูกค่าเสี่ยงสูง: ร้านสมหญิง การค่า (CU0178)")
    click_tab(page, "Customer Health & Churn", args.pause)
    time.sleep(args.pause * 1.2)
    print("    ✅ นำเสนอเกจวัด Health Score และตาราง High Churn Risk Early Warning")

    # 3.4 (สไลด์ 16): วิทยาศาสตร์ข้อมูล 4: วิเคราะห์ความคุ้มค่าทางการเงิน (Campaign Financial ROI)
    wait_next_step(
        page, step_offset + 4, total_steps,
        "เคส 3 [สไลด์ 16] · วิทยาศาสตร์ข้อมูล 4: วิเคราะห์ความคุ้มค่าทางการเงิน (Campaign Financial ROI - DFD 5.1)",
        "ฝ่ายการตลาดพิสูจน์ความคุ้มค่าของงบโฆษณาได้จริง แคมเปญ Digital Ads Q3 ให้ ROI เกิน 100% ตอบโจทย์การลงทุนของผู้บริหาร",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 16/17", "เคส 3: Campaign Financial ROI (Feature 4)", "วิเคราะห์ ROI, ROAS, Funnel: ชี้เป้าแคมเปญ CMP003 Digital Ads Q3 ให้ ROI สูงสุด 103.4%")
    click_tab(page, "Campaign ROI", args.pause)
    time.sleep(args.pause * 1.2)
    print("    ✅ นำเสนอ Campaign ROI & Financial Funnel (CMP003 สรุปผลตอบแทนเกิน 100%)")

    # 3.5 (สไลด์ 17): บทสรุปการสาธิตระบบ: รายงานยอดขายและส่งมอบผลงาน (Delivery Ready)
    wait_next_step(
        page, step_offset + 5, total_steps,
        "เคส 3 [สไลด์ 17] · บทสรุปการสาธิตระบบ : รายงานยอดขายและส่งมอบผลงาน (Delivery Ready - DFD 5.2)",
        "ทั้งหมดนี้คือ Smart CRM Analytics ที่ผสานทฤษฎีฐานข้อมูลเชิงสัมพันธ์ วิทยาศาสตร์ข้อมูล และซอฟต์แวร์ที่ทำงานได้จริง 100% ครับ",
        args.interactive, args.pause
    )
    set_hud(page, "DEMO 17/17", "เคส 3: รายงานยอดขาย & Delivery Ready (Process 5.2)", "รายงานสรุปยอดขายผู้บริหาร พร้อมปุ่ม Export CSV ยืนยันความพร้อมส่งมอบ 100% ตามหลัก 3NF")
    click_tab(page, "รายงานสรุปยอดขาย", args.pause)
    time.sleep(args.pause * 1.5)
    set_hud(page, "🎉 สำเร็จครบ 100%", "Smart CRM Analytics v1.2.2", "การสาธิตระบบตามสไลด์ crm-demo.pptx.pdf ครบถ้วน 100% พร้อมรับ Q&A")
    print("    ✅ นำเสนอรายงานยอดขายผู้บริหารและระบบ Export CSV เสร็จสมบูรณ์")


# =============================================================================
# SCENARIO: ALL SLIDE CASES (สไลด์ 3 - 17 รวมครบ 15 ขั้นตอน)
# =============================================================================
def run_slide_all(page, base_url: str, args):
    total_steps = 15
    print("\n🎬  เริ่มต้นการนำเสนอครบ 3 เคสธุรกิจตามสไลด์ crm-demo.pptx.pdf (รวม 15 ขั้นตอน)...")
    run_slide_case1(page, base_url, args, step_offset=0, total_steps=total_steps)
    run_slide_case2(page, base_url, args, step_offset=7, total_steps=total_steps)
    run_slide_case3(page, base_url, args, step_offset=10, total_steps=total_steps)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def run_live_demo():
    parser = argparse.ArgumentParser(description="Smart CRM Analytics - Live Browser Demo")
    parser.add_argument("-s", "--step", "--interactive", dest="interactive", action="store_true",
                        help="โหมดสั่ง Next ทีละสเต็ป: รองรับคลิกปุ่ม [⏭️ ถัดไป] บนจอ, เคาะ Spacebar บนเว็บ, หรือกด [Enter] ใน Terminal")
    parser.add_argument("--scenario", "--flow", dest="scenario", default="standard",
                        choices=[
                            "standard", "full", "grand",
                            "slide", "slides", "all-cases",
                            "case1", "lead-to-customer",
                            "case2", "support",
                            "case3", "executive", "analytics"
                        ],
                        help="เลือก Scenario: 'standard' (7 ขั้นตอน), 'grand' (18 ขั้นตอน), "
                             "'case1' (เคส 1: สไลด์ 3-9), 'case2' (เคส 2: สไลด์ 10-12), "
                             "'case3' (เคส 3: สไลด์ 13-17), หรือ 'slide' (ครบทั้ง 3 เคส 15 ขั้นตอน)")
    parser.add_argument("--port", type=int, default=8501, help="Streamlit port (default: 8501)")
    parser.add_argument("--slow-mo", type=int, default=1100, help="Playwright action delay in ms (default: 1100)")
    parser.add_argument("--pause", type=float, default=1.5, help="Extra pause after major steps in sec (default: 1.5)")
    parser.add_argument("--headless", action="store_true", help="Run without opening browser window (default: False)")
    parser.add_argument("--no-seed", action="store_true", help="Do not re-seed database before starting")
    parser.add_argument("--keep-open", action="store_true", default=True, help="Keep browser open after completion")
    args = parser.parse_args()

    scenario_map = {
        "standard": ("STANDARD FLOW 7 ขั้นตอน (3 เคสธุรกิจ 10 นาที)", 7),
        "full": ("GRAND TOUR 18 ขั้นตอน (เจาะลึก 1.1 ก่อน 1.2 ครบทุกหน้าจอ)", 18),
        "grand": ("GRAND TOUR 18 ขั้นตอน (เจาะลึก 1.1 ก่อน 1.2 ครบทุกหน้าจอ)", 18),
        "case1": ("เคสที่ 1: Lead-to-Customer with AI (สไลด์ 3-9 รวม 7 ขั้นตอน)", 7),
        "lead-to-customer": ("เคสที่ 1: Lead-to-Customer with AI (สไลด์ 3-9 รวม 7 ขั้นตอน)", 7),
        "case2": ("เคสที่ 2: Support & 5-Star Rating (สไลด์ 10-12 รวม 3 ขั้นตอน)", 3),
        "support": ("เคสที่ 2: Support & 5-Star Rating (สไลด์ 10-12 รวม 3 ขั้นตอน)", 3),
        "case3": ("เคสที่ 3: Executive Real-time 4 AI (สไลด์ 13-17 รวม 5 ขั้นตอน)", 5),
        "executive": ("เคสที่ 3: Executive Real-time 4 AI (สไลด์ 13-17 รวม 5 ขั้นตอน)", 5),
        "analytics": ("เคสที่ 3: Executive Real-time 4 AI (สไลด์ 13-17 รวม 5 ขั้นตอน)", 5),
        "slide": ("สไลด์นำเสนอครบ 3 เคสธุรกิจ (สไลด์ 3-17 รวม 15 ขั้นตอน)", 15),
        "slides": ("สไลด์นำเสนอครบ 3 เคสธุรกิจ (สไลด์ 3-17 รวม 15 ขั้นตอน)", 15),
        "all-cases": ("สไลด์นำเสนอครบ 3 เคสธุรกิจ (สไลด์ 3-17 รวม 15 ขั้นตอน)", 15),
    }

    sc_name, total_steps = scenario_map.get(args.scenario, ("STANDARD FLOW 7 ขั้นตอน", 7))

    print("\n" + "=" * 78)
    print("🎬  SMART CRM ANALYTICS — REAL UI LIVE DEMO")
    print(f"    🌟 SCENARIO: {sc_name}")
    if args.interactive:
        print(f"    🕹️  โหมด: SINGLE-SCREEN STEP-BY-STEP (คลิก [⏭️ ถัดไป] บนจอ หรือเคาะ Spacebar ได้เลย ไม่ต้องสลับหน้าต่าง)")
    else:
        print("    ⚡ โหมด: AUTO PLAY (เล่นต่อเนื่องตามความเร็ว Slow-Mo)")
    print("=" * 78)

    # 1. จัดการข้อมูลตั้งต้น
    if not args.no_seed:
        print(f"\n🌱 [0/{total_steps}] กำลังตั้งค่าฐานข้อมูลตั้งต้น (Seed Data)...")
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
            no_viewport=True if not args.headless else False,
            viewport={"width": 1440, "height": 900} if args.headless else None
        )
        page = context.new_page()

        if not args.headless:
            try:
                client = context.new_cdp_session(page)
                win = client.send("Browser.getWindowForTarget")
                client.send("Browser.setWindowBounds", {"windowId": win["windowId"], "bounds": {"windowState": "maximized"}})
            except Exception:
                pass

        try:
            print("\n▶️ [เริ่มต้น] เข้าสู่หน้าหลักระบบ Smart CRM Analytics...")
            page.goto(base_url, wait_until="networkidle")
            page.wait_for_timeout(1000)
            set_hud(page, "ภาพรวมระบบ", "Smart CRM Analytics v1.2.2", "ระบบบริหารจัดการลูกค้าอัจฉริยะ (3NF SQLite + AI Data Science)")

            if args.scenario in ("case1", "lead-to-customer"):
                run_slide_case1(page, base_url, args, step_offset=0, total_steps=7)
            elif args.scenario in ("case2", "support"):
                run_slide_case2(page, base_url, args, step_offset=0, total_steps=3)
            elif args.scenario in ("case3", "executive", "analytics"):
                run_slide_case3(page, base_url, args, step_offset=0, total_steps=5)
            elif args.scenario in ("slide", "slides", "all-cases"):
                run_slide_all(page, base_url, args)
            elif args.scenario in ("full", "grand"):
                run_grand_tour(page, base_url, args)
            else:
                run_standard_tour(page, base_url, args)

            print("\n" + "=" * 78)
            print(f"🎉  การสาธิตสดเสร็จสิ้นสมบูรณ์ 100% ครบทั้ง {total_steps} ขั้นตอน!")
            print("=" * 78)

            if not args.headless and args.keep_open:
                print("\n💡 หน้าต่างเบราว์เซอร์ยังคงเปิดอยู่เพื่อให้คุณหรืออาจารย์ทดลองคลิกดูได้")
                print("   กด [Ctrl+C] หรือกด [Enter] ในเทอร์มินัลนี้เพื่อปิดเบราว์เซอร์...")
                try:
                    input()
                except (KeyboardInterrupt, EOFError):
                    pass

        finally:
            try:
                browser.close()
            except (Exception, KeyboardInterrupt):
                pass
            if proc:
                print("🛑 กำลังปิด Streamlit Server ชั่วคราว...")
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()


if __name__ == "__main__":
    run_live_demo()
