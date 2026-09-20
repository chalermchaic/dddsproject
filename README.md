# 📈 Smart CRM Analytics

**เวอร์ชัน 1.2.1** — ดูเลขล่าสุดที่ไฟล์ [`VERSION`](VERSION)

- `1.2.1` — ปรับมาตรฐานชื่อไฟล์หน้าจอและ URL (ASCII snake_case + clean url_path) + เพิ่ม Unit Tests สูตรโมเดล Data Science ครบ 4 งาน + Real UI Playwright E2E ฟอร์มใบเสนอราคา (Process 2.3) + B-Tree Index Benchmark
- `1.2.0` — ครอบคลุมกิจกรรม DFD ครบ 14 (Process 3.1/3.2/3.3 แยกขั้น, To-Do 2.1,
  ส่งโปรโมชัน 1.3, ประเมินผลบริการ 4.3, รายงานสรุปยอดขาย 5.2) + หน้า **Portal**
  จำลองผู้สนใจ/ลูกค้า + ชุดทดสอบ pytest/Playwright
- `1.1.0` — เพิ่มตาราง `EMPLOYEE` + FK และระบบเข้าใช้งานแยกตาม role
- `1.0.0` — ระบบ CRM + Data Science 4 งาน พร้อม Streamlit UI / Docker

ต้นแบบระบบบริหารความสัมพันธ์ลูกค้า (CRM) ครบวงจร ตั้งแต่งานการตลาด → ติดตามการขาย →
ออกใบเสนอราคา → ดูแลลูกค้า → งานบริการหลังการขาย พร้อมชั้นวิเคราะห์ข้อมูลด้วย
Machine Learning 4 งาน

สร้างด้วย **Python + Streamlit + SQLite + scikit-learn** — รันได้ทั้งแบบ local และ **Docker**

โครงงานรายวิชา 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (DDDS) — Assignment 2
อ้างอิง `DDDS_Project_Proposal.md` และ `data-dictionary.txt` (Data Store D1–D5)

---

## 🚀 เริ่มใช้งาน

> ฐานข้อมูล `db/crm.db` ไม่ได้ถูก commit เข้า repo (ถูก gitignore) — ต้อง **seed ก่อนรันครั้งแรก**

### วิธีที่ 1 — Docker (แนะนำ)

```bash
docker compose up --build
```

ครั้งแรก container จะสร้าง `db/crm.db` + ข้อมูลจำลองให้อัตโนมัติ แล้วเปิดที่ http://localhost:8501
ข้อมูลถูกเก็บถาวรผ่าน volume `./db` — ครั้งถัดไปจะไม่ seed ซ้ำ
ถ้าต้องการ seed ใหม่ ให้ลบ `db/crm.db` แล้ว `docker compose up` อีกครั้ง

### วิธีที่ 2 — Local (Python 3.11+)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt

