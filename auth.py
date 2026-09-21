"""
Auth ชั้นบางๆ สำหรับ prototype — เลือกบัญชีพนักงานเพื่อเข้าใช้งาน (ไม่มีรหัสผ่าน)
1 บัญชี = 1 แถวใน EMPLOYEE; role กำหนดว่าเห็นเมนูหน้าไหนบ้าง
"""
from __future__ import annotations

import re

import streamlit as st

from db.connection import run_query

ROLE_TH = {
    "admin":     "ผู้ดูแลระบบ",
    "marketing": "ฝ่ายการตลาด",
    "sales":     "ฝ่ายขาย",
    "support":   "ฝ่ายบริการลูกค้า",
    "guest":     "ผู้สนใจ / ลูกค้า (จำลอง)",
}

# คำนำหน้า username → คำเต็มสำหรับแสดงผล (เช่น "cs1" -> "Customer Support 1")
USERNAME_PREFIX_LABEL = {
    "admin": "Admin", "marketing": "Marketing", "sale": "Sale", "cs": "Customer Support",
}


def display_username(username: str) -> str:
    """แปลง username ดิบ (เช่น cs1) เป็นข้อความอ่านง่าย (เช่น Customer Support 1)"""
    m = re.match(r"^([a-zA-Z]+)(\d+)$", username)
    if not m:
        return username
    prefix, num = m.groups()
    label = USERNAME_PREFIX_LABEL.get(prefix.lower(), prefix.capitalize())
    return f"{label} {num}"

# บัญชีจำลองสำหรับสวมบทเป็น external entity (ผู้สนใจ/ลูกค้า) ใน DFD
GUEST_USER = dict(employee_id=None, username="guest", name="ผู้สนใจ / ลูกค้า",
                  role="guest", department="-", position="-")

# หน้า → role ที่เข้าถึงได้  (ลำดับในลิสต์ = ลำดับในเมนู)
# group="" = ไม่มีหัวข้อกลุ่ม (แสดงบนสุดของเมนู เหมือน "Dashboard" เดี่ยวๆ ในเทมเพลต backoffice ทั่วไป)
PAGE_DEFS = [
    dict(path="pages/0_home.py",                title="ภาพรวม",              icon=":material/dashboard:", url_path="home",
         roles={"admin", "marketing", "sales", "support"}, group=""),
    dict(path="pages/1_marketing.py",           title="งานการตลาด",          icon=":material/campaign:", url_path="marketing",
         roles={"admin", "marketing"}, group="งานขาย & การตลาด"),
    dict(path="pages/2_sales_followup.py",      title="ติดตามการขาย",        icon=":material/call:", url_path="sales-followup",
         roles={"admin", "sales"}, group="งานขาย & การตลาด"),
    dict(path="pages/3_order_billing.py",       title="ใบเสนอราคา/ชำระเงิน",  icon=":material/receipt_long:", url_path="order-billing",
         roles={"admin", "sales"}, group="งานขาย & การตลาด"),
    dict(path="pages/4_customer_profile.py",    title="ข้อมูลลูกค้า",         icon=":material/person:", url_path="customer-profile",
         roles={"admin", "marketing", "sales", "support"}, group="บริการลูกค้า"),
    dict(path="pages/5_support_ticket.py",      title="รับแจ้งปัญหา",         icon=":material/confirmation_number:", url_path="support-ticket",
         roles={"admin", "support"}, group="บริการลูกค้า"),
    dict(path="pages/6_analytics_dashboard.py", title="แดชบอร์ดวิเคราะห์",    icon=":material/monitoring:", url_path="analytics-dashboard",
         roles={"admin", "marketing", "sales", "support"}, group="รายงาน"),
    dict(path="pages/9_portal.py",              title="Portal ผู้สนใจ/ลูกค้า", icon=":material/public:", url_path="portal",
         roles={"guest"}, group=""),
]


