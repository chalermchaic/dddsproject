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
    dict(path="pages/0_🏠_Home.py",               title="ภาพรวม",             icon="🏠",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/1_📢_Marketing.py",           title="งานการตลาด",         icon="📢",
         roles={"admin", "marketing"}),
    dict(path="pages/2_📞_Sales_Followup.py",      title="ติดตามการขาย",       icon="📞",
         roles={"admin", "sales"}),
    dict(path="pages/3_🧾_Order_Billing.py",       title="ใบเสนอราคา/ชำระเงิน", icon="🧾",
         roles={"admin", "sales"}),
    dict(path="pages/4_👤_Customer_Profile.py",    title="ข้อมูลลูกค้า",        icon="👤",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/5_🎫_Support_Ticket.py",      title="รับแจ้งปัญหา",        icon="🎫",
         roles={"admin", "support"}),
    dict(path="pages/6_📊_Analytics_Dashboard.py", title="แดชบอร์ดวิเคราะห์",   icon="📊",
         roles={"admin", "marketing", "sales", "support"}),
    dict(path="pages/9_🌐_Portal.py",              title="Portal ผู้สนใจ/ลูกค้า", icon="🌐",
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
        st.Page(d["path"], title=d["title"], icon=d["icon"], default=(i == 0))
        for i, d in enumerate(allowed)
    ]
    return st.navigation(pages)


def render_login(app_version: str = "") -> None:
    """หน้า landing: เลือกบัญชีเพื่อเข้าสู่ระบบ"""
    st.title("📈 Smart CRM Analytics")
    st.caption("เลือกบัญชีผู้ใช้เพื่อเข้าสู่ระบบ — prototype สาธิต ไม่มีรหัสผ่าน"
               + (f" · v{app_version}" if app_version else ""))
    st.divider()

    try:
        df = list_logins()
    except FileNotFoundError:
        st.error("ยังไม่มีฐานข้อมูล — รัน `python db/seed_data.py` ก่อน")
        st.stop()

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


def sidebar_userbox(app_version: str = "") -> None:
    u = current_user()
    with st.sidebar:
        st.markdown(f"👤 **{u['name']}**")
        st.caption(f"`{u['username']}` · {ROLE_TH.get(u['role'], u['role'])}")
        if st.button("ออกจากระบบ", use_container_width=True):
            logout()
            st.rerun()
        st.divider()
        if app_version:
            st.caption(f"Smart CRM Analytics · เวอร์ชัน {app_version}")
