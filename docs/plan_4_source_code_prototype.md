# 💻 แผนงานและความคืบหน้า: ซอร์สโค้ดฉบับสมบูรณ์ (Source Code & Prototype)

> **วิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
> **โครงงาน:** ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM & Data Science Analytics Platform)  
> **เวอร์ชันปัจจุบัน:** `v1.2.1` (Clean Multi-Page Naming & Streamlit Navigation Native Icons)  
> **กำหนดส่งมอบ (Due Date):** สัปดาห์ที่ 15 (ส่งไฟล์ซอร์สโค้ด / ลิงก์ GitHub ใน Google Classroom)  
> **สถานะปัจจุบัน:** 🟢 **100% (โค้ดระบบ, โมเดล AI, ฐานข้อมูล และแพ็กเกจส่งมอบพัฒนาเสร็จสมบูรณ์แล้ว — แก้ไขบั๊กทั้งหมดพร้อมมี Automated Regression Tests ครบถ้วน ดูหัวข้อ 6)**

---

## 1. สถานะภาพรวม (Overall Progress)

| คอมโพเนนต์หลัก | สถานะ | เปอร์เซ็นต์ | รายละเอียดความพร้อม |
|---|:---:|:---:|---|
| **1. ฐานข้อมูล (Database Layer)** | 🟢 สมบูรณ์ 100% | 100% | 10 ตารางตาม 3NF, SQLite Foreign Keys, Seed Data พร้อมข้อมูลทดลอง |
| **2. โมเดล Data Science (Analytics Engine)** | 🟢 สมบูรณ์ 100% | 100% | โค้ด 4 ฟังก์ชัน (Lead Scoring, RFM, Churn Health, Campaign ROI) |
| **3. หน้าจอเว็บแอปพลิเคชัน (Streamlit UI)** | 🟢 สมบูรณ์ 100% | 100% | ครบ 8 หน้าหลัก (Home, Marketing, Sales, Billing, Customer, Support, Dashboard, Portal) |
| **4. ความปลอดภัยและการเข้าใช้งาน (Auth & RBAC)** | 🟢 สมบูรณ์ 100% | 100% | ระบบ Login แยก 4 สิทธิ์ (Admin, Marketing, Sales, Support) + Portal จำลอง |
| **5. ชุดทดสอบระบบ (Test Automation)** | 🟢 สมบูรณ์ 100% | 100% | Unit Tests, DFD Flow Tests (37 tests) มี Automated Regression Tests คุมบั๊กทั้ง 2 จุด และ Playwright E2E Screenshot |
| **6. คอนเทนเนอร์และติดตั้ง (Container & Setup)** | 🟢 สมบูรณ์ 100% | 100% | มี Dockerfile, docker-compose.yml, Makefile, bootstrap.py (รองรับ Windows UTF-8) |
| **7. การตรวจทานเตรียมส่งมอบ (Packaging)** | 🟢 สมบูรณ์ 100% | 100% | ตรวจสอบไฟล์ขยะ, ปรับ `.gitignore` กันไฟล์ `.zip`, มีคำสั่ง `bootstrap.py` สร้างแพ็กเกจ 1 คลิก |
| **ภาพรวมซอร์สโค้ดทั้งหมด (Overall)** | 🟢 สมบูรณ์สูงสุด | **100%** | **พร้อมใช้งาน รันสาธิต และส่งมอบได้ทันที — ผ่านการทดสอบทั้งหมด 37 รายการ** |

---

## 2. โครงสร้างซอร์สโค้ดและหน้าที่ของแต่ละไฟล์ (Codebase Architecture)

