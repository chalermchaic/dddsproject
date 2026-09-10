# 📊 คู่มือเจาะลึก Feature 2: Customer RFM Segmentation & K-Means (0% – 100%)
## ระบบจัดเกรดและแบ่งกลุ่มลูกค้าเชิงกลยุทธ์ด้วย RFM Model และ Unsupervised Machine Learning
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**อ้างอิงโค้ด:** `analytics/rfm_segmentation.py`, `db/schema.sql`, `pages/1_📢_Marketing.py`, `pages/4_👤_Customer_Profile.py`, `pages/6_📊_Analytics_Dashboard.py`

---

## 1. ที่มา ที่ไป และหลักคิดทางธุรกิจ (Problem & Business Motivation)

### 🔴 ปัญหาเดิมขององค์กร (The Problem)
* **การทำการตลาดแบบเหวี่ยงแห (Mass Marketing Inefficiency):** เมื่อองค์กรต้องการจัดกิจกรรมส่งเสริมการขาย มักส่งข้อความหรือโปรโมชันเดียวกันให้กับลูกค้าทุกคนในฐานข้อมูล ส่งผลให้ลูกค้ารู้สึกรำคาญ (Spam Fatigue) และอัตราการตอบรับต่ำมาก
* **ไม่เห็นคุณค่าที่แท้จริงของลูกค้า (Customer Blindness):** องค์กรไม่สามารถระบุได้ว่าลูกค้าคนใดเป็น "เสาหลักสร้างกำไร" (High-value Champions) และคนใดเป็น "ลูกค้าที่กำลังจะตีจาก" (At-Risk Churners) ทำให้สูญเสียลูกค้าชั้นดีไปโดยไม่รู้ตัว
* **ทรัพยากรการตลาดและการบริการสูญเปล่า:** การจัดสรรงบส่วนลดให้ลูกค้าที่ไม่จำเป็นต้องลดราคาก็ซื้ออยู่แล้ว หรือการทุ่มเทดูแลลูกค้าที่เข้ามาซื้อสินค้าลดราคาเพียงครั้งเดียวแล้วไม่เคยกลับมาอีก

### 💡 หลักคิดของโซลูชัน (The Core Concept)
* ประยุกต์ใช้ทฤษฎีการตลาดเชิงปริมาณ **RFM Analysis (Recency, Frequency, Monetary)** ร่วมกับ **Unsupervised Machine Learning (K-Means Clustering)**
* **RFM Framework:**
  1. **Recency ($R$):** ซื้อล่าสุดเมื่อไร? (ยิ่งซื้อเร็ว ยิ่งผูกพันสูง)
  2. **Frequency ($F$):** ซื้อบ่อยแค่ไหน? (ซื้อซ้ำสะท้อนความภักดีต่อแบรนด์)
  3. **Monetary ($M$):** จ่ายรวมไปเท่าไร? (ยอดเงินรวมสะท้อนกำลังซื้อและคุณค่าต่อธุรกิจ)
* ผสมผสาน **Rule-based Scoring (1–5 Quintiles)** เพื่อให้ฝ่ายธุรกิจเข้าใจง่าย เข้ากับ **K-Means Clustering** บนสเกล Log-transformed เพื่อค้นพบโครงสร้างกลุ่มพฤติกรรมธรรมชาติที่ซ่อนอยู่ในข้อมูล
* จำแนกลูกค้าออกเป็น **6 กลุ่มยุทธศาสตร์ (Strategic Segments)** พร้อมแผนปฏิบัติการเฉพาะกลุ่ม (Actionable Next Steps)

---

## 2. สมมติฐานหลัก (Underlying Hypotheses & Assumptions)

1. **Recency Decay Hypothesis (เวลาผ่านไป ความสนใจยิ่งลดลง):**  
   ลูกค้ายิ่งมีระยะเวลาห่างจากการซื้อครั้งล่าสุดสั้นเท่าไร ยิ่งมีโอกาสเปิดรับข้อเสนอและกลับมาซื้อซ้ำสูงกว่าลูกค้าที่หยุดซื้อไปเป็นเวลานานตามหลัก Exponential Decay
2. **Frequency Habituation Hypothesis (การซื้อซ้ำสะท้อนความภักดี):**  
   ความถี่ในการซื้อมีความสัมพันธ์เชิงบวกกับความเชื่อมั่นในสินค้า ลูกค้าที่ซื้อซ้ำ $\ge 3$ ครั้ง มีแนวโน้มย้ายค่ายยากกว่าลูกค้าใหม่
