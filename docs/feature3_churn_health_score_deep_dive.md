# 🩺 คู่มือเจาะลึก Feature 3: Customer Health Score & Churn Risk (0% – 100%)
## ระบบประเมินสุขภาพความสัมพันธ์ลูกค้าและเตือนภัยความเสี่ยงการยกเลิก (Proactive Churn Alert)
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**อ้างอิงโค้ด:** `analytics/churn_health.py`, `db/schema.sql`, `pages/4_👤_Customer_Profile.py`, `pages/5_🎫_Support_Ticket.py`, `pages/6_📊_Analytics_Dashboard.py`

---

## 1. ที่มา ที่ไป และหลักคิดทางธุรกิจ (Problem & Business Motivation)

### 🔴 ปัญหาเดิมของการดูแลลูกค้า (The Problem)
* **การตีจากแบบเงียบงัน (Silent Customer Churn):** ในธุรกิจบริการและ B2B ลูกค้าส่วนใหญ่จะไม่เดินมาบอกล่วงหน้าว่าจะหยุดซื้อหรือเปลี่ยนไปใช้คู่แข่ง แต่จะค่อยๆ ลดการติดต่อ ลดปริมาณการสั่งซื้อ จนกระทั่งหายไปในที่สุด
* **ขาดการบูรณาการข้อมูลข้ามสายงาน (Cross-department Silo):**
  * ฝ่ายขาย (Sales) ดูแลเฉพาะยอดซื้อและสัญญา
  * ฝ่ายสนับสนุน (Support/CS) ดูแลเฉพาะการรับเรื่องร้องเรียน (Tickets)
  * ขาดการเชื่อมโยงว่า ลูกค้าที่กำลังประสบปัญหาทางเทคนิคบ่อยครั้ง มีความเสี่ยงที่จะหยุดต่อสัญญาในอีกไม่กี่เดือนข้างหน้า
* **ต้นทุนการหาลูกค้าใหม่สูงกว่าการรักษาลูกค้าเดิม (Acquisition vs Retention):** การดึงดูดลูกค้าใหม่มีต้นทุนค่าการตลาดและโฆษณาสูงกว่าการรักษาฐานลูกค้าเดิมถึง 5–7 เท่า การปล่อยให้ลูกค้าปัจจุบัน Churn จึงส่งผลกระทบต่อกำไรสุทธิโดยตรง

### 💡 หลักคิดของโซลูชัน (The Core Concept)
* สร้างดัชนีชี้วัดสุขภาพลูกค้าแบบองค์รวม **Customer Health Score (0 – 100 คะแนน)** โดยผสมผสานทั้ง **สัญญาณเชิงบวก (Positive Value: พฤติกรรมการซื้อ)** และ **สัญญาณเชิงลบ (Negative Friction: ปัญหาจากการรับบริการ)**
* กำหนดเกณฑ์แจ้งเตือนความเสี่ยง (Risk Tiers) ออกเป็น 3 ระดับ: 🟢 **แข็งแรง**, 🟡 **เฝ้าระวัง**, 🔴 **เสี่ยงสูง**
* กำหนดนิยามการยกเลิกเชิงพฤติกรรม (**Silent Churn = ไม่มีการสั่งซื้อเกิน 180 วัน**)
* ใช้ **Machine Learning (Logistic Regression)** ตรวจสอบความเที่ยงตรง (Model-based Validation) และถอดรหัสปัจจัยขับเคลื่อนหลัก (Driver Importance) เพื่อให้ฝ่ายบริการและฝ่ายขายเข้าแทรกแซงเชิงรุก (Proactive Retention Intervention) ก่อนที่ลูกค้าจะหายไปจริง

---

## 2. สมมติฐานหลัก (Underlying Hypotheses & Assumptions)

1. **Purchase Recency as Ultimate Engagement Indicator:**  
   ระยะเวลาที่ห่างจากการซื้อครั้งล่าสุด (`Recency_Days`) คือดัชนีชี้วัดความผูกพันที่แม่นยำที่สุด ลูกค้าที่หยุดสั่งซื้อเกิน 180 วัน มีโอกาสกลับมาซื้อเองน้อยกว่า 5%
2. **Service Friction Escalation Hypothesis:**  
   ปัญหาทางเทคนิคระดับวิกฤต (`Critical_Tickets`) เช่น ระบบล่ม หรือสินค้าชำรุด มีผลทำลายความเชื่อมั่นของลูกค้ามากกว่าปัญหาทั่วไปอย่างมีนัยสำคัญ
