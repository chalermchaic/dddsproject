"""
Smart CRM Analytics — entry point / router
รัน: streamlit run app.py

- ยังไม่ล็อกอิน  → หน้าเลือกบัญชีผู้ใช้ (auth.render_login)
- ล็อกอินแล้ว   → เมนู st.navigation ที่มีเฉพาะหน้าของ role นั้น
"""
from pathlib import Path

import streamlit as st

import auth

_version_file = Path(__file__).parent / "VERSION"
APP_VERSION = _version_file.read_text(encoding="utf-8").strip() if _version_file.exists() else "dev"

st.set_page_config(page_title="Smart CRM Analytics",
                   page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

user = auth.current_user()
if user is None:
    auth.render_login(APP_VERSION)
    st.stop()

auth.sidebar_userbox(APP_VERSION)
auth.build_navigation(user["role"]).run()
