# 📋 แผนการตรวจสอบและแก้ไขผลกระทบจากการปรับแต่ง UI (UI Redesign Impact & Remediation Plan)
### โครงงาน: ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM & Data Science Analytics Platform)
**Branch:** `fix/ui-impacts` (สืบทอดจาก `ui-redesign`)  
**เป้าหมาย:** ตรวจสอบผลกระทบจากการเปลี่ยนธีม UI (Dark-Orange Backoffice Theme, Fixed Sidebar Header/Footer, Card Shadow Markers, Custom Input Borders) ต่อระบบทดสอบอัตโนมัติ สคริปต์สาธิต และเอกสารคู่มือ พร้อมกำหนดขั้นตอนแก้ไขให้กลับมาทำงานได้อย่างสมบูรณ์ 100% ก่อนส่งมอบ

---

## 🧭 ภาพรวมและที่มาของแผน (Executive Summary)

ใน branch `ui-redesign` มีการปรับโฉมการแสดงผลครั้งใหญ่เพื่อให้มีรูปลักษณ์ระดับ Enterprise (CoreUI Inspired):
1. **Sidebar Architecture:** แยกส่วนหัวโลโก้และโปรไฟล์ (`.sidebar-brand-marker`) ไว้อยู่บนสุดแบบ `position: fixed` และปุ่มออกจากระบบ (`.sidebar-logout-marker`) ปักไว้ล่างสุด
2. **Theme & Card Styling:** กำหนดโทนสี Dark-Orange (#171B26, #FF7A1A) พร้อมใช้ `<span class="card-shadow-marker"></span>` ควบคุมเงาและการจัดขอบการ์ดใน `st.container(border=True)` และ `st.form()`
3. **Form & Input Borders:** ปรับแต่งขอบ `[data-baseweb="input"]` สีเทาอ่อน (#D0D3D9) และสีส้มโฟกัส (#FF7A1A) เพื่อแก้ปัญหาเส้นขอบกลืนกับพื้นหลัง
4. **Grouped Navigation & Breadcrumb:** จัดหมวดหมู่เมนูนำทางใน `auth.py` และเพิ่ม Breadcrumbs เหนือ `st.title()` ในทุกหน้า

การเปลี่ยนแปลงทางกายภาพ (DOM Structure, Button Text, Container Hierarchy) เหล่านี้ **มีความเสี่ยงสูงที่จะทำให้ระบบอัตโนมัติ (Playwright / E2E Tests) และเอกสารคู่มือที่อิงภาพหน้าจอเดิมหลุดจากความจริง** แผนนี้จึงถูกจัดทำขึ้นเพื่อเป็นแนวทางปฏิบัติการที่ชัดเจน

---

## 🔍 การวิเคราะห์ผลกระทบรายส่วน (Detailed Impact Assessment)

```
┌────────────────────────────────────────────────────────────────────────┐
│                     UI Redesign (Commit 89d0f24)                       │
│    Dark-Orange Sidebar, Fixed Header/Footer, Card Markers, CSS Hack   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
[ 🔴 High Impact ]           [ 🔴 High Impact ]           [ 🟡 Medium Impact ]
1. E2E & Automation Tests    2. Live Demo Script          3. CSS & Responsive
   - tests/e2e/*.py             - live_browser_demo.py       - Sidebar Margin
   - Button texts change        - Selector timeouts          - Container nesting
   - Evidence capture breaks    - HUD subtitles sync         - Mobile viewport
       │                            │                            │
       └────────────────────────────┼────────────────────────────┘
                                    │
                                    ▼
                             [ 🔴 High Impact ]
                             4. Docs & Evidence
                                - docs/user_manual.md (27 screenshots)
                                - build_user_manual_docx.py
                                - export_pdf.ps1
```

### ด้านที่ 1: สคริปต์ทดสอบและแคปภาพหน้าจออัตโนมัติ (Playwright / Pytest)
* **ไฟล์เป้าหมาย:**
  * `tests/e2e/capture_manual_evidence.py` (แคปภาพ 27 ภาพของ 14 กิจกรรม DFD)
  * `tests/e2e/test_quotation_form_e2e.py`
  * `tests/e2e/test_live_demo_flow.py`
* **ประเด็นผลกระทบ:**
  * **Login Button:** เดิมเป็น `button:has-text("เข้าใช้งานเป็น {username}")` ถูกเปลี่ยนเป็น `button:has-text("เข้าสู่ระบบ")` ในการ์ดผู้ใช้แต่ละคน ทำให้ Playwright ที่หาตาม text เดิมจะ timeout
  * **DOM Nesting:** การครอบ `st.container(border=True)` และแทรก `<span class="card-shadow-marker"></span>` อาจส่งผลต่อ XPath หรือ CSS selector บางตัวที่นับ child index หรือ hierarchy
  * **Input & Selectors:** การเปลี่ยน styling ช่องกรอก อาจกระทบ event click/fill ในบางเคส

### ด้านที่ 2: สคริปต์สาธิตระบบสด (Live Browser Demo)
* **ไฟล์เป้าหมาย:**
  * `scripts/live_browser_demo.py` (โหมด Standard 7 ขั้นตอน และ Grand Tour 18 ขั้นตอน)
* **ประเด็นผลกระทบ:**
  * สคริปต์มีระบบจำลองการคลิกตามข้อความ (เช่น ข้อความบนปุ่ม, ลิงก์ใน Sidebar)
  * การจัดหมวดหมู่เมนูใน Sidebar (`auth.py`) อาจทำให้ลำดับ element หรือ selector ของเมนูเปลี่ยนไป
  * อาจเกิดอาการ Element Click Intercepted หากปุ่มหรือลิงก์ถูก Fixed Sidebar Header/Footer บังอยู่ใน viewport บางขนาด

### ด้านที่ 3: โครงสร้าง CSS และความเข้ากันได้บนจอขนาดต่างๆ (Responsive & CSS Glitches)
* **ไฟล์เป้าหมาย:**
  * `app.py`
  * `.streamlit/config.toml`
* **ประเด็นผลกระทบ:**
  * การใช้ระยะตายตัว `[data-testid="stSidebarNav"] { margin-top: 168px; }` อาจเกิดการทับซ้อน (Overlap) หรือเว้นช่องว่างเกินพอดีหากเปิดบนจอความละเอียดต่างกัน หรือเมื่อข้อความชื่อ-ตำแหน่งผู้ใช้ยาวเกิน 1 บรรทัด
  * การใช้ `:has()` และ fixed container ของ Streamlit เป็น unofficial CSS hack ซึ่งอาจแสดงผลผิดเพี้ยนหาก Streamlit มีการอัปเดตเวอร์ชัน
  * การใส่ `<span class="card-shadow-marker"></span>` ต้องตรวจสอบให้ครบทุกหน้าใน `pages/0` ถึง `pages/9` ว่าไม่มีหน้าไหนตกหล่นหรือมีการ์ดซ้อนกันจนเงาเพี้ยน

### ด้านที่ 4: เอกสารคู่มือและการส่งออกรายงาน (User Manual & Document Exports)
* **ไฟล์เป้าหมาย:**
  * `docs/user_manual.md`
  * `docs/evidence/` (ไฟล์ภาพหน้าจอ 27 ภาพ)
  * `build_user_manual_docx.py`
  * `export_pdf.ps1` และ `export_demo_pdf.ps1`
* **ประเด็นผลกระทบ:**
  * ภาพหน้าจอเดิมใน `docs/evidence/` ถูกบันทึกไว้ตั้งแต่เวอร์ชันธีมสีขาวเดิม (Light Theme) เมื่อ UI ถูกเปลี่ยนเป็น Dark-Orange Backoffice Theme ภาพในคู่มือจะไม่ตรงกับหน้าตาระบบจริง
  * จำเป็นต้องรันสคริปต์ Re-capture ภาพทั้ง 27 ภาพใหม่ทั้งหมด และ Re-build เอกสาร `.docx` / `.pdf`

---

## 🛠️ แผนการตรวจสอบทีละขั้นตอน (Step-by-Step Verification Matrix)

ผลการตรวจสอบจริงเพื่อบันทึกสถานะข้อผิดพลาด (Error Baseline):

| ลำดับ | รายการตรวจสอบ | คำสั่งทดสอบ | ผลลัพธ์ที่คาดหวัง / สิ่งที่ต้องจับตา | ผลการตรวจจริง (Baseline Status) |
| :--- | :--- | :--- | :--- | :--- |
| **V1** | **Unit & Logic Tests** | `pytest tests/test_smoke.py tests/test_dfd_flows.py tests/test_analytics_units.py` | ต้องผ่าน 100% (เพราะ Logic Backend ไม่ควรถูกกระทบ) | ✅ **PASSED (46/46)** ใน 24.97s |
| **V2** | **E2E Quotation Test** | `pytest tests/e2e/test_quotation_form_e2e.py` | ตรวจสอบว่า Playwright หาช่องกรอกและปุ่มในฟอร์มพบหรือไม่ | ❌ **FAILED (Timeout 20s)** หลุดที่ปุ่ม Login |
| **V3** | **Live Demo Flow Test** | `pytest tests/e2e/test_live_demo_flow.py` | ตรวจสอบ flow การล็อกอินและสลับหน้าเมนู | ✅ **PASSED (7/7)** (ใช้ AppTest จำลอง Session) |
| **V4** | **Interactive Live Demo** | `python scripts/live_browser_demo.py -s --scenario standard` | สังเกตการคลิกจริงบนเบราว์เซอร์ ว่ามีจังหวะปุ่มหลุดหรือไม่ | ⚠️ **FAILING RISK** (โค้ดบรรทัด 106 หา text เก่า) |
| **V5** | **Evidence Capture Script** | `python tests/e2e/capture_manual_evidence.py` | ตรวจสอบว่าสามารถแคปภาพหน้าจอครบทั้ง 27 รูปโดยไม่ติด timeout | ❌ **FAILING RISK** (โค้ดบรรทัด 58 หา text เก่า) |

---

## 📊 บันทึกรายละเอียดผลการตรวจสอบจริง (Verification Findings Log)

### 1. ผลลัพธ์การรัน V1: Unit & Logic Tests (สมบูรณ์ 100%)
* **คำสั่ง:** `.venv\Scripts\pytest.exe tests/test_smoke.py tests/test_dfd_flows.py tests/test_analytics_units.py -v`
* **ผลลัพธ์:** ผ่านครบทั้ง 46 รายการ (46 passed in 24.97s)
  * `test_smoke.py`: ตรวจสอบ RBAC role permission ทั้ง 8 หน้า ผ่านทั้งหมด
  * `test_dfd_flows.py`: ตรวจสอบ Business Logic & Database operations Process 1.1 - 5.3 ผ่านทั้งหมด
  * `test_analytics_units.py`: ตรวจสอบ Machine Learning models (RFM, Churn, Lead Scoring, ROI) ผ่านทั้งหมด
* **ข้อสรุป:** ยืนยันว่า Backend, Database SQLite 3NF, และ Analytics Module ไม่เสียหายจากการเปลี่ยน UI

### 2. ผลลัพธ์การรัน V2: E2E Quotation Form Test (พบจุดพังจริง)
* **คำสั่ง:** `.venv\Scripts\pytest.exe tests/e2e/test_quotation_form_e2e.py -v`
* **ผลลัพธ์:** ล้มเหลวทันทีที่ขั้นตอนเข้าสู่ระบบ (1 failed in 29.51s)
  * **Error Trace:** `TimeoutError: Locator.click: Timeout 20000ms exceeded. waiting for get_by_role("button", name="เข้าใช้งานเป็น sale1")`
  * **สาเหตุ:** ฟังก์ชัน `login_as()` ใน `tests/e2e/conftest.py` บรรทัดที่ 72 มองหาปุ่มตามข้อความเก่า `"เข้าใช้งานเป็น {username}"` แต่ใน `auth.py` ของ branch `ui-redesign` ปุ่มถูกเปลี่ยนเป็นข้อความ `"เข้าสู่ระบบ"` ภายใต้การ์ดพนักงาน

### 3. ผลลัพธ์การรัน V3: Live Demo Flow AppTest (ผ่านเนื่องจากไม่พึ่ง DOM)
* **คำสั่ง:** `.venv\Scripts\pytest.exe tests/e2e/test_live_demo_flow.py -v`
* **ผลลัพธ์:** ผ่านครบทั้ง 7 ขั้นตอน (7 passed in 6.24s)
  * เพราะชุดเทสนี้ใช้ `streamlit.testing.v1.AppTest` และกำหนด `at.session_state["user"]` โดยตรง จึงไม่ได้รับผลกระทบจาก DOM และ CSS เปลี่ยนแปลง

### 4. การวิเคราะห์ V4 & V5: Script Automation (ดำเนินการแก้ไขแล้ว)
* `tests/e2e/capture_manual_evidence.py` บรรทัดที่ 58:
  ```python
  # ปรับเป็นระบบค้นหาการ์ดตาม data-user หรือชื่อพนักงาน แล้วกดปุ่ม "เข้าสู่ระบบ"
  card = page.locator("[data-testid='stVerticalBlockBorderWrapper']").filter(has=user_marker)
  card.get_by_role("button", name="เข้าสู่ระบบ").first.click()
  ```
* `scripts/live_browser_demo.py` บรรทัดที่ 106:
  ```python
  # รองรับทั้งปุ่มเดิม และการ์ดธีมใหม่แบบไดนามิก พร้อม regex fallback
  ```
* ผลการปรับปรุง: ทั้ง `capture_manual_evidence.py` และ `live_browser_demo.py` ผ่านการทดสอบ 100%

---

## 📸 รายละเอียดการ Capture หน้าจอและการจัดการเอกสาร (Documentation & Evidence Scope)

ตามข้อกำหนดโครงการล่าสุด **ได้ตัดการสร้างไฟล์ Binary (Word, PowerPoint, PDF) ออกจากขอบเขตงานทั้งหมด** เพื่อให้โฟลเดอร์โครงการกระชับและรักษา Markdown (`docs/*.md`) เป็น Source of Truth เพียงชุดเดียว:

* ❌ **ไฟล์ที่ยกเลิกการสร้างและลบออกจากโปรเจกต์:**
  * `user_manual.docx`, `user_manual.pdf` (ลบสคริปต์ `build_user_manual_docx.py`, `export_manual_pdf.ps1`)
  * `demo.pptx`, `demo.pdf` (ลบสคริปต์ `build_demo_presentation.py`, `export_demo_pdf.ps1`)
  * `Precision_AI_CRM.pptx`, `Precision_AI_CRM.pdf` (ลบสคริปต์ `build_presentation.py`, `export_pdf.ps1`)

* ✅ **เอกสารหลักที่คงไว้เป็น Source of Truth:**
  * 📖 [`docs/user_manual.md`](file:///c:/Users/momo/dev/dddsproject/docs/user_manual.md) (คู่มือการใช้งานระบบฉบับสมบูรณ์ 14 กิจกรรม DFD พร้อมภาพประกอบ)
  * 📸 [`docs/evidence/*.png`](file:///c:/Users/momo/dev/dddsproject/docs/evidence/) (ภาพหน้าจอจริง 27 ภาพในธีม Dark-Orange ที่ผ่านการแคปอัตโนมัติ)
  * 🎬 [`scripts/live_browser_demo.py`](file:///c:/Users/momo/dev/dddsproject/scripts/live_browser_demo.py) (สคริปต์สาธิตระบบสดอัตโนมัติ Standard 7 ขั้นตอน และ Grand Tour 18 ขั้นตอน)

---

## 🎯 บันทึกผลการดำเนินงานแก้ไข (Remediation Execution Log)

### เฟส 1: ปรับปรุง E2E Selectors & Test Fixtures (สำเร็จ ✅)
1. เพิ่ม Attribute `data-user="{r.Username}"` บน Marker การ์ดพนักงานใน [`auth.py`](file:///c:/Users/momo/dev/dddsproject/auth.py)
2. อัปเดต `login_as()` ใน [`tests/e2e/conftest.py`](file:///c:/Users/momo/dev/dddsproject/tests/e2e/conftest.py) ให้ค้นหาการ์ดผ่าน `data-user` และคลิกปุ่ม `"เข้าสู่ระบบ"` โดยมี Regex Fallback
3. **ผลทดสอบ:** `tests/e2e/test_quotation_form_e2e.py` และ `test_dfd_evidence.py` ผ่าน 100% (11 passed)

### เฟส 2: ปรับปรุงสคริปต์สาธิตระบบสด (สำเร็จ ✅)
1. ปรับปรุงฟังก์ชัน `login()` ใน [`scripts/live_browser_demo.py`](file:///c:/Users/momo/dev/dddsproject/scripts/live_browser_demo.py) ให้รองรับ UI การ์ดแบบใหม่
2. เพิ่มระบบจัดการการเข้ารหัส UTF-8 บน Windows Terminal (`sys.stdout.reconfigure`)
3. **ผลทดสอบ:**
   * รัน `scripts/live_browser_demo.py --headless --scenario standard` ผ่านครบ 7 ขั้นตอน (100%)
   * รัน `scripts/live_browser_demo.py --headless --scenario grand` ผ่านครบ 18 ขั้นตอน (100%)

### เฟส 3: Re-capture ภาพหลักฐานสำหรับคู่มือ Markdown (สำเร็จ ✅)
1. รัน `tests/e2e/capture_manual_evidence.py` บันทึกภาพหน้าจอใหม่ครบทั้ง 27 ภาพลงใน `docs/evidence/`
2. ภาพใน [`docs/user_manual.md`](file:///c:/Users/momo/dev/dddsproject/docs/user_manual.md) แสดงผลตรงตามธีม Dark-Orange ใหม่สมบูรณ์ 100%

### เฟส 4: ลบการสร้างไฟล์เอกสาร Binary และสคริปต์ส่วนเกินออกจากโปรเจกต์ (สำเร็จ ✅)
1. ลบสคริปต์ `build_*.py` และ `export_*.ps1` ทั้ง 6 ไฟล์ออกจาก Git
2. ลบไฟล์ `.docx`, `.pptx`, `.pdf` ที่ไม่จำเป็นออกจากโฟลเดอร์ `docs/`

---

## ✅ เกณฑ์การยอมรับงาน (Acceptance Criteria / Definition of Done)

* [x] ชุดการทดสอบ `pytest` (Unit, Smoke, DFD, E2E) ผ่านครบทั้งหมด (Green 100%)
* [x] สคริปต์ `scripts/live_browser_demo.py` รันผ่านฉลุยทั้งแบบ 7 ขั้นตอน และ 18 ขั้นตอน โดยไม่เกิด Selector Timeout
* [x] ภาพในโฟลเดอร์ `docs/evidence/` ทั้ง 27 รูปได้รับการอัปเดตเป็นธีมใหม่อย่างสมบูรณ์
* [x] เอกสารคู่มือผู้ใช้ `docs/user_manual.md` เป็น Source of Truth ฉบับสมบูรณ์
* [x] ลบไฟล์และสคริปต์สร้าง `user_manual.docx/.pdf`, `demo.pptx/.pdf`, `Precision_AI_CRM.pptx/.pdf` ออกจากโปรเจกต์เรียบร้อย
* [x] โค้ดทั้งหมดพร้อมสำหรับ Merge กลับเข้า `ui-redesign` และ `master` อย่างมั่นใจ
