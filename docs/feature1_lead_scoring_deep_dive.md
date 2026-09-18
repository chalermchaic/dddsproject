# 🎯 คู่มือเจาะลึก Feature 1: Lead Scoring (0% – 100%)
## ระบบพยากรณ์โอกาสปิดการขายและจัดลำดับผู้สนใจอัจฉริยะ (Smart Lead Scoring)
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**อ้างอิงโค้ด:** `analytics/lead_scoring.py`, `db/schema.sql`, `pages/2_sales_followup.py`, `pages/6_analytics_dashboard.py`

---

## 1. ที่มา ที่ไป และหลักคิดทางธุรกิจ (Problem & Business Motivation)

### 🔴 ปัญหาเดิมของฝ่ายขาย (The Problem)
* **ทรัพยากรบุคคลและเวลามีจำกัด:** พนักงานขาย (Sales Representative) หนึ่งคน มีศักยภาพในการโทรติดตามและให้ข้อมูลเชิงลึกกับลูกค้าได้อย่างมีคุณภาพประมาณ 15–20 รายชื่อต่อวัน
* **ปริมาณ Lead ที่เข้ามามีมากเกินไป:** เมื่อปล่อยแคมเปญการตลาดผ่านช่องทางต่าง ๆ (Facebook Ads, Google Search, LINE Official) จะมีรายชื่อผู้สนใจ (Leads) ไหลเข้ามาวันละ 30–60 รายชื่อ
* **รูปแบบการทำงานแบบดั้งเดิม (Unoptimized Workflow):**
  1. *First-In, First-Out (FIFO):* โทรตามลำดับเวลาที่กรอกข้อมูลเข้ามา
  2. *Random Picking:* สุ่มโทรตามความรู้สึก หรือเลือกโทรเฉพาะคนที่ชื่อคุ้นเคย
* **ผลเสียทางธุรกิจ:**
  * พนักงานขายเสียเวลากับผู้สนใจที่ "แค่เข้ามาดูเล่นๆ" (Junk Leads / Window Shoppers) วันละหลายชั่วโมง
  * ผู้สนใจที่มี "ความต้องการซื้ออย่างเร่งด่วน" (High Purchase Intent) กลับต้องรอคอยคิวนานข้ามวัน จนอาจเปลี่ยนใจ หรือถูกคู่แข่งแย่งโทรไปปิดการขายก่อน

### 💡 หลักคิดของโซลูชัน (The Core Concept)
* แปลงปัญหานี้ให้เป็นโจทย์ **Supervised Machine Learning: Binary Classification**
* นำข้อมูลร่องรอยพฤติกรรม (Digital Footprints & Touchpoints) ของ Lead ในอดีต ทั้งกลุ่มที่ **ปิดการขายสำเร็จ ($y=1$)** และ **ไม่สนใจ/ปฏิเสธ ($y=0$)** มาให้โมเดล Machine Learning เรียนรู้
* โมเดลจะทำการสังเคราะห์ความสัมพันธ์ และคำนวณออกมาเป็น **คะแนนความน่าจะเป็น (Probability Score: 0.00 – 1.00 หรือ 0% – 100%)** ให้กับผู้สนใจใหม่ทุกคนที่เข้ามาในระบบ
* จัดลำดับความสำคัญ (Lead Prioritization) แบ่งเป็นเกรด **🔥 Hot / 🌤 Warm / ❄️ Cold** เพื่อให้พนักงานขายพุ่งเป้าโทรหาผู้สนใจที่มีโอกาสปิดการขายสูงสุดก่อนเป็นอันดับแรก

---

## 2. สมมติฐานหลัก (Underlying Hypotheses & Assumptions)

ก่อนที่โมเดลจะทำงานได้อย่างถูกต้อง มีสมมติฐานทางสถิติและพฤติกรรมศาสตร์ 4 ข้อที่ต้องกำหนด:

1. **Behavioral Consistency Hypothesis (พฤติกรรมในอดีตทำนายอนาคตได้):** 
   ผู้สนใจที่จะปิดการขายสำเร็จในอนาคต จะมีรูปแบบการตอบสนอง การติดต่อ และการมีปฏิสัมพันธ์คล้ายคลึงกับลูกค้าที่เคยปิดการขายสำเร็จในอดีต
2. **Channel Intent Variance (ความตั้งใจซื้อในแต่ละช่องทางไม่เท่ากัน):** 
   ผู้สนใจที่ค้นหาเข้ามาเองผ่าน Google Search (Active Intent) มีโอกาสปิดการขายสูงกว่าผู้สนใจที่ปัดผ่านหน้าฟีดโซเชียลมีเดียแล้วกดลงทะเบียน (Passive Intent)
