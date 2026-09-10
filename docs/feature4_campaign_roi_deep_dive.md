# 💰 คู่มือเจาะลึก Feature 4: Campaign Performance & Marketing ROI (0% – 100%)
## ระบบวิเคราะห์ผลตอบแทนการลงทุนแคมเปญ ท่อส่งการตลาด และทดสอบสมมติฐานทางสถิติ
**รายวิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)  
**อ้างอิงโค้ด:** `analytics/campaign_roi.py`, `db/schema.sql`, `pages/1_📢_Marketing.py`, `pages/6_📊_Analytics_Dashboard.py`

---

## 1. ที่มา ที่ไป และหลักคิดทางธุรกิจ (Problem & Business Motivation)

### 🔴 ปัญหาเดิมของฝ่ายการตลาดและผู้บริหาร (The Problem)
* **การวัดผลด้วยตัวเลขลวงตา (Vanity Metrics Trap):** ทีมการตลาดมักรายงานความสำเร็จด้วยยอดกดไลก์ ยอดวิว ยอดคลิก หรือจำนวนผู้สนใจ (Leads) ที่ลงทะเบียนเข้ามา แต่เมื่อผู้บริหารสอบถามว่า "เงินงบประมาณ 100,000 บาทที่จ่ายไป ได้กำไรกลับมากี่บาท?" กลับไม่สามารถตอบได้
* **การขาดความเชื่อมโยงระหว่างต้นทุนและรายได้จริง (Cost-to-Revenue Disconnect):**
  * ฝ่ายการตลาดบันทึกงบโฆษณาในระบบหนึ่ง
  * ฝ่ายขายออกใบเสนอราคาและบันทึกรายได้ในอีกระบบหนึ่ง
  * ทำให้ไม่ทราบว่ารายได้จากบิลขายแต่ละใบ เกิดจากอิทธิพลของแคมเปญใด
* **ไม่ทราบจุดรั่วไหลของลูกค้า (Funnel Leakage Blindness):** ไม่ทราบว่าผู้สนใจตกหล่นไปในขั้นตอนใด ระหว่างการติดต่อครั้งแรก การเสนอราคา หรือขั้นตอนการชำระเงิน
* **การตัดสินใจจัดสรรงบประมาณด้วยสัญชาตญาณ (Intuition-based Budgeting):** ผู้บริหารตัดสินใจเพิ่มหรือลดงบประมาณตามความรู้สึก โดยไม่มีการทดสอบทางสถิติว่าช่องทางใดมีประสิทธิภาพเหนือกว่าช่องทางอื่นจริงหรือไม่

### 💡 หลักคิดของโซลูชัน (The Core Concept)
* **Full-Funnel Closed-Loop Attribution:** เชื่อมโยงงบประมาณแคมเปญ (D5) ข้ามไปยังกระบวนการติดตามผู้สนใจ (D1) ใบเสนอราคา และบิลปิดการขายจริง (D2) เพื่อคำนวณตัวชี้วัดความคุ้มค่าทางการเงินสุทธิ (**ROI, ROAS, CAC, CPL**)
* **Marketing Funnel Analytics:** วิเคราะห์การแปลงสภาพของลูกค้าในแต่ละขั้นและคำนวณอัตราการตกหล่น (**% Drop-Off Rate**)
* **Statistical Rigor (Chi-Square Test of Independence):** ทำการทดสอบสมมติฐานทางสถิติเพื่อพิสูจน์ว่า อัตราการปิดการขายที่แตกต่างกันในแต่ละช่องทาง (Facebook, Google, LINE, Direct, Walk-in) เกิดจากคุณภาพที่แท้จริงของช่องทาง หรือเป็นเพียงความบังเอิญสุ่มทางสถิติ

---

## 2. สมมติฐานหลัก (Underlying Hypotheses & Assumptions)

1. **Direct First-Touch Attribution Model:**  
   ผู้สนใจที่ลงทะเบียนผ่าน `Campaign_ID` ใด เมื่อมีการแปลงสภาพเป็นคำสั่งซื้อสำเร็จในภายหลัง จะถือว่ามูลค่ายอดขายทั้งหมดนั้นเกิดขึ้นจากคุณูปการของแคมเปญดังกล่าว