python db/seed_data.py           # สร้าง db/crm.db + mockup data (รันจาก repo root)
streamlit run app.py
```

> **Windows:** ถ้า `python db/seed_data.py` พิมพ์ผลลัพธ์แล้วเจอ `UnicodeEncodeError`
> ให้ตั้งค่า `set PYTHONUTF8=1` (cmd) หรือ `$env:PYTHONUTF8=1` (PowerShell) ก่อนรัน

### ตรวจความพร้อมของโปรเจกต์

```bash
python bootstrap.py --check      # ตรวจว่าไฟล์สำคัญครบ / import ผ่าน / ตารางครบ
python bootstrap.py              # แพ็กเป็น .zip สำหรับส่งงาน
```

---

## 🔐 การเข้าใช้งานตาม Role

เปิดแอปแล้วจะเจอหน้า **เลือกบัญชีผู้ใช้** ก่อน (prototype สาธิต — ไม่มีรหัสผ่าน)
แต่ละบัญชีเป็น 1 แถวในตาราง `EMPLOYEE` และ `Role` กำหนดว่าเห็นเมนูหน้าไหน:

| หน้า | admin | marketing | sales | support |
| :--- | :---: | :---: | :---: | :---: |
| 🏠 ภาพรวม | ✓ | ✓ | ✓ | ✓ |
| 📢 งานการตลาด | ✓ | ✓ | | |
| 📞 ติดตามการขาย | ✓ | | ✓ | |
| 🧾 ใบเสนอราคา/ชำระเงิน | ✓ | | ✓ | |
| 👤 ข้อมูลลูกค้า | ✓ | ✓ | ✓ | ✓ |
| 🎫 รับแจ้งปัญหา | ✓ | | | ✓ |
| 📊 แดชบอร์ดวิเคราะห์ | ✓ | ✓ | ✓ | ✓ |

**บัญชี demo** (สร้างโดย `db/seed_data.py`): `admin1` · `marketing1` `marketing2` ·
`sale1` `sale2` `sale3` `sale4` · `cs1` `cs2` `cs3`

เมื่อล็อกอินแล้ว การบันทึกงาน (สร้างแคมเปญ / บันทึกกิจกรรม / ออกใบเสนอราคา / รับเคส)
จะผูก `Employee_ID` ของผู้ใช้ที่ล็อกอินให้อัตโนมัติ

นอกจากนี้มีปุ่ม **🌐 เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)** บนหน้า login → เปิดหน้า **Portal**
สำหรับทดลอง flow ที่ external entity ส่งข้อมูลเข้าระบบตาม DFD
(ลงทะเบียนเอง, ยืนยันคำสั่งซื้อ, อัปโหลดสลิป, แจ้งปัญหา, ให้คะแนนบริการ)

---

## ✅ ครอบคลุมกิจกรรม DFD ครบ 14 (v1.2.1)

| Process | กิจกรรม | ทดลองที่ |
| :--- | :--- | :--- |
| 1.1 / 1.2 | รับข้อมูลแคมเปญ · ลงทะเบียนผู้สนใจ | 📢 งานการตลาด + 🌐 Portal |
| 1.3 | ส่งรายละเอียดโปรโมชันให้ผู้สนใจ | 📞 ติดตามการขาย |
| 2.1 | คิวติดตามประจำวัน (To-Do) | 📞 แท็บ "คิวติดตามวันนี้" |
| 2.2 / 2.3 | บันทึกกิจกรรม · ออกใบเสนอราคา | 📞 · 🧾 |
| 3.1 / 3.2 / 3.3 | ตรวจคำสั่งซื้อ · ตรวจสลิป · ออกใบเสร็จ+บันทึกลูกค้า | 🧾 (Portal ส่งคำสั่งซื้อ/สลิป) |
| 4.1 / 4.2 / 4.3 | รับแจ้ง · แก้ไข · แจ้งผล+ประเมิน | 🎫 (Portal แจ้ง/ให้คะแนน) |
| 5.1 / 5.2 | รายงานแคมเปญ · รายงานสรุปยอดขาย | 📊 แดชบอร์ด แท็บ 4 / 5 |

---

## 🧪 การทดสอบระบบ (Testing & Quality Assurance)

ระบบได้รับการทดสอบครอบคลุมแบบหลายระดับ (Multi-layer Testing) รวมทั้งหมดมากกว่า 54 กรณีทดสอบ เพื่อรับประกันความถูกต้องของตรรกะ Machine Learning, โฟลว์การทำงานตาม Data Flow Diagram (DFD) ทุกกระบวนการ, การควบคุมสิทธิ์ (RBAC), และประสิทธิภาพของฐานข้อมูล

### 1. ติดตั้งเครื่องมือทดสอบ (ครั้งแรก)

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium   # จำเป็นสำหรับชุดทดสอบ Real UI E2E
```

### 2. วัตถุประสงค์และคำสั่งรันแต่ละชุดทดสอบ

