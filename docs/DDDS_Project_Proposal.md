# ข้อเสนอโครงงาน: ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะด้วยการวิเคราะห์ข้อมูล
## (Smart CRM & Data Science Analytics Platform)
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**ภาคเรียนที่:** 1 ปีการศึกษา 2569 | **งานมอบหมาย:** Assignment 2 (Database Design for Data Science Project)

---

## 1. ข้อมูลภาพรวมโครงงาน (Project Overview)

### 1.1 ความเป็นมาและความสำคัญ
ระบบบริหารจัดการความสัมพันธ์ลูกค้า (Customer Relationship Management: CRM) เป็นหัวใจสำคัญในการขับเคลื่อนธุรกิจยุคดิจิทัล โครงงานนี้ต่อยอดจากการวิเคราะห์และออกแบบระบบเชิงแนวคิด (DFD 5 กระบวนการหลัก, ER Diagram ตามมาตรฐาน Peter Chen Model และ Data Dictionary) มาสู่การพัฒนาต้นแบบแอปพลิเคชัน (Prototype Application) ที่บูรณาการการออกแบบฐานข้อมูลเชิงสัมพันธ์เข้ากับการประยุกต์ใช้วิทยาศาสตร์ข้อมูล (Data Science) เพื่อช่วยสนับสนุนการตัดสินใจของฝ่ายการตลาด ฝ่ายขาย และฝ่ายบริการลูกค้า

### 1.2 วัตถุประสงค์
1. เพื่อพัฒนาระบบฐานข้อมูลเชิงสัมพันธ์ที่สอดคล้องกับพจนานุกรมข้อมูล (Data Dictionary D1–D5) และโครงสร้าง ER Diagram
2. เพื่อพัฒนา Web Application Prototype สำหรับจำลองกระบวนการทำงานของระบบ CRM ครบทั้ง 5 โมดูล
3. เพื่อประยุกต์ใช้เทคนิค Data Science และ Machine Learning ในการวิเคราะห์พฤติกรรมลูกค้า พยากรณ์โอกาสการขาย และประเมินผลตอบแทนทางธุรกิจ

### 1.3 จุดเน้นในการออกแบบโครงงาน (Focus Areas)
* **หลัก:** `Data Science / ML / AI` (การวิเคราะห์พยากรณ์และจัดกลุ่มข้อมูลลูกค้า)
* **ร่วม:** `Database Architecture / Database Design` (การออกแบบสถาปัตยกรรมฐานข้อมูลเชิงสัมพันธ์)
* **เสริม:** `Cloud Technology / Web Service` (การจำลองและปรับใช้งานผ่าน Streamlit Platform)

---

## 2. ขอบเขตระบบงานและสถาปัตยกรรม (System Scope & Architecture)

### 2.1 โมดูลการทำงานตามกระบวนการหลัก (5 Core Processes ตาม DFD Level 0)
1. **Process 1.0 (Lead Intake & Management):** จัดการแคมเปญการตลาด (D5) บันทึกข้อมูลผู้สนใจ (D1) ทั้งจากฟอร์มและ Portal พร้อมส่งโปรโมชัน
2. **Process 2.0 (Sales Qualification & Follow-up):** จัดคิว To-Do ประจำวัน บันทึกกิจกรรมการติดตาม (D1) และจัดทำใบเสนอราคา (D2)
3. **Process 3.0 (Deal Closing & Payment Processing):** ตรวจสอบคำสั่งซื้อ ตรวจสอบหลักฐานสลิปโอนเงิน ออกใบเสร็จ และขึ้นทะเบียนประวัติลูกค้าทางการ (D3)
4. **Process 4.0 (Customer Support & Service Management):** รับแจ้งปัญหา (D4) ประสานงานแก้ไข แจ้งผลบริการ และรับการประเมินความพึงพอใจ (CSAT)
5. **Process 5.0 (Reporting & Analytics):** สรุปรายงานประสิทธิภาพแคมเปญให้ฝ่ายการตลาด และรายงานสรุปยอดขายให้ฝ่ายขาย

### 2.2 สถาปัตยกรรมทางเทคนิค (Tech Stack)
* **Database Layer:** SQLite (สำหรับการพัฒนาและสาธิตแบบ Embedded) / PostgreSQL (Cloud-ready)
* **Application & UI Layer:** Python + **Streamlit Web Application**
* **Analytics Layer:** Pandas, NumPy, Scikit-learn (ML Modeling), Plotly / Altair (Data Visualization)

---

## 3. การประยุกต์ใช้งานด้าน Data Science 4 งานหลักจากฐานข้อมูล CRM