2. **Channel Intent Divergence Hypothesis:**  
   ผู้สนใจจากช่องทางแบบค้นหาเจาะจง (Inbound Intent เช่น Google Search) มีอัตราการปิดการขาย (Conversion Rate) สูงกว่าช่องทางแบบผลักดันโฆษณา (Outbound Push เช่น Facebook Ads) อย่างมีนัยสำคัญ
3. **Statistical Independence Hypothesis ($H_0$ vs $H_1$):**  
   * **สมมติฐานว่าง ($H_0$):** ช่องทางการตลาดไม่มีผลต่ออัตราการปิดการขาย (Conversion Rate ในทุกช่องทางเท่ากันทางสถิติ)
   * **สมมติฐานทางเลือก ($H_1$):** ช่องทางการตลาดส่งผลต่ออัตราการปิดการขายอย่างมีนัยสำคัญ ($p\text{-value} < 0.05$)
4. **Economies of Scale & CAC Diminishing Returns:**  
   การเพิ่มงบประมาณในแคมเปญเดิมเกินจุดคุ้มค่า จะทำให้ต้นทุนต่อการได้มาซึ่งลูกค้าหนึ่งราย (`CAC`) สูงขึ้นเรื่อยๆ จากกลุ่มเป้าหมายที่อิ่มตัว

---

## 3. สถาปัตยกรรมข้อมูลและการเชื่อมโยงฐานข้อมูล (Data Architecture & Schema)