| ชุดทดสอบ | ไฟล์ที่ใช้ | วัตถุประสงค์ (ใช้ทำอะไร) | คำสั่งรัน |
|---|---|---|---|
| **Data Science Unit Tests** | `tests/test_analytics_units.py` | ตรวจสอบความถูกต้องของสูตรคำนวณและ edge cases ของโมเดลทั้ง 4 ตัว (RFM Quintiles, Customer Health Weights 100%, Lead Thresholds Hot/Warm/Cold, Chi-square p-value & ROI) โดยไม่ต้องพึ่งพาฐานข้อมูล | `pytest tests/test_analytics_units.py -v` |
| **DFD Process Flows** | `tests/test_dfd_flows.py` | จำลองการทำงานตาม Data Flow Diagram ครบทุกกิจกรรม (Process 1.0 – 5.0) ผ่าน `AppTest` และ assert การเปลี่ยนแปลงในฐานข้อมูล SQLite จริง | `pytest tests/test_dfd_flows.py -v` |
| **Live Demo Storyline** | `tests/test_demo_flow.py` | ทดสอบ Flow การสาธิตระบบสดครบ 7 ขั้นตอน (10 นาที) ตั้งแต่ลงทะเบียน, ติดตาม, ออกใบเสนอราคา, แนบสลิป, ออกใบเสร็จ, รับเรื่องปัญหา, จนถึงแดชบอร์ด | `pytest tests/test_demo_flow.py -v` |
| **RBAC Security & Smoke** | `tests/test_smoke.py` | ตรวจสอบสิทธิ์การเข้าถึงเมนูและหน้าเพจตาม Role (Admin, Marketing, Sales, Support, Guest) ทุกคู่หน้า ป้องกันการเข้าถึงหน้าที่ไม่อนุญาต | `pytest tests/test_smoke.py -v` |
| **Playwright Real UI E2E** | `tests/e2e/test_quotation_form_e2e.py` | ขับเบราว์เซอร์ Chromium จริงเพื่อทดสอบฟอร์มออกใบเสนอราคา (Process 2.3) เลือกสินค้าแบบ multiselect, ตรวจสอบการคำนวณส่วนลดอัตโนมัติบนหน้าจอ, และยืนยันการบันทึกสถานะ `ออกใบเสนอราคาแล้ว` ลงตาราง `SALE` | `pytest tests/e2e/test_quotation_form_e2e.py -v` |
| **Index & Query Benchmark** | `scripts/benchmark_index_usage.py` | รัน `EXPLAIN QUERY PLAN` วิเคราะห์การทำงานของ B-Tree Index บน 7 Query หลักของระบบ และสรุปรายงานที่ `docs/INDEX_QUERY_PLAN_REPORT.md` | `python scripts/benchmark_index_usage.py` |

### 3. รันการสาธิตระบบสดผ่านเบราว์เซอร์จริง (Real UI Live Demo)

สคริปต์อัตโนมัติสำหรับเปิดเบราว์เซอร์ Chromium จริงบนหน้าจอ แสดงการทำงานแบบก้าวหน้าทีละขั้นตอน (Slow-Mo) พร้อมคำบรรยาย Floating HUD Subtitle บนหัวเว็บ ครอบคลุมทั้ง 3 เคสธุรกิจ 7 ขั้นตอน (DFD Process 1.0 - 5.0, D1 - D5):

* **โหมดสั่ง Next ทีละสเต็ป (Interactive Step-by-Step — แนะนำสำหรับการนำเสนอสด):**
  ```bash
  python scripts/live_browser_demo.py --step
  ```
  *(ระบบจะหยุดรอให้ผู้กด `[Enter]` ใน Terminal ก่อนเริ่มดำเนินการในแต่ละขั้นตอน พร้อมแสดงบทพูดแนะนำสำหรับบรรยายให้อาจารย์ฟัง)*

* **โหมดเล่นสดอัตโนมัติต่อเนื่อง (Auto Play Mode):**
  ```bash
  python scripts/live_browser_demo.py
  # ปรับความเร็วได้ตามต้องการ เช่น:
  python scripts/live_browser_demo.py --slow-mo 800 --pause 1.0
  ```

### 4. รันชุดทดสอบทั้งหมด (Quick Commands)

* **รันชุดทดสอบมาตรฐานทั้งหมด (53 เทสต์ — เร็ว ไม่เปิดเบราว์เซอร์):**
  ```bash
  pytest tests/ -v
  # หรือใช้ Makefile:
  make test
  ```

* **รันชุดทดสอบ E2E ทั้งหมดผ่าน Playwright เบราว์เซอร์จริง:**
  ```bash
  pytest tests/e2e -q --browser chromium
  # หรือใช้ Makefile:
  make e2e
  ```

* **บันทึกภาพหน้าจอหลักฐานการทำงานจริงอัตโนมัติ (Visual Evidence Capture):**
  ```bash
  python tests/e2e/capture_manual_evidence.py
  python tests/e2e/build_report.py
  # หรือใช้ Makefile:
  make evidence
  ```
  *(ผลลัพธ์จะถูกบันทึกเป็นรูปภาพใน `docs/evidence/*.png` และสร้างเอกสาร `docs/evidence/README.md`)*

### 5. ทดสอบรันและดูผลลัพธ์ชั้น Analytics เดี่ยวๆ (ไม่ต้องเปิดแอป)