3. **Engagement Signal Hypothesis (ระดับปฏิสัมพันธ์สะท้อนความสนใจ):** 
   จำนวนครั้งที่มีการติดต่อ (`Activity_Count`) และความต่อเนื่องของช่วงเวลาพูดคุย (`Engagement_Span_Days`) มีความสัมพันธ์เชิงบวกแบบมีนัยสำคัญกับอัตราความสำเร็จในการปิดดีล
4. **Latency Sensitivity (ความเร็วในการตอบสนองมีผลต่อความรู้สึก):** 
   ระยะเวลาที่ทีมขายติดต่อกลับครั้งแรก (`First_Response_Days`) ยิ่งสั้น โอกาสปิดการขายยิ่งสูงขึ้นอย่างมีนัยสำคัญ

---

## 3. สถาปัตยกรรมข้อมูลและการเชื่อมโยงฐานข้อมูล (Data Architecture & Schema)

โมเดลเชื่อมโยงกับฐานข้อมูลเชิงสัมพันธ์ OLTP ดึงข้อมูลจาก View พิเศษ [`V_LEAD_FEATURES`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L195-L208):

```
+------------------+         +-----------------------+         +------------------+
|     LEAD (D1)    |         |  LEAD_ACTIVITY (D1)   |         |  CAMPAIGN (D5)   |
|------------------|         |-----------------------|         |------------------|
| Lead_ID (PK)     |1       *| Activity_ID (PK)      |*       1| Campaign_ID (PK) |
| Source_Channel   |<--------| Lead_ID (FK)          |-------->| Discount_Rate    |
| Created_At       |         | Activity_Date         |         +------------------+
| Followup_Status  |         | Activity_Type         |
+------------------+         +-----------------------+
```

### คำสั่ง SQL สร้าง Feature Set (`db/schema.sql`)
```sql
CREATE VIEW V_LEAD_FEATURES AS
SELECT  l.Lead_ID,
        l.Source_Channel,
        COALESCE(c.Discount_Rate, 0)                             AS Discount_Rate,
        COUNT(a.Activity_ID)                                     AS Activity_Count,
        COUNT(DISTINCT a.Activity_Type)                          AS Distinct_Channel_Used,
        MIN(julianday(a.Activity_Date) - julianday(l.Created_At)) AS First_Response_Days,
        MAX(julianday(a.Activity_Date) - julianday(l.Created_At)) AS Engagement_Span_Days,
        CASE WHEN l.Followup_Status = 'ปิดการขายสำเร็จ' THEN 1 ELSE 0 END AS Target_Converted
FROM LEAD l
LEFT JOIN CAMPAIGN      c ON c.Campaign_ID = l.Campaign_ID
LEFT JOIN LEAD_ACTIVITY a ON a.Lead_ID     = l.Lead_ID
WHERE l.Followup_Status IN ('ปิดการขายสำเร็จ', 'ไม่สนใจ')   -- เฉพาะผลลัพธ์ที่ชัดเจนสำหรับเทรน
GROUP BY l.Lead_ID;
```

### พจนานุกรมฟีเจอร์ (Feature Dictionary)

| ชื่อฟีเจอร์ | ประเภท | บทบาทในการคำนวณ | ความหมายทางธุรกิจ |
| :--- | :--- | :--- | :--- |
| **`Discount_Rate`** | Numeric | Continuous Feature | ขนาดของส่วนลดโปรโมชันที่ Lead ได้รับ (%) เป็นตัวกระตุ้นราคา |
| **`Activity_Count`** | Numeric | Count Feature | จำนวนครั้งรวมที่พนักงานขายตามติดต่อ (โทร, ประชุม, แชท) |
| **`Distinct_Channel_Used`** | Numeric | Diversity Feature | ความหลากหลายของช่องทางที่ใช้ติดต่อ (เช่น โทรศัพท์ + LINE) |
| **`First_Response_Days`** | Numeric | Latency Feature | ความเร็วในการติดต่อกลับครั้งแรก (วัน) นับจากลงทะเบียน |
| **`Engagement_Span_Days`** | Numeric | Duration Feature | จำนวนวันนับจากการติดต่อแรกจนถึงการติดต่อล่าสุด |
| **`Source_Channel`** | Categorical | Demographic Feature | ช่องทางการได้มา (Facebook, Google, Line, Direct, Walk-in) |
| **`Target_Converted`** | Binary (0/1) | **Target Variable ($y$)** | $1 =$ ปิดการขายสำเร็จ, $0 =$ ไม่สนใจ/ปฏิเสธ |