ระบบเชื่อมโยง 5 ตารางในฐานข้อมูลเชิงสัมพันธ์ OLTP ผ่าน View [`V_CAMPAIGN_ROI`](file:///c:/Users/momo/dev/dddsproject/db/schema.sql#L234-L247) และ Sub-queries:

```
+--------------------+           +--------------------+           +--------------------+
|   CAMPAIGN (D5)    |           |     LEAD (D1)      |           |     SALE (D2)      |
|--------------------|           |--------------------|           |--------------------|
| Campaign_ID (PK)   |1         *| Lead_ID (PK)       |1         *| Sale_ID (PK)       |
| Campaign_Name      |-----------| Campaign_ID (FK)   |-----------| Lead_ID (FK)       |
| Budget_Cost        |           | Source_Channel     |           | Sale_Status        |
| Start_Date         |           | Followup_Status    |           | Total_Amount       |
| End_Date           |           +--------------------+           | Confirmed_At       |
+--------------------+                                            +--------------------+
                                                                            1
                                                                            |
                                                                            *
                                                                  +--------------------+
                                                                  |  SALE_DETAIL (D2)  |
                                                                  |--------------------|
                                                                  | Detail_ID (PK)     |
                                                                  | Sale_ID (FK)       |
                                                                  | Product_ID (FK)    |
                                                                  | Quantity, Subtotal |
                                                                  +--------------------+
```

### คำสั่ง SQL สร้าง View ผลตอบแทนแคมเปญ (`db/schema.sql`)
```sql
CREATE VIEW V_CAMPAIGN_ROI AS
SELECT  c.Campaign_ID,
        c.Campaign_Name,
        c.Budget_Cost,
        COUNT(DISTINCT l.Lead_ID)  AS Total_Leads,
        COUNT(DISTINCT s.Lead_ID)  AS Converted_Leads,
        ROUND(100.0 * COUNT(DISTINCT s.Lead_ID) / NULLIF(COUNT(DISTINCT l.Lead_ID),0), 2) AS Conversion_Rate,
        ROUND(c.Budget_Cost / NULLIF(COUNT(DISTINCT l.Lead_ID),0), 2)  AS Cost_Per_Lead,
        COALESCE(SUM(s.Total_Amount),0) AS Revenue,
        ROUND((COALESCE(SUM(s.Total_Amount),0) - c.Budget_Cost) / NULLIF(c.Budget_Cost,0), 4) AS ROI
FROM CAMPAIGN c
LEFT JOIN LEAD l ON l.Campaign_ID = c.Campaign_ID
LEFT JOIN SALE s ON s.Lead_ID = l.Lead_ID AND s.Sale_Status = 'ปิดการขายสำเร็จ'
GROUP BY c.Campaign_ID;
```

### คำสั่ง SQL สกัด Marketing Funnel และยอดขายรายสินค้า (`analytics/campaign_roi.py`)
```sql
-- คำนวณ 4 ลำดับขั้นของท่อการตลาด (Funnel)
SELECT 'ผู้สนใจทั้งหมด' AS Stage, COUNT(*) AS N, 1 AS ord FROM LEAD
UNION ALL SELECT 'ได้รับการติดตาม', COUNT(DISTINCT Lead_ID), 2 FROM LEAD_ACTIVITY
UNION ALL SELECT 'ออกใบเสนอราคา',  COUNT(DISTINCT Lead_ID), 3 FROM SALE
UNION ALL SELECT 'ปิดการขายสำเร็จ', COUNT(DISTINCT Lead_ID), 4 FROM SALE WHERE Sale_Status='ปิดการขายสำเร็จ'
ORDER BY ord;
```

### พจนานุกรมสูตรคำนวณทางการเงินและการตลาด (Financial Metric Dictionary)

| ตัวชี้วัด | สูตรการคำนวณทางคณิตศาสตร์ | หน่วย | ความหมายเชิงธุรกิจ |
| :--- | :--- | :---: | :--- |
| **Conversion Rate** | $\frac{\text{Converted Leads}}{\text{Total Leads}} \times 100$ | % | สัดส่วนผู้สนใจที่สามารถปิดการขายได้สำเร็จ |
| **CPL (Cost Per Lead)** | $\frac{\text{Budget Cost}}{\text{Total Leads}}$ | บาท/คน | ต้นทุนเฉลี่ยในการได้มาซึ่งผู้สนใจ 1 ราย |
| **CAC (Acquisition Cost)** | $\frac{\text{Budget Cost}}{\text{Converted Leads}}$ | บาท/คน | ต้นทุนเฉลี่ยในการได้มาซึ่งลูกค้าจริง 1 ราย |
| **ROAS (Return on Ad Spend)**| $\frac{\text{Revenue}}{\text{Budget Cost}}$ | เท่า | ยอดขายรวมที่สร้างได้ต่อเงินงบประมาณ 1 บาท |
| **Marketing ROI** | $\frac{\text{Revenue} - \text{Budget Cost}}{\text{Budget Cost}} \times 100$ | % | กำไรสุทธิจากการลงทุนด้านการตลาด |
| **Average Deal Size** | $\frac{\text{Revenue}}{\text{Converted Leads}}$ | บาท/บิล | ขนาดมูลค่ายอดซื้อเฉลี่ยต่อคำสั่งซื้อ |

---

## 4. ขั้นตอนการพัฒนาระบบตั้งแต่ 0% ถึง 100% (End-to-End Pipeline)

```
[0% Aggregation] ➔ [25% Financial Metrics & Verdict] ➔ [50% Funnel Leakage] ➔ [75% Chi-Square Test] ➔ [100% Reallocation Decision]
```

### 🔹 ขั้นที่ 1 (0% – 25%): การเชื่อมต่อข้อมูลต้นทุนกับยอดขาย (Data Ingestion)
* รวมงบประมาณของแคมเปญจากตาราง `CAMPAIGN`
* เชื่อมโยงข้ามตารางแบบ Outer Join กับ `LEAD` และ `SALE` สถานะ `'ปิดการขายสำเร็จ'`
* นำค่าว่าง (NULL) มาแทนที่ด้วย `0` หรือ `pd.NA` เพื่อป้องกันข้อผิดพลาดกรณีหารด้วยศูนย์ (Division by Zero)

### 🔹 ขั้นที่ 2 (25% – 50%): การวิศวกรรมตัวชี้วัดและติดป้ายประเมินผล (Metric Engineering & Verdict)
ฟังก์ชัน `campaign_overview()` คำนวณตัวชี้วัดทางการเงินพร้อมติดป้ายกำกับตามเกณฑ์:

| เกณฑ์ประเมิน (`Verdict`) | ช่วงของค่า ROI (%) | คำแนะนำการบริหารจัดการ |
| :--- | :---: | :--- |
| ❌ **ขาดทุน** | $\text{ROI} < 0\%$ | รายได้น้อยกว่างบโฆษณา ควรหยุดแคมเปญหรือปรับปรุงกลุ่มเป้าหมาย |
| ⚠️ **พอไปได้** | $0\% \le \text{ROI} \le 100\%$ | คืนทุนหรือมีกำไรไม่เกิน 1 เท่าตัว ควรปรับจูนข้อความและราคา |
| ✅ **คุ้มค่ามาก** | $\text{ROI} > 100\%$ | กำไรเกินกว่าเท่าตัว แนะนำให้อัดฉีดงบประมาณเพิ่ม (Scale up) |

### 🔹 ขั้นที่ 3 (50% – 75%): การวิเคราะห์การรั่วไหลของท่อส่งลูกค้า (Marketing Funnel Analysis)
ฟังก์ชัน `funnel()` ทำการสกัดจำนวนผู้ใช้งานในแต่ละด่าน และคำนวณอัตราส่วน:
1. **สัดส่วนเทียบกับยอดรวมทั้งหมด (% of Total):**
   $$\text{Pct\_of\_Total}_i = \frac{N_i}{N_1} \times 100$$
2. **อัตราการหลุดจากท่อ (% Drop-Off):**
   $$\text{Drop\_Off}_i = \left( 1 - \frac{N_i}{N_{i-1}} \right) \times 100$$
* **การตรวจหาคอขวด (Bottleneck Detection):**
  * หากพบว่า Drop-off ระหว่างขั้นที่ 1 $\rightarrow$ 2 สูง: ทีมขายติดต่อกลับช้าเกินไป
  * หากพบว่า Drop-off ระหว่างขั้นที่ 3 $\rightarrow$ 4 สูง: ราคาสูงเกินไป หรือข้อเสนอในใบเสนอราคาไม่ดึงดูดพอ

### 🔹 ขั้นที่ 4 (75% – 90%): การทดสอบสมมติฐานทางสถิติ (Statistical Hypothesis Testing)
เพื่อตอบคำถามว่า "ช่องทาง Google ปิดการขายได้ 25% ในขณะที่ Facebook ปิดได้ 12% ความต่างนี้เกิดขึ้นจริง หรือเป็นแค่เรื่องบังเอิญ?"  
ฟังก์ชัน `channel_significance()` สร้างตารางการแจกแจงแบบไขว้ (Contingency Table):

```
                  ปิดการขายสำเร็จ (Converted)    ไม่สนใจ/หลุด (Not Converted)
Facebook Ads                 a                                b
Google Search                c                                d
LINE Official                e                                f
Walk-in / Direct             g                                h
```

ใช้การทดสอบ **Chi-Square Test of Independence ($\chi^2$)** จากไลบรารี `scipy.stats`:
$$\chi^2 = \sum \frac{(O - E)^2}{E}$$
* $O$: ความถี่ที่สังเกตได้จริง (Observed Frequency)
* $E$: ความถี่ที่คาดหวังตามความน่าจะเป็นสถิติ (Expected Frequency)
* **การแปลผล ($p\text{-value}$):**
  * ถ้า $p < 0.05$: **ปฏิเสธสมมติฐานว่าง ($H_0$)** สรุปว่า ช่องทางการตลาดมีผลต่อการปิดการขายอย่างมีนัยสำคัญทางสถิติ
  * ถ้า $p \ge 0.05$: ยอมรับสมมติฐานว่าง แสดงว่าความแตกต่างอาจเกิดจากความแปรปรวนสุ่มของข้อมูล

### 🔹 ขั้นที่ 5 (90% – 100%): การจัดสรรงบประมาณและการตัดสินใจเชิงกลยุทธ์ (Budget Optimization)
* เชื่อมโยงข้อมูลยอดขายรายเดือน (`monthly_trend()`) และรายการสินค้าขายดี (`top_products()`)
* แสดงคำแนะนำในการโยกย้ายงบประมาณ (Capital Reallocation): ปรับลดยอดเงินจากแคมเปญที่ "❌ ขาดทุน" แล้วนำไปเพิ่มให้กับแคมเปญที่ "✅ คุ้มค่ามาก"

---

## 5. สิ่งที่ต้องมีก่อนเริ่มใช้งาน (Prerequisites)

1. **วินัยในการลงงบประมาณการตลาด:**
   * ตาราง `CAMPAIGN` ต้องระบุฟิลด์ `Budget_Cost` เป็นยอดเงินจริง ไม่ปล่อยให้เป็นค่าว่างหรือ 0
2. **การผูกโยงข้อมูลการปิดการขาย:**
   * คำสั่งซื้อในตาราง `SALE` ต้องระบุ `Lead_ID` ที่เชื่อมโยงกลับไปยัง `Campaign_ID` ได้อย่างสมบูรณ์
3. **ปริมาณกลุ่มตัวอย่างสำหรับ Chi-Square:**
   * ทุกช่องในตาราง Contingency Table ควรมีความถี่ที่คาดหวัง ($E$) อย่างน้อย 5 ตัวอย่างขึ้นไป เพื่อให้ค่าสถิติ $\chi^2$ มีความแม่นยำ

---

## 6. ต้องประมวลผลใหม่เมื่อไร? (Execution Schedule & Audit)

1. **การคำนวณแบบ Real-time / On-demand:**
   * ตัวเลขสถิติใน Dashboard จะคำนวณอัตโนมัติทุกครั้งที่มีคำสั่งซื้อใหม่ปิดการขายสำเร็จ ทำให้ทีมการตลาดเห็นผลตอบแทนแบบ Real-time
2. **การสรุปผลรอบแคมเปญ (Post-Mortem Campaign Review):**
   * รันสรุปผลทางการเมื่อสิ้นสุดวันที่ `End_Date` ของแคมเปญ เพื่อจัดทำรายงานเสนอคณะกรรมการบริหาร
3. **การทดสอบความแตกต่างของช่องทางประจำไตรมาส (Quarterly A/B Audit):**
   * รันการทดสอบ $\chi^2$ ซ้ำทุกไตรมาส เพื่อดูว่าช่องทางใหม่ๆ ที่เปิดเริ่มมีนัยสำคัญทางสถิติหรือยัง

---

## 7. ข้อจำกัดและความเสี่ยง (Limitations & Edge Cases)

1. **ข้อจำกัดของ First-Touch Attribution:**
   * ระบบให้เครดิตยอดขายแก่แคมเปญที่ Lead เข้ามาครั้งแรก 100% ซึ่งอาจไม่สะท้อนลูกค้าที่เห็นแคมเปญอื่นซ้ำก่อนตัดสินใจซื้อ (Multi-Touch Attribution Blindspot)
2. **วงจรการขายที่ยาวนานในธุรกิจ B2B (Sales Cycle Lag):**
   * ในการขายระบบขนาดใหญ่ที่ต้องใช้เวลาเจรจา 3–6 เดือน แคมเปญที่ปล่อยในเดือนแรกจะมียอด ROI ติดลบ (-100%) ในช่วงเริ่มต้น จนกว่าคำสั่งซื้อจะปิดสำเร็จในอนาคต จึงต้องพิจารณาร่วมกับ Funnel
3. **ต้นทุนแฝงที่ไม่ได้รวมใน Budget:**
   * `Budget_Cost` ปัจจุบันคิดเฉพาะค่ายิงโฆษณาและงบกิจกรรม ไม่ได้รวมเงินเดือนพนักงานหรือค่าจัดทำสื่อกราฟิก (Overhead Costs)

---

## 8. สรุปความเชื่อมโยงกับหน้าจอแอปพลิเคชัน (Streamlit UI Integration)

* **หน้างบการตลาด ([1_📢_Marketing.py](file:///c:/Users/momo/dev/dddsproject/pages/1_📢_Marketing.py)):**
  * ฟอร์มสร้างแคมเปญใหม่พร้อมระบุงบประมาณและช่องทาง
  * ตารางสรุปแคมเปญปัจจุบันพร้อมแสดงจำนวน Lead ที่ได้มา
* **หน้าแดชบอร์ดวิเคราะห์ ([6_📊_Analytics_Dashboard.py](file:///c:/Users/momo/dev/dddsproject/pages/6_📊_Analytics_Dashboard.py) — แท็บ 4):**
  * การ์ด KPI ทางการเงิน 4 มิติ: Total Spend, Total Revenue, Net ROI %, Average ROAS
  * ตารางเปรียบเทียบแคมเปญพร้อม Badge ประเมินผล (✅ คุ้มค่า, ⚠️ พอไปได้, ❌ ขาดทุน)
  * กราฟแท่งเปรียบเทียบ Conversion Rate และ Revenue per Lead รายช่องทาง
  * แผนภูมิ Funnel แสดงการตกหล่นของลูกค้าทั้ง 4 ขั้นตอน
  * กล่องข้อความแสดงผลการทดสอบสมมติฐานทางสถิติ Chi-Square ($\chi^2$, $p\text{-value}$ และข้อสรุปภาษาไทย)
  * กราฟแนวโน้มยอดขายรายเดือนแยกตามแคมเปญ และตาราง 10 สินค้าขายดี