โครงสร้างตารางและแอตทริบิวต์ในพจนานุกรมข้อมูล (Data Dictionary) รองรับการนำไปประมวลผลทางวิทยาศาสตร์ข้อมูลได้ทันที 4 ด้าน ดังนี้:

```
+-----------------------------------------------------------------------------------+
|                            CRM DATABASE (OLTP)                                    |
|   [LEAD] <-> [LEAD_ACTIVITY] <-> [CAMPAIGN] <-> [SALE] <-> [CUSTOMER] <-> [TICKET] |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        DATA SCIENCE & ANALYTICS PIPELINE                          |
|  1. Lead Scoring Model       : ทำนายโอกาสปิดการขาย (Supervised Classification)      |
|  2. RFM Segmentation         : แบ่งกลุ่มพฤติกรรมลูกค้า (Clustering / Rule-based)    |
|  3. Churn & Service Health   : วิเคราะห์ความเสี่ยงลูกค้าเลิกใช้บริการ                |
|  4. Campaign ROI Analytics   : วิเคราะห์ผลตอบแทนการลงทุนแคมเปญการตลาด              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        STREAMLIT INTERACTIVE DASHBOARD                            |
|       (หน้าจอจำลองการทำงาน 5 Process + แสดงผลโมเดลและกราฟวิเคราะห์ข้อมูล)         |
+-----------------------------------------------------------------------------------+
```

### 🎯 งานที่ 1: โมเดล Lead Scoring (พยากรณ์โอกาสปิดการขาย)
* **เป้าหมาย:** ทำนายโอกาสที่ผู้สนใจ (Lead) แต่ละรายจะเปลี่ยนเป็นลูกค้าที่ซื้อสินค้าจริง เพื่อจัดลำดับความสำคัญให้ฝ่ายขายโทรติดตาม
* **ตารางที่ใช้:** `LEAD`, `LEAD_ACTIVITY`, `CAMPAIGN`, `SALE`
* **ตัวแปรในการวิเคราะห์ (Feature Variables):**
  * `LEAD.Source_Channel` — ช่องทางการได้มา (Facebook, Line, Google, Direct)
  * `CAMPAIGN.Discount_Rate` — อัตราส่วนลดในแคมเปญที่ Lead เข้าร่วม
  * `COUNT(LEAD_ACTIVITY.Activity_ID)` — จำนวนครั้งที่มีการติดต่อติดตาม
  * `LEAD_ACTIVITY.Activity_Type` — รูปแบบการติดต่อล่าสุด (โทรศัพท์, ไลน์, นัดพบ)
  * `(Activity_Date - Created_At)` — ระยะเวลาตอบสนองนับจากวันที่ลงทะเบียน
* **ตัวแปรเป้าหมาย (Target):** `LEAD.Followup_Status` ('ปิดการขายสำเร็จ' = 1, 'ไม่สนใจ' = 0)
* **โมเดลที่ใช้:** Logistic Regression / Random Forest Classifier

---

### 🎯 งานที่ 2: การวิเคราะห์ RFM Customer Segmentation (จัดเกรดคุณค่าลูกค้า)
* **เป้าหมาย:** จัดกลุ่มลูกค้าตามพฤติกรรมการซื้อจริง 3 มิติ เพื่อวางแผนส่งเสริมการขายแบบเจาะจงรายกลุ่ม
* **ตารางที่ใช้:** `CUSTOMER`, `SALE`, `SALE_DETAIL`
* **สูตรและตัวแปรคำนวณ (RFM Metrics):**
  * **R (Recency):** ระยะเวลาห่างจากการซื้อครั้งล่าสุด $= \text{Current\_Date} - \max(\text{SALE.Confirmed\_At})$
  * **F (Frequency):** ความถี่ในการซื้อสินค้า $= \text{COUNT}(\text{SALE.Sale\_ID})$
  * **M (Monetary):** ยอดเงินรวมที่ซื้อสะสม $= \sum(\text{SALE.Total\_Amount})$
* **กลุ่มผลลัพธ์ (Customer Segments):**
  * *Champions / VIP:* ซื้อบ่อย ยอดเงินสูง เพิ่งซื้อไม่นาน
  * *Loyal Customers:* ซื้อต่อเนื่องสม่ำเสมอ
  * *At Risk:* เคยซื้อเยอะแต่หยุดซื้อไปนาน (ต้องมีโปรโมชันดึงกลับ)
  * *Lost:* ลูกค้าที่ไม่มีการซื้อซ้ำเป็นเวลานาน

---