---

## 4. ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)

```
[0% Data Query] ➔ [20% Preprocessing] ➔ [40% Model Training] ➔ [60% Evaluation] ➔ [80% Explainability] ➔ [100% Serving]
```

### 🔹 ขั้นที่ 1 (0% – 20%): การเตรียมข้อมูลและตัดแบ่ง (Data Ingestion & Split)
1. **คัดกรองข้อมูลประวัติ:** ดึงเฉพาะ Lead ที่จบกระบวนการแล้ว (`ปิดการขายสำเร็จ` หรือ `ไม่สนใจ`) จากตาราง `V_LEAD_FEATURES`
2. **ไม่นำ Lead ที่ยังค้างอยู่มาเทรน:** เพื่อป้องกันการปนเปื้อนข้อมูลที่ยังไม่รู้ผลจริง (Unlabeled Data)
3. **ตัดแบ่งข้อมูล Train / Test Split (75:25):**
   ```python
   X = df[NUM_FEATURES + CAT_FEATURES]
   y = df["Target_Converted"].astype(int)
   X_tr, X_te, y_tr, y_te = train_test_split(
       X, y, test_size=0.25, stratify=y, random_state=42
   )
   ```
   * การใช้ `stratify=y` รับประกันว่า สัดส่วนคนซื้อต่อคนไม่ซื้อในชุดฝึกสอนและชุดทดสอบจะตรงกับประชากรจริง

### 🔹 ขั้นที่ 2 (20% – 40%): การจัดการคุณลักษณะ (Data Preprocessing Pipeline)
ใช้ `ColumnTransformer` รวมการแปลงคุณลักษณะเป็นท่อเดียว (Single Pipeline) เพื่อป้องกันข้อมูลรั่วไหล (Data Leakage):
* **กลุ่มตัวแปรตัวเลข (`NUM_FEATURES`):**
  1. `SimpleImputer(strategy="median")`: เติมค่าว่างด้วยค่ามัธยฐาน
  2. `StandardScaler()`: ปรับค่าเฉลี่ยเป็น 0 และส่วนเบี่ยงเบนมาตรฐานเป็น 1 ($Z$-Score)
* **กลุ่มตัวแปรหมวดหมู่ (`CAT_FEATURES`):**
  1. `OneHotEncoder(handle_unknown="ignore")`: แปลงเป็น Dummy Variables ($0/1$) รองรับกรณีเจอช่องทางใหม่ในอนาคต

### 🔹 ขั้นที่ 3 (40% – 60%): การเลือกและฝึกสอนโมเดล (Model Training)
ทดสอบ 2 โมเดลเพื่อเปรียบเทียบประสิทธิภาพ:
1. **Baseline Model (Logistic Regression):**
   * โมเดลเชิงเส้นเพื่อใช้วัดเกณฑ์อ้างอิงพื้นฐาน
   * กำหนด `class_weight="balanced"` เพื่อปรับน้ำหนักแก้ปัญหา Class Imbalance
2. **Main Model (Random Forest Classifier):**
   * ใช้ป่าตัดสินใจ 300 ต้น (`n_estimators=300`)
   * ควบคุมการ Overfitting ด้วย `max_depth=8` และ `min_samples_leaf=5`
   * สามารถตรวจจับความสัมพันธ์แบบไม่เป็นเส้นตรง (Non-linear Interaction) เช่น ช่องทาง Google + ส่วนลด 20% รวมกันแล้วได้ผลลัพธ์สูงกว่าผลรวมของแต่ละตัว

### 🔹 ขั้นที่ 4 (60% – 80%): การประเมินผลและการอธิบายโมเดล (Evaluation & Interpretability)
* **5-Fold Cross-Validation:** วนรอบสลับชุดทดสอบ 5 ครั้งเพื่อยืนยันความเสถียรของโมเดล (`ROC-AUC Mean ± Std`)
* **Metrics:**
  * `Accuracy`: ความแม่นยำรวม
  * `Precision`: เมื่อทายว่า "จะซื้อ" ลูกค้าซื้อจริงกี่ % (ลดการเสียเวลาโทรฟรีของเซลส์)
  * `Recall`: ในบรรดาคนที่ "ซื้อจริงทั้งหมด" โมเดลตามเจอได้กี่ % (ป้องกันการพลาดลูกค้าสำคัญ)
  * `F1-Score`: ค่าเฉลี่ยฮาร์โมนิกระหว่าง Precision และ Recall
  * `ROC-AUC`: พื้นที่ใต้กราฟ ROC เพื่อวัดความสามารถในการแยกแยะ (Discrimination Power)