```bash
python -m analytics.lead_scoring          # ทดสอบเทรน Random Forest & Logistic Regression
python -m analytics.rfm_segmentation      # ทดสอบคำนวณ RFM Quintiles & K-Means
python -m analytics.churn_health          # ทดสอบคำนวณ Health Score & Churn Probability
python -m analytics.campaign_roi          # ทดสอบคำนวณ Funnel, ROI & Chi-square
# หรือรันรวม: make analytics
```

---

## 🧩 โครงสร้างโปรเจกต์

```
app.py                     entry point / router — หน้า login + st.navigation ตาม role
auth.py                    login/session/role → เมนูที่มองเห็น
db/
  schema.sql               DDL ตาม Data Dictionary (10 entities รวม EMPLOYEE) + Views
  seed_data.py             สร้างฐานข้อมูล + ข้อมูลจำลอง (~600 leads, reproducible seed=42)
  connection.py            helper: get_conn / run_query / execute / next_id / cached_query
analytics/
  lead_scoring.py          งานที่ 1 — จำแนกโอกาสปิดการขาย (LogReg / RandomForest)
  rfm_segmentation.py      งานที่ 2 — RFM + K-Means segmentation
  churn_health.py          งานที่ 3 — Customer Health Score (0–100) + churn risk
  campaign_roi.py          งานที่ 4 — Conversion / CPL / CAC / ROAS / ROI + chi-square
pages/
  0_home.py                ภาพรวม + KPI (หน้าแรกหลังล็อกอิน)
  1_marketing.py           Process 1.0 — แคมเปญ + บันทึกผู้สนใจ
  2_sales_followup.py      Process 2.0 — คิวงานจัดลำดับด้วย ML + บันทึกกิจกรรม
  3_order_billing.py       Process 3.0 — ใบเสนอราคา + ยืนยันชำระเงิน
  4_customer_profile.py    Process 4.0 — โปรไฟล์ลูกค้า + RFM รายบุคคล
  5_support_ticket.py      Process 5.0 — เคสแจ้งปัญหา + บทสนทนา
  6_analytics_dashboard.py แดชบอร์ดรวมผล Data Science ทั้ง 4 งาน
  9_portal.py              Portal จำลองสำหรับผู้สนใจและลูกค้า (External Entity)
tests/
  test_analytics_units.py  Unit test สูตรคำนวณ DS ทั้ง 4 โมเดล (9 tests)
  test_dfd_flows.py        DFD flow ครบ Process 1.0 – 5.0 ผ่าน AppTest (16 tests)
  test_demo_flow.py        Live Demo Storyline 7 ขั้นตอน (7 tests)
  test_smoke.py            Smoke test & RBAC ทุกบทบาท (21 tests)
  e2e/                     Playwright E2E เบราว์เซอร์จริง (Quotation form + Screenshots)
scripts/
  benchmark_index_usage.py สคริปต์รัน EXPLAIN QUERY PLAN ทดสอบ Index
```

---

## 📚 คู่มือวิศวกรรมข้อมูลและการวิเคราะห์ (0% – 100%)

- [📘 คู่มือรวม 4 Features หลัก (Overview)](docs/analytics_4_features_full_guide.md)
- [🎯 Feature 1: Lead Scoring Deep Dive](docs/feature1_lead_scoring_deep_dive.md)
- [📊 Feature 2: Customer RFM Segmentation & K-Means Deep Dive](docs/feature2_rfm_segmentation_deep_dive.md)
- [🩺 Feature 3: Customer Health Score & Churn Risk Deep Dive](docs/feature3_churn_health_score_deep_dive.md)
- [💰 Feature 4: Campaign Performance & Marketing ROI Deep Dive](docs/feature4_campaign_roi_deep_dive.md)
- [🧪 แผนและรายงานผลการทดสอบเพิ่มเติม (Additional Test Coverage Plan)](docs/TEST_PLAN_additional_coverage.md)
- [⚡ รายงานผลการทดสอบ Query Plan และ Index Benchmark](docs/INDEX_QUERY_PLAN_REPORT.md)
- [📸 หลักฐานภาพหน้าจอการทำงานจริงตาม DFD ครบทุกขั้นตอน](docs/evidence/README.md)

---

## ⚙️ Tech Stack

| ชั้น | เครื่องมือ |
| :--- | :--- |
| Database | SQLite 3 (embedded) — schema พร้อม CHECK constraints + Views สำหรับ analytics |
| Application / UI | Python + Streamlit (multipage) |
| Analytics / ML | pandas, numpy, scikit-learn, scipy |
| Visualization | Plotly |
| Deploy | Docker + docker-compose |
