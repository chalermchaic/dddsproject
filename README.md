# 📈 Smart CRM Analytics

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
python bootstrap.py --check      # ตรวจว่าไฟล์สำคัญครบและ import ผ่าน
python bootstrap.py              # แพ็กเป็น .zip สำหรับส่งงาน
```

---

## 🧩 โครงสร้าง

```
app.py                     Streamlit entry point (หน้า Home + KPI)
db/
  schema.sql               DDL ตาม Data Dictionary D1–D5 + Views (V_LEAD_FEATURES ฯลฯ)
  seed_data.py             สร้างฐานข้อมูล + ข้อมูลจำลอง (~600 leads, reproducible seed=42)
  connection.py            helper: get_conn / run_query / execute / next_id / cached_query
analytics/
  lead_scoring.py          งานที่ 1 — จำแนกโอกาสปิดการขาย (LogReg / RandomForest)
  rfm_segmentation.py      งานที่ 2 — RFM + K-Means segmentation
  churn_health.py          งานที่ 3 — Customer Health Score (0–100) + churn risk
  campaign_roi.py          งานที่ 4 — Conversion / CPL / CAC / ROAS / ROI + chi-square
pages/
  1_📢_Marketing.py         Process 1.0 — แคมเปญ + บันทึกผู้สนใจ
  2_📞_Sales_Followup.py    Process 2.0 — คิวงานจัดลำดับด้วย ML + บันทึกกิจกรรม
  3_🧾_Order_Billing.py     Process 3.0 — ใบเสนอราคา + ยืนยันชำระเงิน
  4_👤_Customer_Profile.py  Process 4.0 — โปรไฟล์ลูกค้า + RFM รายบุคคล
  5_🎫_Support_Ticket.py    Process 5.0 — เคสแจ้งปัญหา + บทสนทนา
  6_📊_Analytics_Dashboard.py  แดชบอร์ดรวมผล Data Science ทั้ง 4 งาน
```

---

## 🔬 ทดสอบชั้น analytics แยก (ไม่ต้องเปิดแอป)

```bash
python -m analytics.lead_scoring
python -m analytics.rfm_segmentation
python -m analytics.churn_health
python -m analytics.campaign_roi
# หรือ:  make test
```

## ⚙️ Tech Stack

| ชั้น | เครื่องมือ |
| :--- | :--- |
| Database | SQLite 3 (embedded) — schema พร้อม CHECK constraints + Views สำหรับ analytics |
| Application / UI | Python + Streamlit (multipage) |
| Analytics / ML | pandas, numpy, scikit-learn, scipy |
| Visualization | Plotly |
| Deploy | Docker + docker-compose |
