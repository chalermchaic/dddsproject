# 🧪 แผนทดสอบเพิ่มเติม (Additional Test Coverage Plan)

> **บริบท:** จากการทบทวนและตรวจสอบชุดทดสอบที่มีอยู่จริงในระบบ (`tests/`, `analytics/`, `pages/`, `db/schema.sql`) เทียบกับกลุ่มงานทดสอบที่กำหนดไว้ (Unit test DS / Regression 2 บั๊ก / ขยาย E2E ครบโมดูล / RBAC+Index) พบว่า **3 ใน 4 กลุ่มมีการทดสอบครอบคลุมอยู่แล้วในโค้ด** เอกสารนี้จึงเน้นการพัฒนาชุดทดสอบเพิ่มเติมเฉพาะช่องว่างที่ยังขาดอยู่ เพื่อให้ระบบมีความสมบูรณ์สูงสุดตามข้อกำหนดเชิงวิศวกรรมข้อมูล

---

## 1. ผลตรวจสอบสถานะปัจจุบัน (Audit Result)

| กลุ่ม | สถานะ | หลักฐาน (ไฟล์ + เทสต์) |
|---|:---:|---|
| Regression: `pages/1_marketing.py` NA-crash (`TypeError: boolean value of NA is ambiguous`) | ✅ **มีแล้ว** | `tests/test_dfd_flows.py::test_1_1_create_campaign` — สร้างแคมเปญ 0-lead แล้วโหลดหน้าซ้ำ พร้อมคอมเมนต์ "Regression check: Ensure Tab 1 renders scatter plot cleanly with 0-lead campaign" |
| Regression: `V_SERVICE_HEALTH` fan-out bug | ✅ **มีแล้ว** | `tests/test_dfd_flows.py::test_5_3_service_health_view_no_fanout` — เทียบค่าจาก View กับค่าจริงที่นับตรงจากตาราง `TICKET`/`TICKET_MESSAGE` |
| RBAC (role ที่อนุญาต/ไม่อนุญาตเข้าแต่ละหน้า) | ✅ **มีแล้ว** | `tests/test_smoke.py::test_allowed_roles_load` และ `test_denied_roles_blocked` — วนทุกหน้า × ทุก role จริง |
| E2E functional ครบทุกโมดูล (ไม่ใช่แค่ screenshot) | ✅ **มีแล้วเป็นส่วนใหญ่** | `tests/test_dfd_flows.py` — 16 เทสต์ (1 เทสต์ = 1 กิจกรรมตาม DFD, ขับผ่าน Streamlit `AppTest` จริงแล้ว assert สถานะใน `db/crm.db`) + `tests/test_demo_flow.py` (7 ขั้นตอน) + `tests/e2e/` (Playwright screenshot evidence 12+ ภาพ) |
| **Unit test ระดับฟังก์ชัน/สูตรของโมเดล Data Science ทั้ง 4 ตัว** | ✅ **เสร็จสมบูรณ์** | `tests/test_analytics_units.py` (9 passed) — ทดสอบ `_label()`, `_score()`, `_norm()`, `WEIGHTS`, `grade()`, `channel_significance()` ครบทุกเงื่อนไขและ edge case |
| **ฟอร์มออกใบเสนอราคา (Process 2.3) ผ่าน UI จริง** | ✅ **เสร็จสมบูรณ์** | `tests/e2e/test_quotation_form_e2e.py` (1 passed) — ขับผ่าน Playwright เบราว์เซอร์จริง เลือกสินค้า multiselect 2 รายการ ตรวจสอบการคำนวณยอดสุทธิ/ส่วนลด กดยืนยัน และ assert แถวใหม่ใน SQLite `SALE` / `SALE_DETAIL` |
| Index/Speed proof (query plan) | ✅ **เสร็จสมบูรณ์** | `scripts/benchmark_index_usage.py` — สคริปต์รัน `EXPLAIN QUERY PLAN` ตรวจสอบการทำงานของ B-Tree Index ทุกตัว และสร้างเอกสารสรุป `docs/INDEX_QUERY_PLAN_REPORT.md` เรียบร้อย |

**สรุป:** ดำเนินการเพิ่มชุดทดสอบครบทั้ง 3 ส่วน (2.1, 2.2, 2.3) เรียบร้อยแล้ว — ทั้งหมดเป็นการ **เพิ่มไฟล์ทดสอบใหม่เท่านั้น ไม่แก้โค้ดโปรแกรมเดิมแม้แต่บรรทัดเดียว (Zero Application Code Modification)**

---

## 2. แผนงานที่จะเพิ่ม (Actionable Plan)

### 2.1 Unit Test สำหรับฟังก์ชันแกนของ Data Science — ไฟล์ใหม่ `tests/test_analytics_units.py`