def list_logins():
    """บัญชีพนักงานทั้งหมด (เรียงตาม role แล้ว username)"""
    return run_query(
        "SELECT Employee_ID, Username, Employee_Name, Position, Department, Role "
        "FROM EMPLOYEE ORDER BY Role, Username"
    )


def current_user() -> dict | None:
    return st.session_state.get("user")


def login(user: dict) -> None:
    st.session_state["user"] = user


def logout() -> None:
    st.session_state.pop("user", None)


def guard(*roles: str) -> dict:
    """เรียกบนหัวหน้าเพจ — บังคับว่าต้อง login และ (ถ้าระบุ) ต้องมี role ที่อนุญาต"""
    u = current_user()
    if u is None:
        st.error("กรุณาเข้าสู่ระบบก่อนใช้งาน")
        st.stop()
    if roles and u["role"] not in roles:
        st.error("บัญชีของคุณไม่มีสิทธิ์เข้าถึงหน้านี้")
        st.stop()
    return u


def build_navigation(role: str):
    """คืนอ็อบเจกต์ st.navigation (จัดกลุ่มตาม PAGE_DEFS[].group) เฉพาะหน้าที่ role นี้เข้าถึงได้"""
    allowed = [d for d in PAGE_DEFS if role in d["roles"]]
    sections: dict[str, list] = {}
    for i, d in enumerate(allowed):
        page = st.Page(d["path"], title=d["title"], icon=d["icon"],
                        url_path=d.get("url_path"), default=(i == 0))
        sections.setdefault(d.get("group", ""), []).append(page)
    return st.navigation(sections)


def breadcrumb(label: str) -> None:
    """เส้นทางหน้าเล็กๆ เหนือหัวข้อหน้า — เรียกก่อน st.title() ในแต่ละหน้า"""
    st.markdown(
        f"<p style='color:#8A8F98;font-size:.8rem;margin:0 0 .15rem 0;'>"
        f"หน้าหลัก&nbsp;/&nbsp;{label}</p>",
        unsafe_allow_html=True,
    )