โครงการตั้งอยู่ที่ไดเรกทอรี [c:\Users\momo\dev\dddsproject\\](file:///c:/Users/momo/dev/dddsproject):

```
dddsproject/
├── app.py                      # จุดเริ่มต้นของระบบ (Entry point) และหน้าจัดการ Authentication
├── auth.py                     # ระบบตรวจสอบสิทธิ์พนักงาน (RBAC), st.navigation และการสลับบทบาท
├── bootstrap.py                # สคริปต์ตรวจสอบสภาพแวดล้อมและเตรียมความพร้อมของระบบ
├── VERSION                     # หมายเลขเวอร์ชันของระบบ (ปัจจุบัน 1.2.1)
├── requirements.txt            # รายการไลบรารี Python ที่จำเป็น
├── Dockerfile                  # คอนฟิกการสร้าง Docker Image
├── docker-compose.yml          # คอนฟิกสำหรับรันระบบด้วย Docker Compose
├── Makefile                    # คำสั่งลัดในการติดตั้ง, รัน, และทดสอบ
│
├── db/                         # ชั้นจัดการฐานข้อมูล (Database Layer)
│   ├── schema.sql              # สคริปต์ DDL สร้างตาราง 10 ตาราง และ Foreign Key Constraints
│   ├── connection.py           # ตัวเชื่อมต่อฐานข้อมูล SQLite และฟังก์ชัน Utility (save_upload, etc.)
│   ├── seed_data.py            # ข้อมูลจำลองตั้งต้น (Dummy Data) สำหรับการทดลองครบทุกขั้นตอน
│   └── crm.db                  # ไฟล์ฐานข้อมูล SQLite จริงที่พร้อมใช้งาน
│
├── analytics/                  # ชั้นการวิเคราะห์ข้อมูลและ AI (Analytics Engine Layer)
│   ├── lead_scoring.py         # ฟังก์ชันคำนวณและโมเดลพยากรณ์คะแนนโอกาสปิดการขาย
│   ├── rfm_segmentation.py     # อัลกอริทึมการแบ่งกลุ่มลูกค้าด้วยเทคนิค RFM
│   ├── churn_health.py         # ฟังก์ชันประเมินความเสี่ยงการยกเลิกบริการและสุขภาพลูกค้า
│   └── campaign_roi.py         # ฟังก์ชันคำนวณผลตอบแทนและสถิติประสิทธิภาพแคมเปญ
│
├── pages/                      # ชั้นส่วนต่อประสานผู้ใช้ (User Interface Layer - Streamlit Multi-page)
│   ├── 0_home.py               # หน้าหลัก แนะนำภาพรวมระบบและสถานะเชื่อมต่อฐานข้อมูล
│   ├── 1_marketing.py          # จัดการแคมเปญ, โปรโมชัน, และลงทะเบียนผู้สนใจ (Process 1.0)
│   ├── 2_sales_followup.py     # ติดตามผู้สนใจ, คิวงาน AI Lead Scoring, ออกใบเสนอราคา (Process 2.0)
│   ├── 3_order_billing.py      # ตรวจคำสั่งซื้อ, ตรวจสอบสลิปโอนเงิน, ออกใบเสร็จ (Process 3.0)
│   ├── 4_customer_profile.py   # ทะเบียนประวัติลูกค้าทางการ และประวัติการสั่งซื้อ (Process 4.0)
│   ├── 5_support_ticket.py     # เปิดเคสแจ้งปัญหา, บันทึกการแก้ไข, บันทึกคะแนนบริการ (Process 4.0)
│   ├── 6_analytics_dashboard.py# แดชบอร์ดสรุปผล Data Science 4 ด้าน และรายงานยอดขาย (Process 5.0)
│   └── 9_portal.py             # หน้าพอร์ทัลจำลองสำหรับผู้สนใจและลูกค้าภายนอก (Customer Portal)
│
├── tests/                      # ชุดทดสอบอัตโนมัติ (Automated Test Suite)
│   ├── conftest.py             # Fixtures สำหรับจำลองสภาพแวดล้อมฐานข้อมูลในหน่วยความจำ
│   ├── test_smoke.py           # Smoke test ตรวจสอบการ import โมดูล และความครบถ้วนของสคริปต์
│   ├── test_dfd_flows.py       # ตรวจสอบความถูกต้องของเส้นทางการไหลข้อมูลตาม DFD
│   └── e2e/
│       ├── test_dfd_evidence.py# ทดสอบผ่านเว็บจริง (Playwright) และจับภาพหน้าจอหลักฐาน 12 รูป
│       └── build_report.py     # ประกอบเอกสารสรุปผลการทดสอบอัตโนมัติ
│
└── docs/                       # เอกสารคู่มือ, แผนงาน และหลักฐานภาพ
    ├── PLAN-dfd-full-coverage.md
    ├── analytics_4_features_full_guide.md
    ├── feature1_lead_scoring_deep_dive.md ถึง feature4...
    └── evidence/ (ภาพแคปเจอร์ 12 ภาพ)
```

---

## 3. สิ่งที่ทำเสร็จแล้วใน v1.2.0 (Completed Milestones)

1. **ครอบคลุม 14 กิจกรรมย่อยตาม DFD แบบ 100%:**
   - ปิดช่องว่างกระบวนการ 1.3 (ส่งข้อมูลโปรโมชัน), 2.1 (คิวติดตามประจำวันตามกำหนด), 3.1–3.3 (แยกตรวจคำสั่งซื้อ/ตรวจสลิป/ออกใบเสร็จ), 4.3 (ประเมินคะแนนบริการ), 5.2 (รายงานสรุปยอดขาย)
2. **สร้างหน้าพอร์ทัลจำลองสำหรับลูกค้า (`pages/9_🌐_Portal.py`):**
   - ให้สวมบทบาทเป็น "ผู้สนใจ" และ "ลูกค้า" ส่งข้อมูลคำสั่งซื้อ, สลิปโอนเงิน และแจ้งปัญหาเข้ามาในระบบได้จริง
3. **ระบบสิทธิ์การเข้าใช้งาน (Role-based Authentication):**
   - มีตาราง `EMPLOYEE` และคัดกรองการเข้าถึงหน้าจอตามหน้าที่อย่างปลอดภัย
4. **ชุดทดสอบผ่านหมด 100%:**
   - ทดสอบครอบคลุมทั้ง Unit Logic, Data Flow Integrity และ End-to-End Visual Verification

---

## 4. แผนงานขั้นตอนสุดท้ายก่อนส่งมอบ (Pre-Submission Action Plan)

| วันที่ | งานที่ต้องทำ | ผลลัพธ์ |
|---|---|---|
| **20 – 25 ก.ย. 69** | ตรวจสอบ Clean Code ลบไฟล์ชั่วคราว (`__pycache__`, ไฟล์ log) และจัดระเบียบ `.gitignore` | โค้ดสะอาดได้มาตรฐาน |
| **26 – 30 ก.ย. 69** | ตรวจสอบไฟล์ `seed_data.py` ให้มีข้อมูลครอบคลุมกรณีทดสอบที่น่าประทับใจสำหรับวันนำเสนอ | ฐานข้อมูลทดสอบพร้อมโชว์ |
| **1 – 4 ต.ค. 69** | ทดสอบรันคำสั่ง `python bootstrap.py` บนเครื่องเปล่า (Clean environment) เพื่อยืนยันว่าอาจารย์หรือเพื่อนร่วมชั้นสามารถรันได้ทันทีโดยไม่ติดขัด | ติดตั้งง่ายใน 1 คลิก |
| **5 – 7 ต.ค. 69** | บีบอัดไฟล์ซอร์สโค้ดเป็น `.zip` และอัปเดตเวอร์ชันล่าสุดขึ้น GitHub Repository | แพ็กเกจโค้ดพร้อมส่ง |
| **8 / 11 ต.ค. 69** | 🚨 **แนบลิงก์ GitHub และส่งไฟล์ .zip ใน Google Classroom** | ส่งมอบงานเรียบร้อย |

---

## 5. คลังวัตถุดิบอ้างอิงและคำสั่งรันระบบ (Quick Start & Commands)

### 🚀 คำสั่งสำหรับรันระบบและทดสอบ
* **การติดตั้งและเปิดโปรแกรม:**
  ```powershell
  cd c:\Users\momo\dev\dddsproject
  pip install -r requirements.txt
  streamlit run app.py
  ```
* **การรีเซ็ตฐานข้อมูลและใส่ Seed Data ใหม่:**
  ```powershell
  python -c "from db.connection import reset_database; reset_database()"
  ```
* **การรันการตรวจสอบระบบ (Bootstrap Check):**
  ```powershell
  python bootstrap.py
  ```
* **การรันด้วย Docker:**
  ```powershell
  docker-compose up --build
  ```

### 📌 ลิงก์ไฟล์ซอร์สโค้ดสำคัญ
* สคริปต์ฐานข้อมูล: [schema.sql](file:///c:/Users/momo/dev/dddsproject/db/schema.sql) | [seed_data.py](file:///c:/Users/momo/dev/dddsproject/db/seed_data.py)
* ตัววิเคราะห์ Data Science: [lead_scoring.py](file:///c:/Users/momo/dev/dddsproject/analytics/lead_scoring.py) | [rfm_segmentation.py](file:///c:/Users/momo/dev/dddsproject/analytics/rfm_segmentation.py) | [churn_health.py](file:///c:/Users/momo/dev/dddsproject/analytics/churn_health.py) | [campaign_roi.py](file:///c:/Users/momo/dev/dddsproject/analytics/campaign_roi.py)
* หน้าเว็บแอปพลิเคชัน: [app.py](file:///c:/Users/momo/dev/dddsproject/app.py) | [auth.py](file:///c:/Users/momo/dev/dddsproject/auth.py) | โฟลเดอร์ [pages/](file:///c:/Users/momo/dev/dddsproject/pages)

---

## 6. บั๊กที่ต้องแก้ไข (Known Issues — ส่งให้ทีมแก้ก่อนส่งมอบ)

พบระหว่างเตรียมภาพหลักฐานสำหรับคู่มือ (`plan_2`) และเตรียมข้อมูล Demo (`plan_5`) — ไม่ได้มาจาก test suite ที่มีอยู่ (แนะนำเพิ่ม regression test คุม 2 จุดนี้ด้วย):

### ✅ [แก้แล้ว] `pages/1_marketing.py` — หน้าแครชเวลาโหลดแท็บ "แคมเปญทั้งหมด"
* **อาการ:** `TypeError: boolean value of NA is ambiguous` ทั้งหน้าแครช แม้กำลังใช้งานแท็บอื่นอยู่ (เพราะ Streamlit รันโค้ดทุกแท็บซ้ำทุกครั้งที่มีการโต้ตอบ ไม่ใช่แค่แท็บที่เปิดอยู่)
* **สาเหตุ:** บรรทัด ~44-46 `px.scatter(df, ..., size="ปิดได้", ...)` พังเมื่อคอลัมน์ `ปิดได้` มีค่า `pd.NA` จาก `SUM(CASE...)` บน `LEFT JOIN` ที่บางแคมเปญไม่มีผู้สนใจเลย
* **แก้แล้วโดยเพื่อน:** เพิ่ม `COALESCE(SUM(...), 0)` ใน SQL และ `.fillna(0).astype(int)` ก่อนส่งเข้า `px.scatter` — ตรวจสอบซ้ำแล้วใช้งานได้ถูกต้อง (ดู `plan_2_user_manual.md` หมวดที่ 5)

### ✅ [แก้แล้ว] `db/schema.sql` — View `V_SERVICE_HEALTH` นับ `Critical_Tickets` ซ้ำ (Fan-out Bug)
* **อาการเดิม:** ลูกค้าที่มีเคสวิกฤตจริงแค่ 4 เคส ระบบคำนวณออกมาเป็น 41 (คูณเกินจริงตามจำนวน Message สนทนา)
* **สาเหตุ:** View เดิม `JOIN` ตาราง `TICKET` เข้ากับ `TICKET_MESSAGE` ในคำสั่งเดียว ทำให้แถวของ `TICKET` เกิด fan-out ทวีคูณตามจำนวนข้อความสนทนาก่อนคำนวณ Aggregate
* **การแก้ไข:** ปรับปรุง View ใน [schema.sql](file:///c:/Users/momo/dev/dddsproject/db/schema.sql) โดยแยก Subquery Aggregate ระหว่างตั๋วและข้อความสนทนาก่อน `LEFT JOIN` เข้ากับ `CUSTOMER`:
  ```sql
  CREATE VIEW V_SERVICE_HEALTH AS
  SELECT  cu.Customer_ID,
          COALESCE(tk.Ticket_Count, 0)     AS Ticket_Count,
          COALESCE(tk.Critical_Tickets, 0) AS Critical_Tickets,
          tk.Avg_Resolution_Days,
          COALESCE(msg.Total_Messages, 0)  AS Total_Messages
  FROM CUSTOMER cu
  LEFT JOIN (
      SELECT Customer_ID,
             COUNT(*) AS Ticket_Count,
             SUM(CASE WHEN Problem_Category IN ('ระบบขัดข้อง','สินค้าชำรุด') THEN 1 ELSE 0 END) AS Critical_Tickets,
             AVG(julianday(Closed_At) - julianday(Created_At)) AS Avg_Resolution_Days
      FROM TICKET
      GROUP BY Customer_ID
  ) tk  ON tk.Customer_ID = cu.Customer_ID
  LEFT JOIN (
      SELECT t.Customer_ID, COUNT(m.Message_ID) AS Total_Messages
      FROM TICKET t JOIN TICKET_MESSAGE m ON m.Ticket_ID = t.Ticket_ID
      GROUP BY t.Customer_ID
  ) msg ON msg.Customer_ID = cu.Customer_ID;
  ```
* **ผลการตรวจสอบและ Regression Test:**
  - รันตรวจสอบตรงกับลูกค้า `CU0214` ได้ `Critical_Tickets = 4` ถูกต้องตรงกับความเป็นจริง (จากเดิม 41)
  - เพิ่ม Automated Regression Test `test_5_3_service_health_view_no_fanout` ใน [tests/test_dfd_flows.py](file:///c:/Users/momo/dev/dddsproject/tests/test_dfd_flows.py) ยืนยันว่าทุก Customer ID มีค่า `Ticket_Count`, `Critical_Tickets`, และ `Total_Messages` ตรงกับตารางต้นทาง 100%
  - รัน `pytest tests/` ผ่านครบทั้ง 37 รายการ