3. **Pareto Principle (กฎ 80/20 ของรายได้):**  
   รายได้ประมาณ 80% ของธุรกิจ ถูกสร้างขึ้นจากฐานลูกค้าชั้นยอดเพียง 20% การรักษาลูกค้ากลุ่มนี้จึงสร้างผลกระทบต่อความอยู่รอดของธุรกิจสูงที่สุด
4. **Behavioral Clustering Convergence (การรวมกลุ่มทางสถิติ):**  
   พฤติกรรมการซื้อไม่ได้กระจายตัวแบบสุ่ม แต่จะเกาะกลุ่มกันตามมิติคุณค่าและระยะเวลา ซึ่งสามารถจำแนกจุดศูนย์กลาง (Centroids) ด้วยอัลกอริทึม K-Means ได้อย่างมีนัยสำคัญ

---

## 3. สถาปัตยกรรมข้อมูลและการเชื่อมโยงฐานข้อมูล (Data Architecture & Schema)

ระบบดึงข้อมูลจากตารางธุรกรรมเชิงสัมพันธ์ (OLTP) ผ่าน View พิเศษ [`V_CUSTOMER_RFM`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L210-L219):

```
+--------------------+            +--------------------+
|   CUSTOMER (D3)    |            |     SALE (D2)      |
|--------------------|            |--------------------|
| Customer_ID (PK)   |1          *| Sale_ID (PK)       |
| Customer_Type      |------------| Lead_ID (FK)       |
| Company_Name       |            | Sale_Status        |
| Membership_Date    |            | Total_Amount       |
+--------------------+            | Confirmed_At       |
                                  +--------------------+
```

### คำสั่ง SQL สร้างฐานข้อมูล RFM (`db/schema.sql`)
```sql
CREATE VIEW V_CUSTOMER_RFM AS
SELECT  cu.Customer_ID,
        cu.Customer_Type,
        CAST(julianday('now') - julianday(MAX(s.Confirmed_At)) AS INTEGER) AS Recency_Days,
        COUNT(s.Sale_ID)      AS Frequency,
        SUM(s.Total_Amount)   AS Monetary
FROM CUSTOMER cu
JOIN SALE s ON s.Lead_ID = cu.Lead_ID AND s.Sale_Status = 'ปิดการขายสำเร็จ'
GROUP BY cu.Customer_ID;
```

### พจนานุกรมข้อมูล (Feature Dictionary)

| ตัวแปร | ประเภท | การคำนวณใน SQL | ความหมายทางธุรกิจ |
| :--- | :--- | :--- | :--- |
| **`Recency_Days`** | Integer | `julianday('now') - julianday(MAX(Confirmed_At))` | จำนวนวันนับจากคำสั่งซื้อล่าสุดจนถึงปัจจุบัน (ค่ายิ่งน้อย ยิ่งดี) |
| **`Frequency`** | Integer | `COUNT(s.Sale_ID)` | จำนวนครั้งรวมที่สั่งซื้อสำเร็จ |
| **`Monetary`** | Real | `SUM(s.Total_Amount)` | ยอดเงินรวมทั้งหมดที่ลูกค้าจ่ายให้กับบริษัท (บาท) |
| **`Customer_Type`**| Text | `cu.Customer_Type` | ประเภทลูกค้า (องค์กร B2B / บุคคลทั่วไป B2C) |

---

## 4. ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)

```
[0% Aggregation] ➔ [25% Quintile Scoring] ➔ [50% Log-Transform & Scale] ➔ [75% K-Means & Elbow] ➔ [90% Segmentation] ➔ [100% Campaign Action]
```

### 🔹 ขั้นที่ 1 (0% – 25%): การประมวลผลข้อมูลดิบ (Data Ingestion & Cleaning)
* ดึงข้อมูลผ่าน `load_rfm()` จากตาราง `V_CUSTOMER_RFM`
* ทำการ Imputation กรณีที่ `Monetary` เป็นค่าว่างด้วย `0.0`
* กรองเฉพาะลูกค้าที่มีการสั่งซื้อเสร็จสมบูรณ์แล้ว (`Sale_Status = 'ปิดการขายสำเร็จ'`)

