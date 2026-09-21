"""
Smart CRM Analytics — entry point / router
รัน: streamlit run app.py

- ยังไม่ล็อกอิน  → หน้าเลือกบัญชีผู้ใช้ (auth.render_login)
- ล็อกอินแล้ว   → เมนู st.navigation ที่มีเฉพาะหน้าของ role นั้น
"""
from pathlib import Path

import plotly.io as pio
import streamlit as st

import auth

# กราฟ Plotly ทุกกราฟในแอปใช้พื้นหลังขาวเป็นค่าเริ่มต้น (ให้กลืนกับการ์ดขาว) โดยไม่ต้องตั้งทีละกราฟ
pio.templates.default = "plotly_white"

_version_file = Path(__file__).parent / "VERSION"
APP_VERSION = _version_file.read_text(encoding="utf-8").strip() if _version_file.exists() else "dev"

st.set_page_config(page_title="Smart CRM Analytics",
                   page_icon="📈", layout="wide",
                   initial_sidebar_state="expanded")

# ธีม backoffice: sidebar เข้ม + การ์ด/metric แบบยกขอบมีเงาบนพื้นเนื้อหาสว่าง
st.markdown("""
<style>
  [data-testid="stSidebar"] { background-color: #171B26; }
  [data-testid="stSidebar"] * { color: #E7E9EE; }
  [data-testid="stSidebarNav"] a { border-radius: 8px; padding-top: .5rem; padding-bottom: .5rem; }
  /* แสดงเมนูครบทุกรายการเสมอ ไม่ต้องกด "View more" */
  [data-testid="stSidebarNavItems"] { max-height: none !important; overflow: visible !important; }
  [data-testid="stSidebarNavViewButton"] { display: none !important; }
  [data-testid="stSidebarNav"] a:hover { background-color: rgba(255,255,255,.06); }
  [data-testid="stSidebarNav"] a[aria-current="page"] {
      background-color: rgba(255,122,26,.16);
  }
  [data-testid="stSidebarNav"] a[aria-current="page"] span { color: #FF9A4D !important; }
  /* หัวข้อกลุ่มเมนู (เช่น "งานขาย & การตลาด") แบบ CoreUI: ตัวพิมพ์ใหญ่ เล็ก จาง เว้นระยะตัวอักษร */
  [data-testid="stSidebarNav"] header {
      color: #6B7280 !important; font-size: .68rem !important; font-weight: 700 !important;
      text-transform: uppercase; letter-spacing: .06em;
      padding: 1rem 0 .35rem .9rem !important; margin: 0 !important;
  }
  /* ไอคอนเมนู Material Symbols: เส้นบาง โทนเดียว ขนาดเล็กลงให้ใกล้เคียง CoreUI */
  [data-testid="stSidebarNav"] [data-testid="stIconMaterial"] {
      font-size: 1.15rem; opacity: .85; color: #C7CAD1 !important;
  }
  [data-testid="stSidebarNav"] a[aria-current="page"] [data-testid="stIconMaterial"] {
      color: #FF9A4D !important; opacity: 1;
  }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.08); }
  [data-testid="stSidebar"] button {
      background-color: #232838; border: 1px solid rgba(255,255,255,.10);
  }
  [data-testid="stSidebar"] [data-testid="stExpander"] {
      background-color: #1D2231; border: 1px solid rgba(255,255,255,.08); border-radius: 8px;
  }
  [data-testid="stSidebar"] code {
      background-color: #2A2F3F; color: #E7E9EE;
  }
  /* หัวตาราง st.table (HTML จริง ปรับ CSS ได้ ต่างจาก st.dataframe ที่เป็น canvas) */
  [data-testid="stTable"] thead th {
      text-align: center !important; font-weight: 700 !important;
  }
  /* ซ่อนคอลัมน์ index ที่ .style.hide(axis="index") ไม่มีผลตอน Streamlit เรนเดอร์ —
     ใช้ class มาตรฐานของ pandas Styler (blank/row_heading) แทน */
  [data-testid="stTable"] table th.blank,
  [data-testid="stTable"] table th.row_heading {
      display: none;
  }
  /* ดึงบล็อกโลโก้+โปรไฟล์ (มาร์กด้วย .sidebar-brand-marker) ออกจากลำดับปกติ ให้ "ลอย" ไปแปะไว้บนสุดของ
     sidebar เหนือเมนูนำทาง (Streamlit บังคับให้เมนูอยู่บนสุดเสมอ นี่คือทางเดียวที่ทำให้เห็นภาพเป็นโลโก้บนสุดได้) */
  [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-brand-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .sidebar-brand-marker)) {
      position: fixed; top: 0; left: 0; width: 21rem; z-index: 20;
      padding: 1rem 1rem 0 1rem; background-color: #171B26;
  }
  [data-testid="stSidebarNav"] { margin-top: 215px; }
  /* ปุ่ม "ออกจากระบบ" (มาร์กด้วย .sidebar-logout-marker) ปักไว้ล่างสุดของ sidebar เสมอ ไม่ต้องเลื่อนหา */
  [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlockBorderWrapper"]:has(.sidebar-logout-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .sidebar-logout-marker)) {
      position: fixed; bottom: 0; left: 0; width: 21rem; z-index: 20;
      padding: .75rem 1rem; background-color: #171B26; border-top: 1px solid rgba(255,255,255,.08);
  }
  [data-testid="stSidebarUserContent"] { padding-bottom: 8rem; }

  div[data-testid="stMetric"] {
      background: #FFFFFF; border-radius: 12px; padding: 1rem 1.1rem;
      box-shadow: 0 1px 3px rgba(16,24,40,.08); border: 1px solid #ECECEE;
      min-height: 116px; display: flex; flex-direction: column; justify-content: flex-start;
  }
  /* เฉพาะ container ที่เรามาร์กไว้ด้วย .card-shadow-marker เท่านั้น — ไม่ใช้ selector กว้างที่จับ
     wrapper โครงสร้างภายในของ Streamlit เองไปด้วย (เคยทำให้เกิดเงายาวข้างขอบซ้ายทั้งหน้า)
     :not(:has(...nested wrapper...)) กันไม่ให้จับ wrapper ชั้นนอกที่ครอบ wrapper ที่มี marker ซ้อนอยู่ข้างใน */
  [data-testid="stAppViewBlockContainer"] [data-testid="stVerticalBlockBorderWrapper"]:has(.card-shadow-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .card-shadow-marker)) {
      background: #FFFFFF !important; border-radius: 12px !important;
      box-shadow: 0 1px 3px rgba(16,24,40,.06);
  }
  /* st.form() ไม่ได้ห่อด้วย stVerticalBlockBorderWrapper เหมือน st.container(border=True) — ใช้
     data-testid="stForm" ตรงๆ กฎด้านบนเลยไม่เคยจับฟอร์มได้เลย (พื้นหลัง/เงาไม่ขึ้น เห็นแค่ช่อง
     input แต่ละช่องแปะติดกันบนพื้นเทาตรงๆ ไม่มีการ์ดครอบจริง) เพิ่มกฎแยกให้ฟอร์มด้วย */
  [data-testid="stAppViewBlockContainer"] [data-testid="stForm"]:has(.card-shadow-marker) {
      background: #FFFFFF !important; border-radius: 12px !important;
      box-shadow: 0 1px 3px rgba(16,24,40,.06);
      padding: 1.25rem 1.5rem !important;
  }
  /* การ์ดโปรไฟล์ใน sidebar: โทนเข้มกลมกลืนกับ sidebar (ไม่ใช้พื้นขาว) */
  [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has(.card-shadow-marker):not(:has([data-testid="stVerticalBlockBorderWrapper"] .card-shadow-marker)) {
      background: #1D2231 !important; border-radius: 10px !important;
      border: 1px solid rgba(255,255,255,.08) !important;
  }

  /* ช่องกรอกข้อมูล (text/number/date/textarea/select) — ธีมของเราตั้งพื้นหลังเป็นสีขาวล้วน
     ทำให้เส้นขอบดีฟอลต์ของ Streamlit (คำนวณจากสีพื้นหลัง) กลายเป็นสีขาวจนมองไม่เห็นเส้นขอบเลย
     ระบุเส้นขอบเทาอ่อนให้เห็นชัดเจนแทน พร้อมเว้นระยะรอบช่องกรอกให้ไม่อึดอัด */
  [data-baseweb="input"],
  [data-baseweb="textarea"],
  [data-baseweb="select"] > div:first-child {
      border: 1.5px solid #D0D3D9 !important;
      border-radius: 8px !important;
      background-color: #FFFFFF !important;
  }
  [data-baseweb="input"]:focus-within,
  [data-baseweb="textarea"]:focus-within,
  [data-baseweb="select"] > div:first-child:focus-within {
      border-color: #FF7A1A !important;
      box-shadow: 0 0 0 1px #FF7A1A !important;
  }
  [data-testid="stElementContainer"] { margin-bottom: .35rem; }
</style>
""", unsafe_allow_html=True)

user = auth.current_user()
if user is None:
    st.markdown('<style>[data-testid="stSidebar"] {display: none;}</style>',
               unsafe_allow_html=True)
    auth.render_login(APP_VERSION)
    st.stop()

auth.sidebar_header(APP_VERSION)
nav = auth.build_navigation(user["role"])
auth.sidebar_footer(APP_VERSION)
nav.run()
