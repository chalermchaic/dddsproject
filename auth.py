"""
Auth ชั้นบางๆ สำหรับ prototype — เลือกบัญชีพนักงานเพื่อเข้าใช้งาน (ไม่มีรหัสผ่าน)
1 บัญชี = 1 แถวใน EMPLOYEE; role กำหนดว่าเห็นเมนูหน้าไหนบ้าง
"""
from __future__ import annotations

import streamlit as st

from db.connection import run_query

ROLE_TH = {
    "admin":     "ผู้ดูแลระบบ",
    "marketing": "ฝ่ายการตลาด",
    "sales":     "ฝ่ายขาย",
    "support":   "ฝ่ายบริการลูกค้า",
    "guest":     "ผู้สนใจ / ลูกค้า (จำลอง)",
}

# บัญชีจำลองสำหรับสวมบทเป็น external entity (ผู้สนใจ/ลูกค้า) ใน DFD
GUEST_USER = dict(employee_id=None, username="guest", name="ผู้สนใจ / ลูกค้า",
                  role="guest", department="-", position="-")

# หน้า → role ที่เข้าถึงได้  (ลำดับในลิสต์ = ลำดับในเมนู)
PAGE_DEFS = [
    dict(path="pages/0_home.py",                title="ภาพรวม",              icon="🏠", url_path="home",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/1_marketing.py",           title="งานการตลาด",          icon="📢", url_path="marketing",
         roles={"admin", "marketing"}),
    dict(path="pages/2_sales_followup.py",      title="ติดตามการขาย",        icon="📞", url_path="sales-followup",
         roles={"admin", "sales"}),
    dict(path="pages/3_order_billing.py",       title="ใบเสนอราคา/ชำระเงิน",  icon="🧾", url_path="order-billing",
         roles={"admin", "sales"}),
    dict(path="pages/4_customer_profile.py",    title="ข้อมูลลูกค้า",         icon="👤", url_path="customer-profile",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/5_support_ticket.py",      title="รับแจ้งปัญหา",         icon="🎫", url_path="support-ticket",
         roles={"admin", "support"}),
    dict(path="pages/6_analytics_dashboard.py", title="แดชบอร์ดวิเคราะห์",    icon="📊", url_path="analytics-dashboard",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/9_portal.py",              title="Portal ผู้สนใจ/ลูกค้า", icon="🌐", url_path="portal",
         roles={"guest"}),
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
    """คืนอ็อบเจกต์ st.navigation ที่มีเฉพาะหน้าที่ role นี้เข้าถึงได้"""
    allowed = [d for d in PAGE_DEFS if role in d["roles"]]
    pages = [
        st.Page(d["path"], title=d["title"], icon=d["icon"],
                url_path=d.get("url_path"), default=(i == 0))
        for i, d in enumerate(allowed)
    ]
    return st.navigation(pages)


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


def render_login(app_version: str = "") -> None:
    """หน้า landing: เลือกบัญชีเพื่อเข้าสู่ระบบ"""
    st.title("📈 Smart CRM Analytics")
    st.caption("เลือกบัญชีผู้ใช้เพื่อเข้าสู่ระบบ — prototype สาธิต ไม่มีรหัสผ่าน"
               + (f" · v{app_version}" if app_version else ""))
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
        st.subheader(ROLE_TH[role])
        cols = st.columns(min(4, len(sub)) or 1)
        for i, r in enumerate(sub.itertuples()):
            with cols[i % len(cols)]:
                st.markdown(f"**{r.Employee_Name}**  \n{r.Position}")
                if st.button(f"เข้าใช้งานเป็น {r.Username}",
                             key=f"login_{r.Username}", use_container_width=True):
                    login(dict(employee_id=r.Employee_ID, username=r.Username,
                                name=r.Employee_Name, role=r.Role,
                                department=r.Department, position=r.Position))
                    st.rerun()

    st.divider()
    st.subheader(ROLE_TH["guest"])
    st.caption("สวมบทเป็นผู้สนใจ/ลูกค้า เพื่อทดลอง flow ที่ส่งข้อมูลเข้าระบบ "
               "(ลงทะเบียน, ยืนยันคำสั่งซื้อ, อัปโหลดสลิป, แจ้งปัญหา, ให้คะแนนบริการ)")
    if st.button("🌐 เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)", use_container_width=True,
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


def sidebar_userbox(app_version: str = "") -> None:
    u = current_user()
    with st.sidebar:
        st.markdown(f"👤 **{u['name']}**")
        st.caption(f"`{u['username']}` · {ROLE_TH.get(u['role'], u['role'])}")
        if st.button("ออกจากระบบ", use_container_width=True):
            logout()
            st.rerun()
        with st.expander("🛠️ เมนูผู้สาธิต (Demo Tool)", expanded=False):
            if st.button("🔄 รีเซ็ตฐานข้อมูล Demo", key="sidebar_reset_db", use_container_width=True):
                if reset_database():
                    st.toast("✅ รีเซ็ตฐานข้อมูลเรียบร้อย!", icon="🌱")
                    st.rerun()
        st.divider()
        if app_version:
            st.caption(f"Smart CRM Analytics · เวอร์ชัน {app_version}")