### 🔹 ขั้นที่ 2 (25% – 50%): การคำนวณคะแนน Quintile (1–5 Scoring)
ใช้การตัดแบ่งเปอร์เซ็นไทล์ 5 ลำดับเท่าๆ กัน (`pd.qcut`) ผ่านฟังก์ชัน `_score()`:
* **Recency Score ($R$):** กลับด้านคะแนน (`reverse=True`) เพราะวันยิ่งน้อยคือเพิ่งซื้อ แสดงว่ามีคะแนนสูงสุด ($5 =$ เพิ่งซื้อภายในช่วงเวลาสั้นที่สุด, $1 =$ หยุดซื้อไปนานที่สุด)
* **Frequency Score ($F$):** ให้คะแนนตามความถี่ ($5 =$ ซื้อบ่อยที่สุด, $1 =$ ซื้อน้อยที่สุด)
* **Monetary Score ($M$):** ให้คะแนนตามยอดเงิน ($5 =$ จ่ายสูงสุด, $1 =$ จ่ายต่ำสุด)
* รวมคะแนนสร้างรหัสพฤติกรรม `RFM_Cell` เช่น `'555'` (แชมเปียนส์) หรือ `'111'` (กลุ่มที่หยุดซื้อไปแล้ว) และคะแนนรวม `RFM_Total = R + F + M` (3 ถึง 15 คะแนน)

### 🔹 ขั้นที่ 3 (50% – 75%): การจัดกลุ่มด้วย K-Means Clustering (Unsupervised ML)
เนื่องจากพฤติกรรมการซื้อของลูกค้ามักมีการกระจายตัวแบบเบ้ขวาอย่างรุนแรง (Positive / Right-skewed Distribution) ลูกค้าส่วนใหญ่ซื้อน้อยแต่นานๆ ทีจะมีลูกค้ารายใหญ่ซื้อยอดมหาศาล จึงต้องผ่านกระบวนการคณิตศาสตร์:
1. **Log-Transformation:** ใช้ $\ln(x + 1)$ ด้วย `np.log1p` บนตัวแปรทั้งสาม เพื่อปรับการกระจายตัวให้เข้าใกล้ Normal Distribution:
   $$X_{\text{trans}} = [\ln(\text{Recency} + 1), \ln(\text{Frequency} + 1), \ln(\text{Monetary} + 1)]$$
2. **Feature Standardization ($Z$-Score):**
   $$z = \frac{x - \mu}{\sigma}$$
   เพื่อให้ทั้งสามมิติมีน้ำหนักเท่ากันในทางเรขาคณิต (Euclidean Distance)
3. **K-Means Optimization:**
   * คำนวณหาจำนวนกลุ่มที่เหมาะสม ($k$) ด้วย **Elbow Method (Inertia/WCSS)**:
     $$\text{WCSS} = \sum_{i=1}^{k} \sum_{x \in C_i} ||x - \mu_i||^2$$
   * ตรวจสอบความหนาแน่นและการแยกของกลุ่มด้วย **Silhouette Score ($s$)**:
     $$s = \frac{b - a}{\max(a, b)}$$
     *(ในระบบกำหนดค่ามาตรฐานที่ $k=4$ ซึ่งให้ค่า Silhouette ที่เสถียรและตีความได้ง่าย)*

### 🔹 ขั้นที่ 4 (75% – 90%): การจำแนกกลุ่มเชิงกลยุทธ์ (Strategic Segmentation)
ประยุกต์ใช้ Business Matrix จัดกลุ่มลูกค้าออกเป็น 6 เซกเมนต์หลัก ผ่านฟังก์ชัน `_label()`:

```
Recency (สูง)
  ^
  | [New Customers]          [Champions]
  | (R>=4, F<=2)             (R>=4, F>=4, M>=4)
  | 
  | [Potential]              [Loyal Customers]
  | (R>=3, M>=3)             (R>=3, F>=3)
  | 
  | [Lost]                   [At Risk]
  | (คะแนนต่ำทุกด้าน)          (R<=2, F>=3)
  +---------------------------------------------> Frequency / Monetary (สูง)
```