### 🎯 งานที่ 3: Customer Churn Risk & Service Health Score (ประเมินความเสี่ยงลูกค้ายกเลิกบริการ)
* **เป้าหมาย:** ตรวจจับสัญญาณเตือนก่อนที่ลูกค้าจะเลิกใช้บริการ โดยประเมินจากประวัติปัญหา ความสม่ำเสมอในการซื้อ และคะแนนความพึงพอใจ
* **ตารางที่ใช้:** `CUSTOMER`, `TICKET`, `TICKET_MESSAGE`, `SALE`
* **ตัวแปรในการวิเคราะห์ (Health Indicators):**
  * `COUNT(TICKET.Ticket_ID)` — จำนวนครั้งที่ลูกค้าเปิดแจ้งปัญหา
  * `TICKET.Problem_Category` — ประเภทปัญหาที่มีผลต่อความพึงพอใจ (เช่น ระบบขัดข้อง, สินค้าชำรุด)
  * `AVG(Closed_At - Created_At)` — ระยะเวลาเฉลี่ยที่ใช้ในการแก้ปัญหาจนปิดเคส
  * `TICKET.Service_Rating` — คะแนนประเมินความพึงพอใจการบริการ (1–5 ดาว)
  * `(Current_Date - MAX(SALE.Confirmed_At))` — ระยะเวลาห่างจากการซื้อครั้งล่าสุด
* **ผลลัพธ์:** คำนวณเป็น **Customer Health Score (0–100)** แจ้งเตือนระดับความเสี่ยง (เขียว/เหลือง/แดง) เมื่อคะแนนต่ำกว่า 50

---

### 🎯 งานที่ 4: Campaign Performance & Marketing ROI Analytics (วิเคราะห์ผลตอบแทนแคมเปญ)
* **เป้าหมาย:** ประเมินความคุ้มค่าของการลงทุนแคมเปญการตลาด เพื่อจัดสรรงบประมาณอย่างมีประสิทธิภาพ
* **ตารางที่ใช้:** `CAMPAIGN`, `LEAD`, `SALE`
* **ตัวแปรและสูตรคำนวณ (Key Performance Indicators):**
  * **Lead Generation Rate:** จำนวนผู้สนใจที่ได้ $= \text{COUNT}(\text{LEAD.Lead\_ID})$ ต่อแคมเปญ
  * **Conversion Rate (%):** อัตราปิดการขายสำเร็จ $= \frac{\text{จำนวน Lead ที่เกิด Sale}}{\text{จำนวน Lead ทั้งหมด}} \times 100$
  * **Marketing ROI:** ผลตอบแทนจากการลงทุน $= \frac{\sum(\text{Total\_Amount จากแคมเปญ}) - \text{Budget\_Cost}}{\text{Budget\_Cost}}$

---

## 4. แผนการดำเนินงานและกำหนดส่ง (Project Timeline)

| ช่วงเวลา | กิจกรรมดำเนินงาน | ผลลัพธ์ (Deliverables) |
| :--- | :--- | :--- |
| **สัปดาห์ที่ 11**<br/>*(10 / 13 ก.ย. 69)* | **ส่งและนำเสนอข้อเสนอโครงงาน (Proposal)** | เอกสาร Proposal (A4 ไม่เกิน 2 หน้า) |
| **สัปดาห์ที่ 12–13**<br/>*(14 – 27 ก.ย. 69)* | 1. สร้าง Database Schema ตาม Data Dictionary (SQLite)<br/>2. สร้าง Mockup Data จำลองกระบวนการ<br/>3. พัฒนาหน้าจอ Streamlit UI สำหรับ 5 Process | ฐานข้อมูลพร้อมโครงสร้างตาราง + ฟังก์ชัน CRUD เบื้องต้น |
| **สัปดาห์ที่ 14**<br/>*(28 ก.ย. – 4 ต.ค. 69)* | 1. พัฒนาโมเดล Data Science (Lead Scoring & RFM)<br/>2. เชื่อมต่อกราฟ Dashboard บน Streamlit<br/>3. ทดสอบความถูกต้องของกระบวนการ | Streamlit Web App Prototype ที่ทำงานร่วมกับโมเดล Data Science ครบถ้วน |
| **สัปดาห์ที่ 15**<br/>*(8 / 11 ต.ค. 69)* | **ส่งโครงงานฉบับสมบูรณ์และนำเสนอ (Final Presentation)** | เล่มรายงานฉบับสมบูรณ์ (บทที่ 1–3 + คู่มือ) + ซอร์สโค้ด + สไลด์นำเสนอ |
