# 📘 คู่มือวิศวกรรมข้อมูลและการวิเคราะห์ 4 งานหลัก (0% – 100%)
## Smart CRM Data Science & Analytics Engineering Manual
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**สถาปัตยกรรมระบบ:** โครงสร้างความสัมพันธ์ฐานข้อมูลเชิงธุรกรรม (OLTP Relational Schema) $\rightarrow$ Analytics Layer (Views/ML Pipelines) $\rightarrow$ Decision Support Streamlit Prototype

---

# สารบัญภาพรวมทั้ง 4 Features

1. [ภาพรวมสถาปัตยกรรมท่อส่งข้อมูล (Data Pipeline Architecture)](#ภาพรวมสถาปัตยกรรมท่อส่งข้อมูล)
2. [Feature 1: Lead Scoring (พยากรณ์โอกาสปิดการขาย)](#🎯-feature-1-lead-scoring-พยากรณ์โอกาสปิดการขาย)
3. [Feature 2: Customer RFM Segmentation & K-Means (จัดเกรดและวิเคราะห์กลุ่มลูกค้า)](#📊-feature-2-customer-rfm-segmentation--k-means-จัดเกรดและวิเคราะห์กลุ่มลูกค้า)
4. [Feature 3: Customer Health Score & Churn Risk (ประเมินสุขภาพและเตือนความเสี่ยงการยกเลิก)](#🩺-feature-3-customer-health-score--churn-risk-ประเมินสุขภาพและเตือนความเสี่ยงการยกเลิก)
5. [Feature 4: Campaign Performance & Marketing ROI (วิเคราะห์ผลตอบแทนและประสิทธิภาพแคมเปญ)](#💰-feature-4-campaign-performance--marketing-roi-วิเคราะห์ผลตอบแทนและประสิทธิภาพแคมเปญ)
6. [ตารางเปรียบเทียบเชิงวิศวกรรมทั้ง 4 งาน (Comprehensive Matrix)](#📋-ตารางเปรียบเทียบเชิงวิศวกรรมทั้ง-4-งาน)

---

# ภาพรวมสถาปัตยกรรมท่อส่งข้อมูล

```
+----------------------------------------------------------------------------------------------------+
|                                    1. ฐานข้อมูล CRM (OLTP DATABASE)                                 |
|                                                                                                    |
|  [CAMPAIGN] <---> [LEAD] <---> [LEAD_ACTIVITY] <---> [SALE] <---> [CUSTOMER] <---> [TICKET]       |
|      (D5)           (D1)             (D1)              (D2)           (D3)              (D4)       |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼ (SQL Analytics Views: V1 - V4)
+----------------------------------------------------------------------------------------------------+
|                                2. การประมวลผลและสกัดคุณลักษณะ (FEATURE ENGINEERING)                |
|  - คำนวณความถี่ / วันที่ห่าง / ยอดสะสม / ระยะเวลาแก้ปัญหา / Conversion Rates / Normalization        |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
|                                 3. โมเดล DATA SCIENCE 4 งานหลัก                                    |
|                                                                                                    |
|  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  |
|  │  1. Lead Scoring    │  │  2. RFM Segment     │  │ 3. Churn & Health   │  │ 4. Campaign ROI   │  |
|  │  (Random Forest /   │  │  (Quintile Scoring  │  │ (Domain-Weighted /  │  │ (Financial Metric │  |
|  │   Logistic Reg.)    │  │   + K-Means Clust.) │  │  Logistic Reg Valid)│  │  + Chi-Square)    │  |
|  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  |
+----------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+----------------------------------------------------------------------------------------------------+
|                             4. การแสดงผลบน PROTOTYPE (STREAMLIT UI / DASHBOARD)                    |
|  - แท็กจัดลำดับความสำคัญ Lead / การแบ่งกลุ่มลูกค้า VIP / กราฟเตือน Ticket เสี่ยง / กราฟ ROI แคมเปญ  |
+----------------------------------------------------------------------------------------------------+
```

---

# 🎯 Feature 1: Lead Scoring (พยากรณ์โอกาสปิดการขาย)

* **ไฟล์โค้ดหลัก:** [`analytics/lead_scoring.py`](file:///c:/Users/momo/dev/dddsproject/analytics/lead_scoring.py)
* **SQL View:** [`V_LEAD_FEATURES`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L195-L208)
* **หน้าจอ UI:** [`pages/2_📞_Sales_Followup.py`](file:///c:/Users/momo/dev/dddsproject/pages/2_📞_Sales_Followup.py) และ [`pages/6_📊_Analytics_Dashboard.py`](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py)

### 1.1 ที่มา ที่ไป และหลักคิดทางธุรกิจ (Business Rationale)
* **ปัญหา:** พนักงานขายมีเวลาโทรติดตามลูกค้าจำกัด (15–20 รายชื่อ/วัน) แต่มีผู้สนใจเข้ามาจากแคมเปญวันละ 30–60 รายชื่อ การโทรแบบสุ่มหรือโทรตามลำดับก่อนหลัง ทำให้เสียเวลากับผู้สนใจที่ไม่ต้องการซื้อจริง และพลาดผู้สนใจที่มีความเร่งด่วนในการซื้อ (High Purchase Intent)
* **หลักคิด:** เปลี่ยนการทำงานเป็น Data-Driven โดยใช้ Supervised Machine Learning (Binary Classification) เรียนรู้จากประวัติการติดต่อในอดีตของผู้สนใจที่ซื้อและไม่ซื้อ เพื่อคำนวณเป็นความน่าจะเป็น ($0.0 - 1.0$) ให้คะแนนผู้สนใจใหม่ และจัดคิวให้โทรหาคนที่มีโอกาสซื้อสูงสุดก่อน

### 1.2 สมมติฐานหลัก (Underlying Hypotheses)
1. **Behavioral Consistency:** รูปแบบการตอบสนอง การพูดคุย และช่องทางที่มาในอดีต สามารถใช้ทำนายพฤติกรรมการตัดสินใจซื้อในอนาคตได้
2. **Channel Intent Variance:** คุณภาพและความตั้งใจซื้อของผู้สนใจในแต่ละช่องทาง (เช่น Google Search vs Facebook Ads) แตกต่างกันอย่างมีนัยสำคัญ
3. **Engagement Signal:** ยิ่งมีการติดต่อหลายครั้ง (`Activity_Count`) และความต่อเนื่องในการพูดคุยยาวนาน ยิ่งมีโอกาสปิดการขายสูง
4. **Latency Sensitivity:** ยิ่งฝ่ายขายติดต่อกลับครั้งแรกเร็วเท่าใด (`First_Response_Days`) โอกาสปิดการขายยิ่งเพิ่มขึ้น

### 1.3 ข้อมูลที่ใช้และการเชื่อมโยงกับฐานข้อมูล (Data Schema)
* **ตารางต้นทาง:** `LEAD` (D1), `LEAD_ACTIVITY` (D1), `CAMPAIGN` (D5), `SALE` (D2)
* **ฟีเจอร์ที่สกัดได้:**
  * `Source_Channel` (Categorical): ช่องทางที่มา
  * `Discount_Rate` (Numeric): ส่วนลด % ของแคมเปญ
  * `Activity_Count` (Numeric): จำนวนครั้งรวมที่โทร/คุย
  * `Distinct_Channel_Used` (Numeric): จำนวนช่องทางการติดต่อที่ใช้
  * `First_Response_Days` (Numeric): จำนวนวันนับจากสมัคร จนติดต่อครั้งแรก
  * `Engagement_Span_Days` (Numeric): ระยะห่างวันจากการติดต่อแรกถึงล่าสุด
* **ตัวแปรเป้าหมาย ($y$):** `Target_Converted` ($1 =$ ปิดการขายสำเร็จ, $0 =$ ไม่สนใจ)

### 1.4 ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)
1. **0% Ingestion:** ดึงข้อมูลเฉพาะ Lead ที่รู้ผลลัพธ์สุดท้ายแล้ว (`Followup_Status IN ('ปิดการขายสำเร็จ', 'ไม่สนใจ')`)
2. **20% Preprocessing:** รวมเป็น Scikit-learn Pipeline ด้วย `ColumnTransformer` (ตัวเลขใช้ `SimpleImputer` + `StandardScaler`, หมวดหมู่ใช้ `OneHotEncoder`)
3. **40% Model Training:** แบ่ง Train/Test 75:25 แบบ Stratified Split และเทรน 2 โมเดล:
   * Baseline: **Logistic Regression** (โมเดลเชิงเส้นเพื่อใช้วัดเกณฑ์อ้างอิง)
   * Main Model: **Random Forest Classifier** (300 Trees, `max_depth=8`, `min_samples_leaf=5`, `class_weight="balanced"`)
4. **60% Evaluation & CV:** ทดสอบ 5-Fold Cross-Validation, ประเมิน ROC-AUC, Accuracy, Precision, Recall, F1-Score
5. **80% Explainability:** สกัดค่า Feature Importance อธิบายว่าปัจจัยใดมีอิทธิพลต่อคะแนนสูงสุด
6. **100% Serving & UI:** ดึง Lead ที่ยังเปิดอยู่ (`รอการติดต่อ`, `อยู่ระหว่างเสนอขาย`) มาคำนวณ `predict_proba` แล้วจัดเกรด:
   * 🔥 **Hot ($\ge 70\%$):** โทรติดต่อทันทีใน 1 ชั่วโมง
   * 🌤 **Warm ($40\% - 69\%$):** ติดตามตามรอบปกติ
   * ❄️ **Cold ($< 40\%$):** ส่งเข้ากระบวนการ Lead Nurturing อัตโนมัติ

### 1.5 สิ่งที่ต้องมี (Prerequisites)
* ประวัติ Lead ที่มีผลลัพธ์ปิดดีลหรือปฏิเสธแล้วอย่างน้อย 50–100 แถวขึ้นไป
* บันทึกการโทรใน `LEAD_ACTIVITY` ที่ทีมงานบันทึกเวลาจริง (ห้ามเป็นตารางว่าง)

### 1.6 ต้องเทรนใหม่เมื่อไร? (Retraining Strategy)
* **รอบปกติ:** ทุก 1 เดือน หรือทุกไตรมาส
* **เมื่อเกิด Data Drift:** เปิดตัวช่องทางการตลาดใหม่ (เช่น TikTok) หรือปรับโปรโมชันส่วนลดครั้งใหญ่
* **เมื่อประสิทธิภาพตก:** เมื่อค่า ROC-AUC ในรอบเดือนล่าสุดตกลงต่ำกว่า 0.70

### 1.7 ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)
* **Cold-Start Problem:** Lead ที่เพิ่งกรอกเข้ามานาทีแรกยังไม่มีประวัติการติดต่อ คะแนนจะเริ่มที่เกณฑ์กลางหรือต่ำเสมอ จนกว่าจะมีการติดต่อครั้งแรก
* **Feedback Loop Bias:** หากเซลส์เลือกโทรเฉพาะกลุ่ม Hot Leads ละเลยกลุ่ม Cold Leads ในรอบถัดไปโมเดลจะยิ่งจำว่า Cold Leads ไม่มีวันซื้อ (ต้องสุ่มโทรตรวจเช็ก 10-15%)

---

# 📊 Feature 2: Customer RFM Segmentation & K-Means (จัดเกรดและวิเคราะห์กลุ่มลูกค้า)

* **ไฟล์โค้ดหลัก:** [`analytics/rfm_segmentation.py`](file:///c:/Users/momo/dev/dddsproject/analytics/rfm_segmentation.py)
* **SQL View:** [`V_CUSTOMER_RFM`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L210-L219)
* **หน้าจอ UI:** [`pages/1_📢_Marketing.py`](file:///c:/Users/momo/dev/dddsproject/pages/1_📢_Marketing.py) และ [`pages/6_📊_Analytics_Dashboard.py`](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py)

### 2.1 ที่มา ที่ไป และหลักคิดทางธุรกิจ (Business Rationale)
* **ปัญหา:** การทำการตลาดแบบเหวี่ยงแห (Mass Marketing) ส่งโปรโมชันเดียวกันให้ลูกค้าทุกคน ทำให้สิ้นเปลืองงบประมาณ ลูกค้าชั้นดี (VIP) ไม่ได้รับความพิเศษ ส่วนลูกค้าที่กำลังจะเลิกซื้อก็ไม่ได้รับการกระตุ้นอย่างทันท่วงที
* **หลักคิด:** ใช้ทฤษฎีการตลาดเชิงพฤติกรรม **RFM Model (Recency, Frequency, Monetary)** ร่วมกับ Unsupervised Machine Learning (K-Means Clustering) เพื่อจำแนกลูกค้าออกเป็นกลุ่มเชิงกลยุทธ์ตามมูลค่าจริง

### 2.2 สมมติฐานหลัก (Underlying Hypotheses)
1. **Recency Law:** ลูกค้าที่เพิ่งซื้อสินค้าไปเร็วๆ นี้ มีแนวโน้มจะกลับมาซื้อซ้ำและเปิดรับแคมเปญใหม่มากกว่าลูกค้าที่ไม่ได้ซื้อมานาน
2. **Pareto Principle (80/20 Rule):** รายได้ส่วนใหญ่ของธุรกิจมาจากลูกค้าประจำและลูกค้า VIP ซึ่งมีสัดส่วนเป็นส่วนน้อยของฐานลูกค้าทั้งหมด
3. **Monetary Elasticity:** ลูกค้าที่มียอดซื้อสะสมสูง มีความยืดหยุ่นต่อราคาน้อย และต้องการบริการระดับพรีเมียมมากกว่าโปรโมชันลดราคาธรรมดา

### 2.3 ข้อมูลที่ใช้และการเชื่อมโยงกับฐานข้อมูล (Data Schema)
* **ตารางต้นทาง:** `CUSTOMER` (D3), `SALE` (D2)
* **ตัวชี้วัดที่คำนวณ:**
  * `Recency_Days` ($R$): `julianday('now') - julianday(MAX(Sale.Confirmed_At))` (ยิ่งน้อยยิ่งดี)
  * `Frequency` ($F$): `COUNT(Sale.Sale_ID)` จำนวนครั้งที่ซื้อสำเร็จ
  * `Monetary` ($M$): `SUM(Sale.Total_Amount)` ยอดเงินรวมที่จ่ายจริง

### 2.4 ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)
1. **0% Aggregation:** รวมยอดคำสั่งซื้อราย `Customer_ID` จากตาราง `SALE` สถานะ `'ปิดการขายสำเร็จ'`
2. **30% Quintile Scoring (1–5):**
   * ตัดแบ่งข้อมูลตามเปอร์เซ็นไทล์ 5 ระดับด้วย `pd.qcut`
   * ค่า $R$: ยิ่งน้อยยิ่งได้คะแนนสูง (Inverted Quintile: 5 คือซื้อเร็วที่สุด, 1 คือนานที่สุด)
   * ค่า $F$ และ $M$: ยิ่งมากยิ่งได้คะแนนสูง (1 ถึง 5)
3. **60% Unsupervised Clustering (K-Means):**
   * ทำ **Log-Transformation**: $\ln(x + 1)$ บนตัวแปร RFM เพื่อลดความเบ้ขวา (Right-skewness)
   * ปรับสเกลด้วย `StandardScaler()`
   * ตรวจสอบจำนวน Cluster ที่เหมาะสม ($k$) ด้วย Elbow Method (Inertia) และ Silhouette Score (เลือก $k=4$)
4. **85% Strategic Segmentation:** ผสมผสานกฎเกณฑ์ทางธุรกิจแบ่งเป็น 6 กลุ่ม:
   * **👑 Champions:** $R \ge 4, F \ge 4, M \ge 4$ (ลูกค้าชั้นดี ยอดซื้อสูงสุด)
   * **⭐ Loyal Customers:** $R \ge 3, F \ge 3$ (ซื้อต่อเนื่องสม่ำเสมอ)
   * **🌱 New Customers:** $R \ge 4, F \le 2$ (เพิ่งเข้ามาซื้อครั้งแรกๆ)
   * **💡 Potential:** $R \ge 3, M \ge 3$ (มีแววเติบโต มียอดซื้อดี)
   * **⚠️ At Risk:** $R \le 2, F \ge 3$ (เคยซื้อบ่อยแต่เริ่มหายไปนาน)
   * **💤 Lost:** คะแนนต่ำทุกด้าน (หลุดออกจากวงจรไปแล้ว)
5. **100% Campaign Trigger:** คำนวณสรุปสัดส่วนรายได้ (Revenue Share %) และเปิดให้ Export รายชื่อกลุ่ม **At Risk** ส่งต่อให้ทีมการตลาดทำแคมเปญกระตุ้นการซื้อซ้ำทันที

### 2.5 สิ่งที่ต้องมี (Prerequisites)
* ข้อมูลการซื้อขายที่ระบุวันเวลาชำระเงินเสร็จสิ้น (`Confirmed_At`) อย่างแม่นยำ
* ลูกค้าต้องเคยมีประวัติการซื้อสำเร็จอย่างน้อย 1 ครั้ง

### 2.6 ต้องคำนวณ/เทรนใหม่เมื่อไร? (Execution & Retraining Strategy)
* **การคำนวณคะแนน (Scoring):** อัปเดตแบบ Daily Batch หรือ Real-time เพราะค่า Recency เปลี่ยนแปลงตามเวลาทุกวัน
* **การ Re-fit โมเดล K-Means:** รันใหม่ทุก 3–6 เดือน เมื่อมีการเปลี่ยนแปลงของระดับราคาสินค้าหรือพฤติกรรมการใช้จ่ายโดยรวม

### 2.7 ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)
* **High-ticket One-off Buyers:** ลูกค้าที่ซื้อสินค้าราคาสูงเพียงครั้งเดียว อาจได้คะแนน Monetary สูง แต่ Frequency ต่ำ
* **Seasonality Distortion:** ลูกค้าที่ซื้อเฉพาะช่วงเทศกาลประจำปี จะกลายสถานะเป็น At Risk นอกช่วงฤดูกาล ทั้งที่ยังไม่ได้เลิกซื้อจริง

---

# 🩺 Feature 3: Customer Health Score & Churn Risk (ประเมินสุขภาพและเตือนความเสี่ยงการยกเลิก)

* **ไฟล์โค้ดหลัก:** [`analytics/churn_health.py`](file:///c:/Users/momo/dev/dddsproject/analytics/churn_health.py)
* **SQL View:** [`V_SERVICE_HEALTH`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L221-L231)
* **หน้าจอ UI:** [`pages/5_🎫_Support_Ticket.py`](file:///c:/Users/momo/dev/dddsproject/pages/5_🎫_Support_Ticket.py) และ [`pages/6_📊_Analytics_Dashboard.py`](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py)

### 3.1 ที่มา ที่ไป และหลักคิดทางธุรกิจ (Business Rationale)
* **ปัญหา:** ลูกค้ามักไม่แจ้งล่วงหน้าก่อนจะเปลี่ยนไปใช้คู่แข่ง เมื่อลูกค้าประสบปัญหาการใช้งานซ้ำๆ หรือได้รับการแก้ปัญหาที่ล่าช้า ความไม่พอใจจะสะสมจนเกิดการเลิกซื้อ (Customer Churn) การดึงลูกค้าใหม่มีต้นทุนสูงกว่าการรักษาลูกค้าเก่าถึง 5 เท่า
* **หลักคิด:** การนำข้อมูลเชิงบวก (พฤติกรรมการซื้อต่อเนื่อง) และข้อมูลเชิงลบ (การแจ้งปัญหา, เคสค้าง, เวลาแก้ปัญหา) มาบูรณาการข้ามสายงาน เพื่อคำนวณดัชนีชี้วัดรวม **Customer Health Score (0 – 100)** เตือนภัยก่อนลูกค้าจะตีจาก

### 3.2 สมมติฐานหลัก (Underlying Hypotheses)
1. **Silent Churn Definition:** ลูกค้าที่ไม่มีคำสั่งซื้อใหม่นานเกิน 180 วัน (`CHURN_DAYS = 180`) ถือว่ามีสถานะ Churn ทางพฤติกรรมแล้ว
2. **Service Friction Impact:** ยิ่งลูกค้ามีสัดส่วนเคสปัญหารุนแรง (`Critical_Tickets`) และมีจำนวนข้อความโต้ตอบในการแก้ปัญหาสูง ยิ่งทำให้ความพึงพอใจลดลงอย่างรวดเร็ว
3. **Resolution Latency Penalty:** ระยะเวลาในการปิดเคสปัญหา (`Avg_Resolution_Days`) ส่งผลลบโดยตรงต่อความภักดีของลูกค้า

### 3.3 ข้อมูลที่ใช้และการเชื่อมโยงกับฐานข้อมูล (Data Schema)
* **ตารางต้นทาง:** `CUSTOMER` (D3), `SALE` (D2), `TICKET` (D4), `TICKET_MESSAGE` (D4)
* **ตัวแปรที่นำมาประมวลผล:**
  * ฝั่งธุรกรรม: `Recency_Days`, `Frequency`, `Monetary`
  * ฝั่งงานบริการ: `Ticket_Count`, `Critical_Tickets` (หมวดระบบขัดข้อง/ชำรุด), `Avg_Resolution_Days`, `Total_Messages`
  * อัตราส่วน: `Tickets_Per_Year` (จำนวนตั๋วเทียบต่ออายุการเป็นลูกค้า `Tenure_Days`)

### 3.4 ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)
1. **0% Cross-Domain Join:** เชื่อมโยงข้อมูลยอดขายและสถิติตั๋วบริการลูกค้าด้วย SQL View
2. **30% Feature Normalization:** ปรับตัวแปรแต่ละด้านให้อยู่ในช่วง $0.0 - 1.0$ (ทำการ Invert ค่าลบ เช่น ยิ่งปิดเคสช้าค่ายิ่งลดลง และตั้งเพดาน Cap เพื่อตัด Outliers)
3. **60% Weighted Domain Scoring:** คำนวณคะแนนเต็ม 100 ตามสัดส่วนน้ำหนัก:
   $$\text{Health Score} = 35\%(R) + 20\%(F) + 15\%(M) + 20\%(\text{Service}) + 10\%(\text{Resolution})$$
   * 🟢 **แข็งแรง ($> 65$ คะแนน):** ความสัมพันธ์ดีมาก
   * 🟡 **เฝ้าระวัง ($41 - 65$ คะแนน):** เริ่มมีความเสี่ยง ต้องติดตาม
   * 🔴 **เสี่ยงสูง ($\le 40$ คะแนน):** โอกาส Churn สูงมาก
4. **80% Model-Based Validation:**
   * ใช้ **Logistic Regression** ฝึกสอนบนพฤติกรรมจริงเพื่อทำนายสถานะ `Is_Churn`
   * เปรียบเทียบค่า ROC-AUC ของ Weighted Score กับโมเดล ML เพื่อตรวจสอบความเที่ยงตรงของเกณฑ์คะแนน
5. **100% Proactive Intervention:** แสดงแผนภูมิ Radar Chart แยก 5 มิติบนแดชบอร์ด แจ้งเตือนฝ่าย Support และผู้จัดการให้เข้าพบลูกค้าที่มีคะแนนตกต่ำทันที

### 3.5 สิ่งที่ต้องมี (Prerequisites)
* บันทึกการเปิดเคส (`Created_At`) และปิดเคส (`Closed_At`) ของ Ticket อย่างสมบูรณ์
* มีฐานข้อมูลลูกค้าที่ครอบคลุมทั้งกลุ่มที่ซื้อต่อเนื่องและกลุ่มที่หยุดซื้อเกิน 180 วัน

### 3.6 ต้องปรับปรุง/เทรนใหม่เมื่อไร? (Re-calibration Triggers)
* **Re-scoring:** รันคำนวณคะแนนสุขภาพใหม่ทุกสัปดาห์ (Weekly Batch)
* **Re-calibration:** ตรวจสอบค่าน้ำหนัก (Weights 35/20/15/20/10) ทุก 6 เดือน โดยดูค่าสัมประสิทธิ์ของ Logistic Regression ว่ามิติใดส่งผลต่อการ Churn ของลูกค้ามากขึ้น

### 3.7 ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)
* **Happy Non-reporters:** ลูกค้าที่ไม่เคยแจ้งปัญหาเลย ไม่ได้แปลว่าพึงพอใจ แต่อาจหมดความสนใจจนไม่อยากแจ้งเรื่อง (จึงต้องถ่วงน้ำหนักด้วย Recency 35% เสมอ)
* **B2B Contract Cycles:** สัญญาบริการรายปีจะมียอด Recency นานในเดือนที่ 11 ซึ่งต้องปรับเกณฑ์พิจารณาตามประเภทสัญญา

---

# 💰 Feature 4: Campaign Performance & Marketing ROI (วิเคราะห์ผลตอบแทนและประสิทธิภาพแคมเปญ)

* **ไฟล์โค้ดหลัก:** [`analytics/campaign_roi.py`](file:///c:/Users/momo/dev/dddsproject/analytics/campaign_roi.py)
* **SQL View:** [`V_CAMPAIGN_ROI`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L234-L247)
* **หน้าจอ UI:** [`pages/1_📢_Marketing.py`](file:///c:/Users/momo/dev/dddsproject/pages/1_📢_Marketing.py) และ [`pages/6_📊_Analytics_Dashboard.py`](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py)

### 4.1 ที่มา ที่ไป และหลักคิดทางธุรกิจ (Business Rationale)
* **ปัญหา:** ฝ่ายการตลาดมักวัดผลจากตัวเลขหลอกตา (Vanity Metrics) เช่น จำนวนคลิก หรือจำนวนผู้สนใจ แต่ผู้บริหารต้องการทราบความคุ้มค่าทางการเงินสุทธิว่างบประมาณที่ลงทุนไปสร้างกำไรหรือขาดทุนเท่าใด
* **หลักคิด:** เชื่อมโยงต้นทุนแคมเปญ (D5) ข้ามไปยังรายได้จริงจากการปิดการขาย (D2) เพื่อคำนวณดัชนีทางการเงิน (ROI, ROAS, CAC, CPL), วิเคราะห์การไหลของลูกค้าผ่าน Marketing Funnel และทดสอบสมมติฐานทางสถิติของช่องทางต่างๆ

### 4.2 สมมติฐานหลัก (Underlying Hypotheses)
1. **Direct Campaign Attribution:** ลูกค้าที่ลงทะเบียนผ่าน Campaign ใด เมื่อเกิดบิลขายขึ้น ยอดขายนั้นถือเป็นผลลัพธ์จากอิทธิพลของแคมเปญนั้น
2. **Channel Efficiency Difference:** ช่องทางการตลาดต่างกันมีอัตราการเปลี่ยนเป็นยอดซื้อ (Conversion Rate) แตกต่างกันจริง
3. **Statistical Significance:** ความแตกต่างของผลตอบแทนระหว่างช่องทางไม่ได้เกิดจากความบังเอิญ แต่เกิดจากคุณภาพของกลุ่มเป้าหมายในช่องทางนั้น

### 4.3 ข้อมูลที่ใช้และการเชื่อมโยงกับฐานข้อมูล (Data Schema)
* **ตารางต้นทาง:** `CAMPAIGN` (D5), `LEAD` (D1), `SALE` (D2), `SALE_DETAIL` (D2), `PRODUCT`
* **ตัวชี้วัดทางการเงินที่คำนวณ:**
  * `Budget_Cost`: งบประมาณต้นทุนของแคมเปญ
  * `Total_Leads` & `Converted_Leads`: จำนวนผู้สนใจและจำนวนผู้ซื้อจริง
  * `Revenue`: ยอดขายรวมที่สร้างได้
  * `Conversion_Rate (%)`: $\frac{\text{Converted Leads}}{\text{Total Leads}} \times 100$
  * `CPL` (Cost Per Lead): $\frac{\text{Budget}}{\text{Total Leads}}$
  * `CAC` (Customer Acquisition Cost): $\frac{\text{Budget}}{\text{Converted Leads}}$
  * `ROAS` (Return on Ad Spend): $\frac{\text{Revenue}}{\text{Budget}}$
  * `Marketing ROI`: $\frac{\text{Revenue} - \text{Budget}}{\text{Budget}}$

### 4.4 ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)
1. **0% Aggregation:** รวมงบประมาณแคมเปญ นับจำนวน Lead และหายอดขายรวมจากตารางบิลขายที่ยืนยันแล้ว
2. **25% Metric Engineering & Verdict:** คำนวณ ROI, ROAS, CAC และติดป้ายประเมินผล:
   * ❌ **ขาดทุน:** $\text{ROI} < 0\%$ (รายได้น้อยกว่างบ)
   * ⚠️ **พอไปได้:** $0\% \le \text{ROI} \le 100\%$ (เท่าทุนหรือกำไรเล็กน้อย)
   * ✅ **คุ้มค่ามาก:** $\text{ROI} > 100\%$ (กำไรเกินเท่าตัว)
3. **50% Marketing Funnel Breakdown:** วิเคราะห์อัตราการตกหล่น (% Drop-off) ใน 4 ลำดับขั้น:
   $$\text{ผู้สนใจทั้งหมด} \longrightarrow \text{ได้รับการติดตาม} \longrightarrow \text{ออกใบเสนอราคา} \longrightarrow \text{ปิดการขายสำเร็จ}$$
4. **75% Statistical Hypothesis Testing (Chi-Square Test):**
   * สร้างตาราง Contingency Table (ช่องทาง vs สถานะปิดการขาย)
   * คำนวณค่า **Chi-Square Test of Independence ($\chi^2$)** และ $p\text{-value}$ ผ่าน `scipy.stats`
   * หาก $p < 0.05$ สรุปได้อย่างมั่นใจว่าช่องทางที่มามีผลต่อการตัดสินใจซื้อจริงอย่างมีนัยสำคัญทางสถิติ
5. **100% Executive Dashboard:** แสดงกราฟแนวโน้มรายเดือน สินค้าขายดี และคำแนะนำเชิงกลยุทธ์ในการโยกย้ายงบประมาณไปยังแคมเปญที่ให้ผลตอบแทนสูงสุด

### 4.5 สิ่งที่ต้องมี (Prerequisites)
* ฝ่ายการตลาดต้องบันทึกงบประมาณจริง (`Budget_Cost`) ทุกครั้งที่สร้างแคมเปญ
* บันทึกการขายต้องผูกโยงกับ `Lead_ID` ที่ระบุ `Campaign_ID` ได้อย่างถูกต้อง

### 4.6 ต้องประมวลผลใหม่เมื่อไร? (Execution Schedule)
* **Real-time / On-demand:** ตัวเลขคำนวณใหม่ทันทีที่มีการบันทึกคำสั่งซื้อสำเร็จในระบบ
* **Post-Campaign Audit:** สรุปผลทางการเมื่อสิ้นสุดระยะเวลาแคมเปญเพื่อจัดสรรงบประมาณในไตรมาสถัดไป

### 4.7 ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)
* **Single-Touch Attribution:** การผูกยอดขายกับแคมเปญเดียว ไม่สะท้อนพฤติกรรมลูกค้าที่เห็นสื่อหลายช่องทางก่อนตัดสินใจซื้อ (Multi-touch Journey)
* **Lagged Sales Cycle:** ในธุรกิจ B2B ยอดขายอาจเกิดขึ้นหลังจากแคมเปญจบไปแล้วหลายเดือน ทำให้ช่วงแรกตัวเลข ROI อาจดูติดลบชั่วคราว

---

# 📋 ตารางเปรียบเทียบเชิงวิศวกรรมทั้ง 4 งาน

| มิติเปรียบเทียบ | Feature 1: Lead Scoring | Feature 2: RFM Segmentation | Feature 3: Churn & Health | Feature 4: Campaign ROI |
| :--- | :--- | :--- | :--- | :--- |
| **Data Science Paradigm** | Supervised Learning (Classification) | Unsupervised Learning & Quintiles | Weighted Domain Scoring & Validation | Financial Analytics & Inference |
| **โมเดล/สถิติที่ใช้** | Random Forest + Logistic Regression | K-Means + Silhouette Score | Weighted Scoring + Logistic Reg. | Chi-Square Test ($\chi^2$) + Financial Form. |
| **ตารางฐานข้อมูลหลัก** | `LEAD`, `LEAD_ACTIVITY`, `CAMPAIGN` | `CUSTOMER`, `SALE` | `CUSTOMER`, `SALE`, `TICKET` | `CAMPAIGN`, `LEAD`, `SALE`, `PRODUCT` |
| **Output หลัก** | Probability Score (0-100%), Tier | Segment Name, Cluster ID | Health Score (0-100), Risk Tier | ROI, ROAS, CAC, Funnel Drop-off % |
| **ผู้ใช้งานเป้าหมาย** | พนักงานขาย (Sales Reps) | ผู้จัดการฝ่ายการตลาด | ฝ่ายบริการลูกค้า (Support / CS) | ผู้บริหาร (Executive) และฝ่ายวางแผน |
| **ความถี่ในการเทรน/คำนวณ** | Retrain ทุกเดือน / ไตรมาส | Recompute ทุกวัน, Re-cluster ทุก 3 เดือน | Recompute ทุกสัปดาห์, Re-calibrate 6 เดือน | Real-time Dashboard ตามธุรกรรม |