| เซกเมนต์ (Segment) | เงื่อนไขคะแนน (Logic) | ความหมายทางพฤติกรรม |
| :--- | :--- | :--- |
| 👑 **Champions** | $R \ge 4 \land F \ge 4 \land M \ge 4$ | ซื้อล่าสุดเร็ว ซื้อบ่อยมาก มียอดซื้อสูงสุด เป็นเสาหลักรายได้ |
| ⭐ **Loyal Customers** | $R \ge 3 \land F \ge 3$ | ซื้อสม่ำเสมอ เชื่อมั่นในสินค้า ตอบรับกิจกรรมของบริษัทอย่างดี |
| 🌱 **New Customers** | $R \ge 4 \land F \le 2$ | ลูกค้าใหม่ที่เพิ่งซื้อครั้งแรก อยู่ในช่วงสร้างความประทับใจ |
| 💡 **Potential** | $R \ge 3 \land M \ge 3$ | เพิ่งซื้อและมียอดซื้อสูง มีศักยภาพที่จะดันขึ้นเป็น Loyal หรือ Champion |
| ⚠️ **At Risk** | $R \le 2 \land F \ge 3$ | **จุดเตือนภัย:** เคยซื้อบ่อยมาก แต่เริ่มหายไปนาน เสี่ยง Churn |
| 💤 **Lost** | ไม่เข้าเงื่อนไขข้างต้น ($R \le 2, F \le 2$) | หยุดซื้อไปนานมาก ยอดซื้อต่ำ หลุดออกจากวงจรธุรกิจ |

### 🔹 ขั้นที่ 5 (90% – 100%): การเปลี่ยนผลวิเคราะห์เป็นการปฏิบัติงาน (Actionable Next Steps)

| เซกเมนต์ | แผนปฏิบัติการที่ระบบแนะนำ (`ACTION`) | เครื่องมือส่งเสริมการตลาด |
| :--- | :--- | :--- |
| **Champions** | มอบสิทธิ์ VIP / เชิญร่วมโปรแกรมทดลองสินค้าใหม่ / เสนอบริการเฉพาะบุคคล | สิทธิ์ Exclusive & Personal Account Manager |
| **Loyal Customers**| โปรแกรมสะสมแต้ม (Loyalty Points) / แนะนำสินค้าเสริม (Cross-sell) | แคมเปญแนะนำเพื่อน (Referral Rewards) |
| **New Customers** | ติดตามความพึงพอใจหลังส่งมอบ (Onboarding) / แนะนำวิธีใช้สินค้า | ส่งคู่มือและคูปองส่วนลดซื้อครั้งที่สอง |
| **Potential** | ส่งข้อเสนอ Membership Upgrade / แนะนำสินค้าพรีเมียมรุ่นสูงกว่า | ข้อเสนอ Bundle Deal จำกัดเวลา |
| **At Risk** | **โทรติดตามด่วน:** สอบถามปัญหาการใช้งาน พร้อมมอบส่วนลดพิเศษเพื่อดึงกลับ | ข้อเสนอ "เราคิดถึงคุณ" (Special Win-back Discount) |
| **Lost** | แคมเปญ Re-engagement ต้นทุนต่ำทางอีเมล/SMS / สำรวจสาเหตุที่เลิกใช้ | แบบสอบถาม Exit Survey แลกของรางวัล |

---

## 5. สิ่งที่ต้องมีก่อนเริ่มใช้งาน (Prerequisites)

1. **ความถูกต้องของประวัติคำสั่งซื้อ:**
   * ตาราง `SALE` ต้องมีการบันทึกเวลาปิดการขาย (`Confirmed_At`) และยอดเงินสุทธิ (`Total_Amount`) อย่างถูกต้อง
2. **ปริมาณลูกค้าขั้นต่ำสำหรับ K-Means:**
   * ระบบกำหนดเงื่อนไขความปลอดภัย: หากมีลูกค้าน้อยกว่า $k \times 3$ (เช่น สำหรับ $k=4$ ต้องมีอย่างน้อย 12 ราย) ระบบจะข้าม K-Means แล้วใช้ Rule-based Segmentation อย่างเดียว เพื่อป้องกันปัญหา Overfitting ในข้อมูลขนาดเล็ก

---

## 6. ต้องคำนวณ/ประมวลผลใหม่เมื่อไร? (Execution & Retraining Strategy)