* **Feature Importance Analysis:**
  * ดึงค่าจาก Random Forest ออกมาแสดงให้เห็นว่าตัวแปรใดมีอิทธิพลสูงสุด (เช่น `Activity_Count` และ `Engagement_Span_Days`)

### 🔹 ขั้นที่ 5 (80% – 100%): การประยุกต์ใช้งานจริง (Model Serving & UI Action)
ฟังก์ชัน `score_open_leads(pipe)` ทำงานร่วมกับหน้าจอ Streamlit:
1. ดึง Lead ที่สถานะ `'รอการติดต่อ'` หรือ `'อยู่ระหว่างเสนอขาย'`
2. ส่งฟีเจอร์เข้า Pipeline เพื่อพยากรณ์ความน่าจะเป็น `predict_proba(...)[:, 1]`
3. จัดกลุ่มความสำคัญ (Priority Tiering):
   * 🔥 **Hot ($\text{Score} \ge 70\%$):** โทรติดต่อทันทีภายใน 1 ชั่วโมง
   * 🌤 **Warm ($40\% \le \text{Score} < 70\%$):** ติดตามตามรอบปกติ ส่งข้อมูลโปรโมชันเสริม
   * ❄️ **Cold ($\text{Score} < 40\%$):** ส่งเข้ากระบวนการ Lead Nurturing อัตโนมัติ (LINE/Email Broadcast)

---

## 5. สิ่งที่ต้องมีก่อนเริ่มใช้งาน (Prerequisites)

1. **ปริมาณข้อมูลขั้นต่ำ (Minimum Sample Size):**
   * ต้องมีข้อมูล Lead ที่รู้ผลลัพธ์แล้ว (`Closed-won` หรือ `Closed-lost`) **อย่างน้อย 50–100 รายการขึ้นไป** (ในโค้ดมีระบบป้องกัน `if len(df) < 50: raise ValueError(...)`)
2. **วินัยในการลงข้อมูลของทีมงาน (Operational Data Integrity):**
   * พนักงานขายต้องบันทึกประวัติการติดต่อในตาราง `LEAD_ACTIVITY` อย่างสม่ำเสมอ หากไม่ลงข้อมูล ตัวแปร `Activity_Count` จะเป็น 0 ทำให้คะแนนพยากรณ์ตกต่ำกว่าความเป็นจริง
3. **ความถูกต้องของ Target Definition:**
   * สถานะการปิดการขายต้องผูกโยงกับตารางคำสั่งซื้อ `SALE` ที่มีการชำระเงินจริง ไม่ใช่เพียงแค่พนักงานขายพิมพ์ว่า "คิดว่าน่าจะซื้อ"

---

## 6. ต้องเทรนโมเดลใหม่เมื่อไร? (Retraining Strategy & Drift Triggers)

Machine Learning Model มีการเสื่อมถอยของประสิทธิภาพตามกาลเวลา ต้องกำหนดกลยุทธ์การ Re-train ชัดเจน:

### 1. รอบเวลาปกติ (Scheduled Retraining)
* **ทุกสิ้นเดือน หรือ ทุกไตรมาส (Monthly / Quarterly):** รวบรวมข้อมูล Lead ที่ปิดการขายรอบล่าสุดเข้ามาเพิ่มใน Training Set เพื่อให้โมเดลทันต่อเหตุการณ์ปัจจุบัน

### 2. เมื่อเกิดการเปลี่ยนแปลงของข้อมูลนำเข้า (Data Drift / Covariate Shift)
* **เปิดช่องทางการตลาดใหม่:** เช่น จากเดิมมีแค่ Facebook, Google แล้วเริ่มทำการตลาดผ่าน TikTok Ads หรือการออกบูธนิทรรศการ ซึ่งพฤติกรรมลูกค้าช่องทางใหม่มีความแตกต่างอย่างมาก
* **ปรับโครงสร้างโปรโมชันครั้งใหญ่:** แคมเปญ Flash Sale ลดราคา 50–70% ซึ่งดึงดูดผู้สนใจกลุ่มใหม่ที่ไม่เคยมีในอดีต