3. **Resolution Latency Frustration:**  
   ระยะเวลาในการแก้ปัญหาที่ยาวนาน (`Avg_Resolution_Days`) และจำนวนข้อความโต้ตอบในการปิดเคส (`Total_Messages`) สะท้อนถึงความยุ่งยาก (Customer Effort) ซึ่งยิ่งสูง ยิ่งเร่งให้อัตรา Churn สูงขึ้น
4. **Tenure Buffering Effect:**  
   ลูกค้าที่เป็นสมาชิกมานานหลายปี (`Tenure_Days`) มีความอดทนต่อปัญหาได้ดีกว่าลูกค้าใหม่ แต่หากคะแนนสุขภาพลดลงต่อเนื่องจนถึงเกณฑ์วิกฤต การสูญเสียลูกค้ารายนี้จะสร้างความเสียหายต่อรายได้มหาศาล

---

## 3. สถาปัตยกรรมข้อมูลและการเชื่อมโยงฐานข้อมูล (Data Architecture & Schema)

ระบบดึงข้อมูลแบบบูรณาการ 2 มิติ (ธุรกรรมการขาย + งานบริการ) จาก Views [`V_CUSTOMER_RFM`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L210-L219) และ [`V_SERVICE_HEALTH`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L221-L231):

```
+--------------------+           +--------------------+           +--------------------+
|   CUSTOMER (D3)    |           |     SALE (D2)      |           |    TICKET (D4)     |
|--------------------|           |--------------------|           |--------------------|
| Customer_ID (PK)   |1         *| Sale_ID (PK)       |1         *| Ticket_ID (PK)     |
| Company_Name       |-----------| Lead_ID (FK)       |-----------| Customer_ID (FK)   |
| Membership_Date    |           | Confirmed_At       |           | Problem_Category   |
| Customer_Type      |           | Total_Amount       |           | Created_At         |
+--------------------+           +--------------------+           | Closed_At          |
                                                                  +--------------------+
                                                                            1
                                                                            |
                                                                            *
                                                                  +--------------------+
                                                                  | TICKET_MESSAGE(D4) |
                                                                  |--------------------|
                                                                  | Message_ID (PK)    |
                                                                  | Ticket_ID (FK)     |
                                                                  +--------------------+
```

### คำสั่ง SQL สร้างชั้นข้อมูลสุขภาพ (`db/schema.sql`)
```sql
CREATE VIEW V_SERVICE_HEALTH AS
SELECT  cu.Customer_ID,
        COUNT(DISTINCT t.Ticket_ID) AS Ticket_Count,
        SUM(CASE WHEN t.Problem_Category IN ('ระบบขัดข้อง','สินค้าชำรุด') THEN 1 ELSE 0 END) AS Critical_Tickets,
        AVG(julianday(t.Closed_At) - julianday(t.Created_At)) AS Avg_Resolution_Days,
        COUNT(m.Message_ID) AS Total_Messages
FROM CUSTOMER cu
LEFT JOIN TICKET t         ON t.Customer_ID = cu.Customer_ID
LEFT JOIN TICKET_MESSAGE m ON m.Ticket_ID   = t.Ticket_ID
GROUP BY cu.Customer_ID;
```

### คำสั่ง SQL เชื่อมโยงตัวแปรหลัก (`analytics/churn_health.py`)
```sql
SELECT  r.Customer_ID, r.Customer_Type, r.Recency_Days, r.Frequency, r.Monetary,
        COALESCE(h.Ticket_Count, 0)       AS Ticket_Count,
        COALESCE(h.Critical_Tickets, 0)   AS Critical_Tickets,
        h.Avg_Resolution_Days,
        COALESCE(h.Total_Messages, 0)     AS Total_Messages,
        cu.Company_Name,
        CAST(julianday('now') - julianday(cu.Membership_Date) AS INTEGER) AS Tenure_Days
FROM V_CUSTOMER_RFM r
JOIN CUSTOMER cu       ON cu.Customer_ID = r.Customer_ID
LEFT JOIN V_SERVICE_HEALTH h ON h.Customer_ID = r.Customer_ID;
```

### พจนานุกรมฟีเจอร์สุขภาพ (Health Feature Dictionary)