def reset_database() -> bool:
    """รีเซ็ตฐานข้อมูลเป็นสถานะเริ่มต้น (Seed Data) และล้าง cache ทั้งหมด"""
    import os
    import subprocess
    import sys
    root = os.path.dirname(os.path.abspath(__file__))
    try:
        subprocess.run([sys.executable, "db/seed_data.py"], cwd=root, check=True,
                       capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการรีเซ็ตฐานข้อมูล: {e}")
        return False


ROLE_ICON = {"admin": "🛡️", "marketing": "📢", "sales": "📞", "support": "🎧"}


def render_login(app_version: str = "") -> None:
    """หน้า landing: เลือกบัญชีเพื่อเข้าสู่ระบบ"""
    st.markdown(
        "<div style='display:flex;align-items:center;gap:.75rem;margin-bottom:.25rem;'>"
        "<div style='width:48px;height:48px;border-radius:12px;background:#FF7A1A;"
        "display:flex;align-items:center;justify-content:center;font-size:1.5rem;"
        "box-shadow:0 4px 10px rgba(255,122,26,.35);'>📈</div>"
        "<div><div style='font-size:1.6rem;font-weight:800;line-height:1.2;'>Smart CRM Analytics</div>"
        f"<div style='color:#8A8F98;font-size:.85rem;'>เลือกบัญชีผู้ใช้เพื่อเข้าสู่ระบบ — "
        f"prototype สาธิต ไม่มีรหัสผ่าน" + (f" · v{app_version}" if app_version else "") + "</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.divider()

    try:
        df = list_logins()
    except FileNotFoundError:
        with st.spinner("🌱 กำลังเตรียมฐานข้อมูลเริ่มต้นสำหรับ Cloud..."):
            reset_database()
            df = list_logins()

    for role in ("admin", "marketing", "sales", "support"):
        sub = df[df.Role == role]
        if sub.empty:
            continue
        st.markdown(f"##### {ROLE_ICON.get(role, '👤')} {ROLE_TH[role]}")
        cols = st.columns(4)
        for i, r in enumerate(sub.itertuples()):
            with cols[i % len(cols)]:
                with st.container(border=True):
                    st.markdown(f'<span class="card-shadow-marker" data-user="{r.Username}"></span>', unsafe_allow_html=True)
                    st.markdown(f"**{r.Employee_Name}**  \n"
                                f"<span style='color:#8A8F98;font-size:.85rem;'>"
                                f"{r.Position} ({display_username(r.Username)})</span>",
                                unsafe_allow_html=True)
                    if st.button("เข้าสู่ระบบ",
                                 key=f"login_{r.Username}", use_container_width=True,
                                 type="primary"):
                        login(dict(employee_id=r.Employee_ID, username=r.Username,
                                    name=r.Employee_Name, role=r.Role,
                                    department=r.Department, position=r.Position))
                        st.rerun()
        st.write("")

    st.divider()
    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.markdown(f"##### 🌐 {ROLE_TH['guest']}")
        st.caption("สวมบทเป็นผู้สนใจ/ลูกค้า เพื่อทดลอง flow ที่ส่งข้อมูลเข้าระบบ "
                   "(ลงทะเบียน, ยืนยันคำสั่งซื้อ, อัปโหลดสลิป, แจ้งปัญหา, ให้คะแนนบริการ)")
        if st.button("🌐 เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)",
                     key="login_guest"):
            login(dict(GUEST_USER))
            st.rerun()

    st.divider()
    with st.expander("🛠️ เมนูสำหรับผู้สาธิต (Demo Tools & Data Reset)", expanded=False):
        st.caption("คลิกปุ่มด้านล่างเพื่อคืนค่าข้อมูลตัวอย่างตั้งต้นทั้งหมด (`seed_data.py`) ให้พร้อมสำหรับการ Demo สดรอบใหม่:")
        if st.button("🔄 รีเซ็ตฐานข้อมูล Demo (Reset Database)", key="login_reset_db", use_container_width=True):
            if reset_database():
                st.toast("✅ รีเซ็ตฐานข้อมูลเรียบร้อย พร้อมสำหรับ Demo!", icon="🌱")
                st.rerun()


def sidebar_header(app_version: str = "") -> None:
    """หัว sidebar: โลโก้ระบบ + การ์ดโปรไฟล์ผู้ใช้ — เรียกก่อนสร้างเมนูนำทาง"""
    u = current_user()
    with st.sidebar:
        with st.container():
            st.markdown('<span class="sidebar-brand-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                "<div style='display:flex;align-items:center;gap:.5rem;"
                "padding:.25rem 0 .75rem 0;'>"
                "<span style='font-size:1.6rem;line-height:1'>🟧</span>"
                "<span style='font-size:1.15rem;font-weight:700;'>Smart CRM</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.markdown(f"👤 **{u['name']}**")
                st.caption(f"{ROLE_TH.get(u['role'], u['role'])} ({display_username(u['username'])})")
                if st.button("🚪 ออกจากระบบ", key="header_logout_btn", use_container_width=True):
                    logout()
                    st.rerun()


def sidebar_footer(app_version: str = "") -> None:
    """ท้าย sidebar: ปุ่มออกจากระบบ + เครื่องมือสาธิต — เรียกหลังสร้างเมนูนำทาง"""
    with st.sidebar:
        st.divider()
        with st.container():
            st.markdown('<span class="sidebar-logout-marker"></span>', unsafe_allow_html=True)
            if st.button("ออกจากระบบ", use_container_width=True):
                logout()
                st.rerun()
        with st.expander("🛠️ เมนูผู้สาธิต (Demo Tool)", expanded=False):
            if st.button("🔄 รีเซ็ตฐานข้อมูล Demo", key="sidebar_reset_db", use_container_width=True):
                if reset_database():
                    st.toast("✅ รีเซ็ตฐานข้อมูลเรียบร้อย!", icon="🌱")
                    st.rerun()
        if app_version:
            st.caption(f"Smart CRM Analytics · เวอร์ชัน {app_version}")