### 3. เมื่อพฤติกรรมลูกค้าเปลี่ยนไป (Concept Drift)
* **อิทธิพลของฤดูกาล (Seasonality):** พฤติกรรมการซื้อช่วงเทศกาลปลายปี (Q4) กับช่วงกลางปี (Q2) มักแตกต่างกันอย่างสิ้นเชิง
* **การแข่งขันในตลาด:** เมื่อคู่แข่งเปิดตัวสินค้าใหม่ที่ดึงดูดใจกว่า ทำให้อัตรา Conversion Rate เดิมใช้ไม่ได้อีกต่อไป

### 4. ตัวชี้วัดประสิทธิภาพตกต่ำ (Performance Degradation Trigger)
* มีระบบตรวจสอบย้อนหลัง (Model Monitoring) รายเดือน หากพบว่า:
  * ค่า **ROC-AUC ลดลงต่ำกว่า $0.70$**
  * หรือค่า **Precision ลดลงมากกว่า $15\%$** เมื่อเทียบกับตอนเทรนครั้งแรก
  * ต้องสั่งรัน Script ฝึกสอนและปรับจูนพารามิเตอร์ (Re-tune Hyperparameters) ทันที

---

## 7. ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)

1. **ปัญหาการเริ่มต้นใหม่ (Cold-Start Problem):**
   * Lead ที่เพิ่งกรอกข้อมูลเข้ามาในนาทีแรกสุด ยังไม่มีประวัติการติดต่อใดๆ (`Activity_Count = 0`, `Engagement_Span = 0`)
   * โมเดลจะสามารถประเมินได้จาก `Source_Channel` และ `Discount_Rate` เท่านั้น ทำให้ Lead หน้าใหม่มีโอกาสเริ่มต้นที่ระดับ Warm หรือ Cold เสมอ จนกว่าเซลส์จะเริ่มโทรครั้งแรก
2. **ปัญหาความลำเอียงจากการเลือกปฏิบัติ (Feedback Loop / Selection Bias):**
   * หากพนักงานขายโทรหาเฉพาะกลุ่ม 🔥 **Hot Leads** และเพิกเฉยต่อกลุ่ม ❄️ **Cold Leads** โดยสิ้นเชิง
   * กลุ่ม Cold Leads ก็จะไม่มีทางปิดการขายได้เลย ส่งผลให้ในรอบการเทรนถัดไป โมเดลจะยิ่งจดจำว่าพฤติกรรมแบบ Cold Leads ไม่มีวันซื้อ (Self-fulfilling prophecy)
   * **แนวทางแก้ไข:** ต้องกำหนดโควตาให้สุ่มโทรหา Cold Leads ประมาณ $10\% - 15\%$ เพื่อนำข้อมูลจริงกลับมาทวนสอบโมเดล
3. **ปัญหาสหสัมพันธ์ไม่ใช่เหตุและผล (Correlation vs Causation):**
   * สถิติอาจชี้ว่า Lead ที่คุยกัน 5 ครั้งขึ้นไปมักจะซื้อ แต่ไม่ได้แปลว่า "การพยายามโทรตื๊อให้ครบ 5 ครั้ง จะบังคับให้ลูกค้าซื้อได้" ลูกค้าที่คุยบ่อยอาจเกิดจากเขามีความสนใจสูงอยู่แล้วแต่แรก

---

## 8. สรุปความเชื่อมโยงกับหน้าจอแอปพลิเคชัน (Streamlit UI Integration)

* **หน้างานขาย ([2_sales_followup.py](file:///c:/Users/momo/dev/dddsproject/pages/2_sales_followup.py)):**
  * แสดงตารางคิวงานประจำวันพร้อม Badge สี (🔥 แดง, 🌤 ส้ม, ❄️ ฟ้า)
  * เรียงลำดับจากคะแนนสูงสุดลงมา ช่วยให้ทีมขายไม่พลาดลูกค้าสำคัญ
* **หน้างานวิเคราะห์ ([6_analytics_dashboard.py](file:///c:/Users/momo/dev/dddsproject/pages/6_analytics_dashboard.py)):**
  * กราฟ ROC Curve และพื้นที่ใต้กราฟ (AUC)
  * ตาราง Confusion Matrix (เปรียบเทียบผลพยากรณ์ vs ความเป็นจริง)
  * แผนภูมิแท่ง Feature Importance แจกแจงปัจจัยขับเคลื่อนยอดขาย
  * เครื่องมือ Interactive Simulator สำหรับทดลองจำลองค่าเพื่อดูคะแนนพยากรณ์แบบ Real-time
