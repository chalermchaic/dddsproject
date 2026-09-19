# 📌 สรุปแผนงานที่ต้องทำต่อ (Action Plan: What's Next)
### โครงงาน DDDS: ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM)

> **เป้าหมาย:** สรุปรายการงานที่ต้องลงมือทำจริงแบบกระชับ อ่านง่าย นำไปใช้ทำคู่มือ (Plan 2) และซ้อม Live Demo 10 นาที (Plan 5) ได้ทันที

---

## 🧭 ภาพรวมสิ่งที่ต้องทำต่อ (High-Level Checklist)

```
[งานที่ 1: Manual Plan 2]  ──► ใส่ภาพจริง 27 ภาพลงคู่มือ user_manual.docx และตรวจ 14 กิจกรรม
[งานที่ 2: Demo Plan 5]    ──► ซ้อมเดโมโหมดคนเดียว (1 คนพูดไปคลิกไป) ดูคู่มือสไลด์ 15-17 ใน PPTX
[งานที่ 3: เครื่องมือในเว็บ]  ──► มีปุ่ม "🔄 รีเซ็ตฐานข้อมูล Demo" บนหน้าเว็บ (Login & Sidebar) พร้อมใช้แล้ว
```

---

## 1. งานคู่มือการใช้งานระบบ (Plan 2: User Manual)

### 📝 สิ่งที่ต้องทำ:
1. **ประกอบภาพหน้าจอจริงลง Word:** นำไฟล์ภาพจากโฟลเดอร์ `docs/evidence/` (มีครบแล้ว 27 ภาพจริง) ไปแทรกแทนภาพ DFD ในแต่ละหัวข้อ
2. **ตรวจเช็ค 14 กิจกรรมตาม DFD:** ตรวจทานเนื้อหาให้อธิบายตามขั้นตอนจริง:
   * **การตลาด (Marketing):** สร้างแคมเปญ (`1_1_campaign_saved.png`), รับ Lead ใหม่ (`1_2_lead_saved.png`)
   * **งานขาย (Sales):** ดูคิวงาน AI Priority (`2_1_ai_priority.png`), บันทึกโทร (`2_2_activity_timeline.png`), ออกใบเสนอราคา (`2_3_quotation_issued.png`), ตรวจสลิป (`3_2_payment_check.png`), ออกใบเสร็จ (`3_3_receipt_issued.png`)
   * **บริการลูกค้า (Support):** เปิดเคส (`4_1_ticket_created.png`), แชท (`4_2_ticket_chat.png`), ปิดเคส (`4_3_ticket_closed.png`)
   * **Portal ลูกค้า:** ลงทะเบียนเอง, โอนเงินแนบสลิป, ให้คะแนน 5 ดาว (`4_3_rating_given.png`)
   * **Dashboard:** วิธีอ่านค่า 4 แท็บ (Lead Scoring, RFM, Churn/Health, Campaign ROI)
3. **ตัดเนื้อหาเกินขอบเขตออก:** เอาหน้าปกซ้ำซ้อน, ทฤษฎี DFD กว้างๆ, และวิธีติดตั้ง Docker ออก เพื่อให้เล่มกระชับพร้อมนำไปรวมท้ายเล่มรายงานใหญ่

---

## 2. งานเตรียมสาธิตระบบสด (Plan 5: Live Demo 10 นาที — โหมด 1 คนพูดไปคลิกไป)