| ตัวแปร | แหล่งที่มา | ทิศทางผลต่อสุขภาพ | บทบาทในการคำนวณ |
| :--- | :--- | :---: | :--- |
| **`Recency_Days`** | `V_CUSTOMER_RFM` | ➖ ยิ่งมาก ยิ่งแย่ | วัดความห่างเหินจากการซื้อ (Cap: 540 วัน) |
| **`Frequency`** | `V_CUSTOMER_RFM` | ➕ ยิ่งมาก ยิ่งดี | วัดความต่อเนื่องในการอุดหนุน (Cap: 6 ครั้ง) |
| **`Monetary`** | `V_CUSTOMER_RFM` | ➕ ยิ่งมาก ยิ่งดี | ขนาดคุณค่าทางเศรษฐกิจ (Log-transformed) |
| **`Tickets_Per_Year`** | คำนวณจาก Ticket / Tenure | ➖ ยิ่งมาก ยิ่งแย่ | อัตราการเกิดปัญหาเฉลี่ยต่อปี (Cap: 12 เคส) |
| **`Critical_Tickets`** | `V_SERVICE_HEALTH` | ➖ ยิ่งมาก ยิ่งแย่ | จำนวนเคสรุนแรง (ระบบล่ม, สินค้าพัง) |
| **`Avg_Resolution_Days`** | `V_SERVICE_HEALTH` | ➖ ยิ่งมาก ยิ่งแย่ | ความช้าในการปิดปัญหา (Cap: 21 วัน) |
| **`Tenure_Days`** | `CUSTOMER.Membership_Date`| ➕ ยิ่งมาก ยิ่งผูกพัน | อายุการเป็นสมาชิกลูกค้า (วัน) |

---

## 4. ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)

```
[0% Data Join] ➔ [30% Normalization & Cap] ➔ [60% Weighted Health Score] ➔ [80% Model Validation] ➔ [100% Intervention Alert]
```

### 🔹 ขั้นที่ 1 (0% – 30%): การรวมข้อมูลและคำนวณอัตราส่วน (Feature Aggregation)
* ทำการ Query ดึงข้อมูลธุรกรรมร่วมกับประวัติการบริการลูกค้า
* คำนวณอัตราส่วนภาระปัญหาต่อปี (`Tickets_Per_Year`):
  $$\text{Tickets\_Per\_Year} = \frac{\text{Ticket\_Count}}{\max(\text{Tenure\_Days}, 30) / 365}$$
  *(ใช้ `clip(lower=30)` เพื่อป้องกันปัญหาการหารด้วยค่าเกือบศูนย์สำหรับลูกค้าที่เพิ่งสมัครใหม่)*

### 🔹 ขั้นที่ 2 (30% – 60%): การปรับสเกลและการตัดขอบเขต (Data Normalization with Caps)
ฟังก์ชัน `_norm(s, invert=False, cap=None)` ทำหน้าที่แปลงค่าดิบให้อยู่ในสเกล $0.0 – 1.0$:
* **การตัดขอบเขตเพื่อลดผลกระทบของค่าผิดปกติ (Outlier Capping):**
  * `Recency_Days`: Cap ที่ 540 วัน (หากเกินนี้ถือว่าแย่เท่ากันทั้งหมด)
  * `Frequency`: Cap ที่ 6 ครั้ง
  * `Tickets_Per_Year`: Cap ที่ 12 ครั้งต่อปี
  * `Avg_Resolution_Days`: Cap ที่ 21 วัน
* **Min-Max Scaling & Directional Inversion:**
  $$n = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$
  * ถ้าเป็นตัวแปรที่ส่งผลเชิงลบ (`invert=True` เช่น Recency, Tickets, Resolution Days) จะทำการกลับด้าน:
    $$\text{score} = 1.0 - n$$
    เพื่อให้ได้คะแนน $1.0$ เมื่อเกิดปัญหาน้อยที่สุด และ $0.0$ เมื่อเกิดปัญหามากที่สุด

### 🔹 ขั้นที่ 3 (60% – 75%): การคำนวณคะแนนรวมตามสัดส่วนน้ำหนัก (Domain-Weighted Scoring)
คะแนนสุขภาพเต็ม 100 คะแนน คำนวณจากน้ำหนัก 5 มิติหลัก:

$$\text{Health Score} = 35\%(R_{\text{norm}}) + 20\%(F_{\text{norm}}) + 15\%(M_{\text{norm}}) + 20\%(\text{Service}_{\text{norm}}) + 10\%(\text{Resolution}_{\text{norm}})$$

* **การกระจายน้ำหนัก (`WEIGHTS`):**
  * **Recency (35%):** ความสดใหม่ของการซื้อขาย (น้ำหนักสูงสุด)
  * **Frequency (20%):** ความถี่ในการซื้อซ้ำ
  * **Monetary (15%):** มูลค่าการซื้อสะสม
  * **Service Friction (20%):** ปัญหาที่พบ (คำนวณจาก `Tickets_Per_Year + 0.5 * Critical_Tickets`)
  * **Resolution Latency (10%):** ความรวดเร็วในการแก้ปัญหาของทีมงาน