1. **การคำนวณคะแนนและจัดกลุ่ม (Daily Batch Scoring):**
   * ควรตั้งเวลาคำนวณคะแนนใหม่ทุกเที่ยงคืน (Daily Cron Job) เนื่องจากค่า `Recency_Days` เพิ่มขึ้น 1 วันทุกวัน ทำให้สถานะของลูกค้าเคลื่อนที่ไปตามกาลเวลา
2. **การ Re-fit โมเดล K-Means (Quarterly Re-calibration):**
   * ควรสั่ง Re-fit โมเดลและคำนวณ Centroids ใหม่ทุกไตรมาส (3 เดือน) หรือเมื่อ:
     * องค์กรมีการปรับฐานราคาสินค้าหลัก
     * มีการขยายตลาดสู่กลุ่มลูกค้าใหม่ (เช่น เพิ่มสายผลิตภัณฑ์ B2B Enterprise)
3. **การตรวจสอบ Silhouette Score Degradation:**
   * หากค่า Silhouette Score ของการจัดกลุ่มตกลงต่ำกว่า $0.35$ แสดงว่าการแบ่งกลุ่มเริ่มทับซ้อนกัน ต้องทำการหาค่า $k$ ใหม่ผ่าน Elbow Curve

---

## 7. ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)

1. **ลูกค้ายอดใหญ่ซื้อครั้งเดียว (High-ticket One-off Buyers):**
   * ลูกค้าที่ซื้อสินค้าราคาสูงเพียงครั้งเดียว เช่น งานระบบ Enterprise ยอด 500,000 บาท จะได้ค่า $M=5$ แต่ $F=1$ ระบบอาจจัดเข้ากลุ่ม Potential แทนที่จะเป็น Champion ฝ่ายขายจึงต้องพิจารณาประกอบกับบริบทสัญญา
2. **ผลกระทบจากฤดูกาล (Seasonality Distortion):**
   * ลูกค้าธุรกิจที่สั่งซื้อสินค้าเฉพาะช่วงเทศกาลปีใหม่ (ซื้อปีละครั้ง ยอดใหญ่) ในช่วงไตรมาส 3 ค่า Recency จะตกไปอยู่ที่ $R=1$ ทำให้ถูกจัดเป็น At Risk ทั้งที่ยังเป็นลูกค้าประจำรอบปี
3. **ปัญหาการผูกขาดรายได้ (Revenue Concentration Risk):**
   * ฟังก์ชัน `segment_summary()` ช่วยคำนวณ `Revenue_Share_%` หากพบว่ากลุ่ม Champions มีลูกค้าเพียง 2% แต่สร้างรายได้ 80% องค์กรจะมีความเสี่ยงสูงมากหากลูกค้ากลุ่มนี้หลุดไป

---

## 8. สรุปความเชื่อมโยงกับหน้าจอแอปพลิเคชัน (Streamlit UI Integration)

* **หน้าข้อมูลลูกค้า ([4_👤_Customer_Profile.py](file:///c:/Users/momo/dev/dddsproject/pages/4_👤_Customer_Profile.py)):**
  * แสดง Badge สีระบุกลุ่ม RFM ของลูกค้าแต่ละราย พร้อมค่า Recency, Frequency, Monetary ชัดเจน
  * แสดงข้อความกลยุทธ์ที่แนะนำสำหรับลูกค้ารายนั้นๆ
* **หน้างบการตลาด ([1_📢_Marketing.py](file:///c:/Users/momo/dev/dddsproject/pages/1_📢_Marketing.py)):**
  * ตัวกรองดึงรายชื่อลูกค้าตามเซกเมนต์ (เช่น เลือกลูกค้ากลุ่ม "At Risk" ทั้งหมด) เพื่อกดส่งแคมเปญโปรโมชันกระตุ้นยอดขาย
* **หน้าแดชบอร์ดวิเคราะห์ ([6_📊_Analytics_Dashboard.py](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py) — แท็บ 2):**
  * แผนภูมิ 3 มิติ (3D Scatter Plot) แสดงพิกัดลูกค้าในแกน Recency, Frequency, Monetary
  * แผนภูมิแท่งสรุปสัดส่วนลูกค้าและส่วนแบ่งรายได้ตามเซกเมนต์ (Revenue Share Analysis)
  * กราฟ Elbow Curve และ Silhouette Analysis สำหรับนักวิทยาศาสตร์ข้อมูลตรวจสอบความเหมาะสมของกลุ่ม K-Means