> 💡 **เอกสารและสไลด์คู่มือเตรียมพร้อมแล้ว:**
> * 📄 **คู่มือสาธิตสดจับมือทำบน Streamlit:** [docs/STREAMLIT_DEMO_GUIDE.md](file:///c:/Users/momo/dev/dddsproject/docs/STREAMLIT_DEMO_GUIDE.md)
> * ☁️ **คู่มือ Deploy ขึ้น Streamlit Cloud:** [docs/STREAMLIT_CLOUD_DEPLOYMENT.md](file:///c:/Users/momo/dev/dddsproject/docs/STREAMLIT_CLOUD_DEPLOYMENT.md)
> * 📊 **สไลด์เดโมเจาะลึก 17 สไลด์:** [docs/demo.pptx](file:///c:/Users/momo/dev/dddsproject/docs/demo.pptx) / [docs/demo.pdf](file:///c:/Users/momo/dev/dddsproject/docs/demo.pdf)
> * 🧪 **รายงานผลทดสอบอัตโนมัติ:** [docs/DEMO_AUTOMATED_TEST_REPORT.md](file:///c:/Users/momo/dev/dddsproject/docs/DEMO_AUTOMATED_TEST_REPORT.md)

### 🚀 คำสั่งเปิดระบบเริ่มซ้อมทันที (มีใน Slide 15):
```bash
# 1. คืนค่าฐานข้อมูลเริ่มต้น (เลือกวิธีใดวิธีหนึ่ง):
#    - วิธี ก (Terminal): python db/seed_data.py
#    - วิธี ข (บนหน้าเว็บ): กดปุ่ม '🔄 รีเซ็ตฐานข้อมูล Demo' บนหน้า Login หรือที่แถบ Sidebar ได้ทันที!
python db/seed_data.py

# 2. รันระบบ Streamlit:
streamlit run app.py
```
* **เทคนิค Solo Presenter:** เปิด 2 หน้าต่างเบราว์เซอร์คู่กัน:
  * **ซ้าย (หน้าต่างปกติ):** หน้าพนักงาน CRM (`admin1`, `marketing1`, `sale1`, `cs1`)
  * **ขวา (Incognito):** หน้า Customer Portal (`guest`)
  * คลิกสลับซ้าย-ขวาได้ทันที ไม่ต้องล็อกอินล็อกเอาท์ซ้ำซ้อน!

---

### 📋 Cheat Sheet: รหัสข้อมูลที่ต้องใช้ตอน Demo (มีใน Slide 15)
แปะโพสต์-อิทชุดนี้ไว้ข้างคีย์บอร์ดตอนซ้อมและวันพรีเซนต์จริง:

| รหัสตัวอย่าง | ชื่อรายการ / ลูกค้า | หน้าที่ใช้ | จุดเด่นที่ต้องโชว์ |
|---|---|:---:|---|
| **`LD0264`** | นายวิชัย ทองดี | งานขาย (Process 2.0) | เป็น **Hot Lead (AI Score ~85%)** โอกาสซื้อสูง |
| **`CMP003`** | แคมเปญ "Digital Ads Q3" | การตลาด & Dashboard | **ROI สูงสุด 103%** งบ 80k ได้เงิน 8.35 ล้าน |
| **`CU0178`** | ร้านสมหญิง การค้า | Churn / Support | **กลุ่ม At Risk / Churn** ไม่ซื้อ 548 วัน มีเคสค้าง |
| **`CU0175`** | ลูกค้ากลุ่ม Champions | RFM (Dashboard) | ซื้อบ่อย ยอดรวมเฉียดล้าน (9.4 แสน) |
| **`TK0008`** | เคสบริการลูกค้า | Support (Process 4.0) | เคสปิดสำเร็จ ได้คะแนนประเมิน 5 ดาว |

---

### ⏱️ ลำดับการคลิกและบทพูด 7 ขั้นตอน (มีใน Slide 16 และ 17)

* **[00:00 - 01:00] Step 1 (Portal):** เข้าหน้า Portal จำลอง (`pages/9_portal.py`)
  * **กรอก:** ชื่อ `คุณสมชาย หมายมั่น` | เบอร์ `081-999-8888` | ช่องทาง `Facebook Ads` ➔ กด `ส่งข้อมูลการติดต่อ`
  * **บทพูด:** *"จำลองลูกค้าภายนอกส่งข้อมูลเข้าสู่ระบบ ข้อมูลไหลเข้า Store D1: LEAD ตาม DFD Process 1.0 อัตโนมัติ"*
* **[01:00 - 02:30] Step 2 (Marketing):** ล็อกอิน `marketing1` เข้า `pages/1_marketing.py`
  * **คลิก:** ชี้แคมเปญ ROI สูงสุด `CMP003` (103%) ➔ เลือก Lead สมชาย ➔ ส่งโปรโมชัน
  * **บทพูด:** *"ฝ่ายการตลาดใช้ผลคำนวณจาก Campaign ROI (Feature 4) เลือกแคมเปญที่มีผลตอบแทนสูงสุดให้ Lead เกิดการเชื่อมโยง DFD 1.0 และ 5.0"*
* **[02:30 - 04:30] Step 3 (Sales):** ล็อกอิน `sale1` เข้า `pages/2_sales_followup.py`
  * **คลิก:** แท็บคิว AI ชี้ `LD0264` (Hot Lead 85%) ➔ บันทึกผลโทร "ลูกค้าตกลงรับข้อเสนอ" ➔ ไปหน้า `3_order_billing.py` ออกใบเสนอราคาแพ็กเกจ Enterprise (ได้รหัส SL)
  * **บทพูด:** *"ฝ่ายขายใช้ AI Lead Scoring จัดลำดับความสำคัญ ช่วยเพิ่มอัตราปิดการขายตาม DFD Process 2.0"*
* **[04:30 - 05:30] Step 4 (Portal):** สลับมาหน้าต่าง Portal เลือก `LD0264`
  * **คลิก:** แท็บ ③ กดยืนยันคำสั่งซื้อ ➔ แท็บ ④ แนบสลิป `slip.png`
  * **บทพูด:** *"ลูกค้า Self-service ยืนยันคำสั่งซื้อและส่งหลักฐานโอนเงินเข้า DFD Process 3.0"*
* **[05:30 - 06:30] Step 5 (Sales):** สลับมาหน้าต่างฝ่ายขาย `pages/3_order_billing.py`
  * **คลิก:** แท็บตรวจชำระเงิน กด "ยืนยันรับเงิน" ➔ แท็บออกใบเสร็จ กด "ออกใบเสร็จ"
  * **บทพูด:** *"เมื่อตรวจรับเงินเสร็จ ระบบยกระดับสถานะจาก Lead เป็น CUSTOMER (รหัส CU) อัตโนมัติ พร้อมออกใบเสร็จตาม DFD 3.0"*
* **[06:30 - 08:00] Step 6 (Support):** ล็อกอิน `cs1` เข้า `pages/5_support_ticket.py`
  * **คลิก:** ดูเคส `CU0178` (หรือ `TK0008`) ตอบแชทช่วยลูกค้า กดปิดเคส ➔ สลับไป Portal แท็บ ⑤ กด 5 ดาว ⭐⭐⭐⭐⭐
  * **บทพูด:** *"เก็บบันทึกประวัติบริการตาม DFD 4.0 คะแนนจะไหลไปคำนวณ Customer Health Score ต่อไป"*
* **[08:00 - 10:00] Step 7 (Dashboard):** ล็อกอิน `admin1` เข้า `pages/6_analytics_dashboard.py`
  * **คลิก:** โชว์ RFM Champions (`CU0175`) vs At Risk (`CU0178`) ➔ เกจวัด Churn Health ➔ สรุป Lead Scoring & ROI ➔ กด Export CSV
  * **บทพูด:** *"ข้อมูลจากขั้นตอน 1-6 ไหลมารวมที่ Dashboard แบบ Real-time ผู้บริหารใช้ 4 โมเดล AI ขับเคลื่อนธุรกิจได้ทันที"*

---

## 3. แผนสำรองฉุกเฉิน (Emergency & Fallback)

1. **ถ้าข้อมูลเพี้ยนระหว่างเดโม/ซ้อม:**
   * **กดปุ่มบนหน้าเว็บได้ทันที:** ที่หน้า Login หรือที่แถบ Sidebar ด้านซ้าย จะมีปุ่ม **"🔄 รีเซ็ตฐานข้อมูล Demo"** กดปุ๊บ ข้อมูลจะกลับมาพร้อมเดโม 100% ใน 2 วินาที!
   * หรือรันผ่าน Terminal: `python db/seed_data.py`
2. **ถ้าเน็ตหอประชุมล่ม:** รันแบบ Localhost บนเครื่องตัวเอง ไม่ต้องต่อ Wi-Fi:
   ```bash
   streamlit run app.py --server.port 8501
   ```
3. **สคริปต์ทดสอบกระบวนการเดโมอัตโนมัติ (Automated Demo Flow Test):**
   * รันตรวจสอบความถูกต้องของทั้ง 3 เคส 7 สเต็ปก่อนขึ้นเวทีจริง:
   ```bash
   python tests/test_demo_flow.py
   # หรือผ่าน pytest:
   pytest tests/test_demo_flow.py -v
   ```
   *(หมายเหตุ: ตัดงานอัดคลิปวิดีโอสำรองออกแล้ว โดยใช้ไฟล์นำเสนอ [docs/demo.pptx](file:///c:/Users/momo/dev/dddsproject/docs/demo.pptx) ที่มีภาพหน้าจอและบทพูดกำกับทุกสไลด์ และสคริปต์ทดสอบอัตโนมัติ 100% แทน)*