### 🔹 ขั้นที่ 4 (75% – 85%): การจัดระดับความเสี่ยงและพยากรณ์การยกเลิก (Risk Stratification)
* **การแบ่งกลุ่มระดับความเสี่ยง (Risk Level):**
  * 🟢 **แข็งแรง (Health Score $> 65$):** สุขภาพดีเยี่ยม ปัญหาบริการต่ำ มีการซื้อซ้ำต่อเนื่อง
  * 🟡 **เฝ้าระวัง ($40 < \text{Health Score} \le 65$):** เริ่มพบปัญหาการบริการ หรือไม่ได้ซื้อสินค้ามาเกิน 3–4 เดือน
  * 🔴 **เสี่ยงสูง ($\text{Health Score} \le 40$):** มีแนวโน้มยกเลิกสูงมาก ต้องเข้าแทรกแซงทันที
* **การประมาณความน่าจะเป็นในการ Churn:**
  $$\text{Churn\_Prob\_Pct} = 100 - \text{Health\_Score}$$
* **คำนวณมูลค่ารายได้ที่ตกอยู่ในความเสี่ยง (Revenue At Stake):**
  รวบรวมผลรวม `Monetary` ของลูกค้าในกลุ่มเสี่ยงสูง เพื่อให้ฝ่ายบริหารเห็นผลกระทบทางการเงินชัดเจน

### 🔹 ขั้นที่ 5 (85% – 100%): การทวนสอบด้วยโมเดลสถิติ (Model-Based Validation)
ฟังก์ชัน `validate_with_model(df)` ทำหน้าที่ตรวจสอบความถูกต้องทางวิทยาศาสตร์:
1. กำหนดเป้าหมาย $y = \text{Is\_Churn}$ โดยนิยามว่า $\text{Recency\_Days} > 180$
2. นำฟีเจอร์อิสระ 6 ตัวเข้าสู่โมเดล **Logistic Regression with Balanced Class Weight**:
   $$P(\text{Churn}) = \frac{1}{1 + e^{-(\beta_0 + \sum \beta_i X_i)}}$$
3. ประเมินผลเปรียบเทียบค่า **ROC-AUC**:
   * `AUC_LogReg`: ความแม่นยำของโมเดล Machine Learning
   * `AUC_HealthScore_Rule`: ความแม่นยำของสูตรคะแนน Health Score ถ่วงน้ำหนัก
   *(หากทั้งสองค่าสูงกว่า $0.80$ ยืนยันว่าเกณฑ์คะแนนมีความเที่ยงตรงและสอดคล้องกับพฤติกรรม Churn จริง)*
4. วิเคราะห์ **Top Drivers:** ดูค่าสัมประสิทธิ์ ($\beta$) เพื่อระบุว่าตัวแปรใดมีอิทธิพลในการผลักดันให้ลูกค้า Churn มากที่สุด

---

## 5. สิ่งที่ต้องมีก่อนเริ่มใช้งาน (Prerequisites)

1. **บันทึกเวลาเปิด-ปิดเคสของ Support:**
   * ตาราง `TICKET` ต้องมีการระบุ `Created_At` และ `Closed_At` หากปล่อยให้เคสค้างโดยไม่ลงเวลาปิด ระบบจะไม่สามารถคำนวณ `Avg_Resolution_Days` ได้อย่างสมบูรณ์
2. **การจัดหมวดหมู่ประเภทปัญหา:**
   * พนักงานรับเรื่องต้องระบุ `Problem_Category` อย่างตรงไปตรงมา โดยเฉพาะการจัดเป็น 'ระบบขัดข้อง' หรือ 'สินค้าชำรุด'
3. **ประวัติการเป็นสมาชิก:**
   * ตาราง `CUSTOMER` ต้องมีฟิลด์ `Membership_Date` เพื่อใช้วัดอายุลูกค้า (Tenure)

---

## 6. ต้องปรับปรุง/คำนวณคะแนนใหม่เมื่อไร? (Re-calibration Triggers)

1. **รอบการคำนวณคะแนน (Weekly Batch Scoring):**
   * ประมวลผลคะแนนสุขภาพใหม่ทุกสัปดาห์ (หรือทันทีที่มี Ticket ปิดเคส) เพื่อให้หน้า Dashboard แสดงสถานะที่เป็นปัจจุบัน