เหตุผล: Data Science/ML/AI คือ **Focus หลักของโครงงาน** (ตามข้อเสนอโครงงาน `DDDS_Project_Proposal.md`) แต่ยังไม่มีเทสต์ยืนยัน "ความถูกต้องของสูตร/ตรรกะ" โดยตรง — เทสต์กลุ่มนี้ยืนยันด้วย input ที่กำหนดเองแล้วรู้ผลลัพธ์ที่ถูกต้องแน่นอน (ไม่ต้องพึ่งฐานข้อมูลจริง):

| Test case | ฟังก์ชันที่ทดสอบ | ตัวอย่าง input → expected output |
|---|---|---|
| `test_rfm_label_boundaries` | `analytics.rfm_segmentation._label(r, f, m)` | `(5,5,5)` → `"Champions"`, `(3,3,2)` → `"Loyal Customers"`, `(5,1,1)` → `"New Customers"`, `(3,1,4)` → `"Potential"`, `(1,3,1)` → `"At Risk"`, `(1,1,1)` → `"Lost"` — ไล่ทุกเงื่อนไขใน if/elif ให้ครบ |
| `test_rfm_score_quintile` | `analytics.rfm_segmentation._score(series, reverse)` | Series สังเคราะห์ 10-20 ค่า → assert ได้คะแนน 1-5 ครบ, `reverse=True` ต้องกลับทิศ (ค่าน้อยสุด → คะแนน 5) |
| `test_churn_norm_range` | `analytics.churn_health._norm(s, invert, cap)` | Series สังเคราะห์ → assert ผลลัพธ์อยู่ในช่วง `[0,1]` เสมอ, `invert=True` ต้องสลับทิศ, ทดสอบ edge case ที่ `hi == lo` (ต้องได้ 0.5 ทุกตัวตามโค้ด) |
| `test_churn_weights_sum_100` | `analytics.churn_health.WEIGHTS` | `assert sum(WEIGHTS.values()) == 100` — กันคนแก้สูตรแล้วน้ำหนักไม่ครบ 100 ในอนาคต |
| `test_lead_scoring_grade_boundaries` | `analytics.lead_scoring.grade(p)` | `grade(0.70)` → `"🔥 Hot"`, `grade(0.69)` → `"🌤 Warm"`, `grade(0.40)` → `"🌤 Warm"`, `grade(0.39)` → `"❄️ Cold"`, `grade(0.0)` / `grade(1.0)` → ค่าขอบสุดสองด้าน (ตรงตามเงื่อนไข `p >= 0.70` / `p >= 0.40` ในโค้ดจริง) |
| `test_campaign_roi_chi_square_shape` | `analytics.campaign_roi.channel_significance()` | `assert result["p_value"]` อยู่ในช่วง `[0,1]`, `result["chi2"] >= 0`, `result["conclusion"]` เป็น string ที่ไม่ว่าง, ทดสอบกับข้อมูลจริงจาก seed (ผ่าน `db` fixture เดิม) |

**คำสั่งรัน:** `pytest tests/test_analytics_units.py -v`

### 2.2 Playwright E2E จริงสำหรับฟอร์มออกใบเสนอราคา — ไฟล์ใหม่ `tests/e2e/test_quotation_form_e2e.py`

ปิดช่องว่างที่ `test_2_3_quotation_insert_shape` ข้ามไป: ใช้ Playwright ขับเบราว์เซอร์จริง (ไม่ใช่ AppTest) เพื่อทดสอบ multiselect+format_func ที่เป็นข้อจำกัดของ AppTest:

1. Login เป็น `sale1` → ไปหน้าที่มีฟอร์มออกใบเสนอราคา (Process 2.3)
2. เลือกสินค้าในช่อง multiselect (อย่างน้อย 2 รายการ)
3. Assert ว่าราคารวม/ส่วนลดที่แสดงบนหน้าจอคำนวณถูกต้องตรงกับที่คาดไว้
4. กดยืนยันออกใบเสนอราคา
5. Assert ว่ามีแถวใหม่ใน `SALE` (`Sale_Status = 'ออกใบเสนอราคาแล้ว'`) — เทียบกับพฤติกรรมเดิมที่ `test_2_3_quotation_insert_shape` ตรวจอยู่ตอนนี้ (แต่คราวนี้ผ่าน UI จริง ไม่ใช่ INSERT ตรง)

**คำสั่งรัน:** `pytest tests/e2e/test_quotation_form_e2e.py -v` (ต้องรันแยก เพราะ `pytest.ini` มี `addopts = --ignore=tests/e2e` เป็นค่าเริ่มต้น เหมือนไฟล์ e2e อื่นๆ ในโฟลเดอร์นี้)

### 2.3 (ตัวเลือกเสริม ไม่บังคับ) Index/Speed proof — สคริปต์ใหม่ `scripts/benchmark_index_usage.py`

ไม่ใช่ Focus Area ที่เลือกไว้ (Focus คือ Data Science / DB Architecture / Cloud & Web Service) จึงไม่จำเป็น แต่เป็นหลักฐานเสริมเล็กๆ ที่ทำได้โดยไม่แตะโค้ด:

- รัน `EXPLAIN QUERY PLAN` กับ query หลักที่ dashboard ใช้บ่อย (เช่น query เบื้องหลัง `V_SERVICE_HEALTH`, `V_CUSTOMER_RFM`)
- บันทึกผลลัพธ์เป็น `docs/INDEX_QUERY_PLAN_REPORT.md` — ใช้อ้างอิงเสริมในรายงานโครงงาน

**คำสั่งรัน:** `python scripts/benchmark_index_usage.py`

---

## 3. สิ่งที่ไม่ต้องทำซ้ำ (Explicitly Out of Scope)

รายการต่อไปนี้ได้รับการทดสอบครอบคลุมและผ่านเกณฑ์เรียบร้อยแล้ว — สามารถตรวจสอบซ้ำได้ด้วยคำสั่ง `pytest tests/ -v` (ไม่รวม `tests/e2e/`):

- Regression test ของ 2 บั๊กที่เคยเจอ (marketing NA-crash, `V_SERVICE_HEALTH` fan-out)
- RBAC allowed/denied role test ครบทุกหน้า
- E2E functional ครบ 16 กิจกรรมตาม DFD (ผ่าน `AppTest`) + Demo flow 7 ขั้นตอน + Playwright screenshot evidence

---

## 4. ผลกระทบต่อรายงานโครงงาน (`crm-report.docx`)

เมื่อชุดทดสอบในหัวข้อ 2.1–2.2 ผ่านเรียบร้อยแล้ว ให้นำผลการทดสอบไปบันทึกเพิ่มเติมในหัวข้อ 3.9 (ผลการทดสอบระบบ) ของรายงานโครงงานฉบับสมบูรณ์ ว่ามี Unit Test ระดับสูตรคำนวณของ Data Science และ E2E จริงของฟอร์มออกใบเสนอราคา เพื่อเพิ่มน้ำหนักให้ Focus 1 (Data Science/ML/AI) มีหลักฐานการทดสอบเชิงลึกที่สมบูรณ์

---

## 5. ผลการดำเนินการและการทดสอบจริง (Implementation & Verification Log)

ดำเนินการเสร็จสมบูรณ์เมื่อวันที่ **2026-09-20**:

### 5.1 ไฟล์ที่สร้างขึ้นใหม่
1. **`tests/test_analytics_units.py`**: Unit tests ครบ 4 โมเดล (9 test cases):
   - `TestRFMSegmentation`: `test_rfm_label_boundaries`, `test_rfm_score_quintile`, `test_rfm_score_edge_case_insufficient_data`
   - `TestChurnHealth`: `test_churn_weights_sum_100`, `test_churn_norm_range_and_direction`, `test_churn_norm_edge_cases`
   - `TestLeadScoring`: `test_lead_scoring_grade_boundaries`, `test_lead_scoring_grade_edge_values`
   - `TestCampaignROI`: `test_campaign_roi_chi_square_shape`
2. **`tests/e2e/test_quotation_form_e2e.py`**: Playwright E2E จริงสำหรับ Process 2.3:
   - จำลอง `sale1` เข้าหน้า `order-billing`
   - เลือกสินค้าผ่าน `st.multiselect` 2 รายการ ตรวจสอบยอดคำนวณสุทธิ
   - กดปุ่ม `🧾 ออกใบเสนอราคา`
   - Assert ยืนยันบน UI (`ออกใบเสนอราคา ... เรียบร้อย`)
   - Assert บันทึกแถวใหม่ลงตาราง `SALE` (`Sale_Status = 'ออกใบเสนอราคาแล้ว'`) และ `SALE_DETAIL` 2 รายการใน SQLite
   - บันทึกภาพ Screenshot: `docs/evidence/2_3_quotation_form_filled.png` และ `docs/evidence/2_3_quotation_submitted_success.png`
3. **`scripts/benchmark_index_usage.py`**: สคริปต์รัน `EXPLAIN QUERY PLAN` บน 7 Query หลัก
4. **`docs/INDEX_QUERY_PLAN_REPORT.md`**: รายงานผลการประเมิน Index usage และ Query Execution Plan

### 5.2 ผลการรันชุดทดสอบ (Test Results)

| ชุดทดสอบ | คำสั่งรัน | ผลลัพธ์ | ระยะเวลา |
|---|---|:---:|:---:|
| **Unit Tests Data Science** | `pytest tests/test_analytics_units.py -v` | ✅ **9 passed** | 2.13s |
| **Playwright Real UI E2E** | `pytest tests/e2e/test_quotation_form_e2e.py -v` | ✅ **1 passed** | 17.45s |
| **All Test Suite (Standard)** | `pytest tests/ -v` | ✅ **53 passed** (เดิม 44 + ใหม่ 9) | 27.08s |
| **Index Benchmark Script** | `python scripts/benchmark_index_usage.py` | ✅ **Generated** | < 1s |

ทุกรายการผ่านการทดสอบ 100% โดยไม่มีการแก้ไขโค้ดแอปพลิเคชันเดิมแม้แต่บรรทัดเดียวตามหลักการ Zero Application Code Modification