2. **การปรับทบทวนค่าน้ำหนัก (Bi-annual Re-weighting Audit):**
   * ทุก 6 เดือน ให้เรียกดู `Top_Drivers` จากโมเดล Logistic Regression:
     * หากพบว่าสัมประสิทธิ์ของ `Avg_Resolution_Days` มีค่าลบสูงขึ้นมาก แสดงว่าลูกค้าในยุคปัจจุบันให้ความสำคัญกับความเร็วในการบริการมากกว่าเดิม อาจต้องพิจารณาปรับเพิ่มน้ำหนักจาก 10% เป็น 15–20%
3. **การเปลี่ยนแปลงของนิยาม Churn Days:**
   * หากธุรกิจปรับเปลี่ยนโมเดลจากการขายครั้งคราวมาเป็นสัญญารายเดือน (SaaS/Subscription) ต้องปรับลดเกณฑ์ `CHURN_DAYS` จาก 180 วัน ลงมาเป็น 45–60 วัน

---

## 7. ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)

1. **ลูกค้านิ่งเฉยแต่ไม่พอใจ (Unhappy Silent Customers):**
   * ลูกค้าบางรายประสบปัญหาแต่ไม่เคยเปิดแจ้ง Ticket เข้ามาในระบบเลย แล้วตัดสินใจเลิกซื้อทันที ระบบป้องกันจุดบอดนี้ด้วยการให้น้ำหนักกับ Recency สูงถึง 35% ดังนั้นแม้ Ticket จะเป็น 0 แต่ถ้าไม่ซื้อใหม่ คะแนนสุขภาพจะลดลงอย่างต่อเนื่องอยู่ดี
2. **รอบการซื้อของกลุ่ม B2B Contract:**
   * ลูกค้าองค์กรขนาดใหญ่ที่มีรอบการสั่งซื้อปีละ 1 ครั้ง อาจถูกจัดเป็นกลุ่มเสี่ยงในเดือนที่ 6–8 ทั้งที่ยังอยู่ในรอบการจัดซื้อปกติ
3. **การแก้ไขปัญหาแบบชั่วคราว (False Resolution):**
   * เคสที่ปิดอย่างรวดเร็ว (`Closed_At` เร็ว) แต่อาจเกิดจากการที่เจ้าหน้าที่กดปิดเคสโดยที่ปัญหายังไม่ได้รับการแก้ไขอย่างแท้จริง ซึ่งสามารถตรวจจับได้จากจำนวน `Total_Messages` หรือการเปิดเคสซ้ำ

---

## 8. สรุปความเชื่อมโยงกับหน้าจอแอปพลิเคชัน (Streamlit UI Integration)

* **หน้าข้อมูลลูกค้า ([4_👤_Customer_Profile.py](file:///c:/Users/momo/dev/dddsproject/pages/4_👤_Customer_Profile.py)):**
  * มาตรวัดสุขภาพ (Health Meter / Gauge) แสดงคะแนนและระดับความเสี่ยงของลูกค้ารายตัว
  * แผนภูมิ Radar Chart 5 มิติ (Recency, Frequency, Monetary, Service, Resolution) แจกแจงจุดแข็งและจุดเปราะบาง
* **หน้ารับแจ้งปัญหา ([5_🎫_Support_Ticket.py](file:///c:/Users/momo/dev/dddsproject/pages/5_🎫_Support_Ticket.py)):**
  * แสดงแท็กเตือนภัยสีแดงสำหรับ Ticket ที่เปิดโดยลูกค้ากลุ่ม "🔴 เสี่ยงสูง" เพื่อให้หัวหน้าทีม Support เข้ามาช่วยดูแลเป็นพิเศษ
* **หน้าแดชบอร์ดวิเคราะห์ ([6_📊_Analytics_Dashboard.py](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py) — แท็บ 3):**
  * การ์ด KPI สรุปจำนวนลูกค้ากลุ่มเสี่ยงและมูลค่ารายได้ที่ตกอยู่ในความเสี่ยง (Revenue at Stake)
  * กราฟกระจายตัวสุขภาพลูกค้า (Health Score Distribution Histogram)
  * ตารางจัดอันดับ "10 ลูกค้าเสี่ยงสูงที่ต้องติดตามด่วนที่สุด" พร้อมปุ่มโทรติดต่อ
  * การแสดงผลการตรวจสอบความเที่ยงตรงด้วย Logistic Regression (ROC-AUC และ Top Drivers)
