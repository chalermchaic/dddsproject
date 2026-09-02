# Implementation Plan — ทดลองได้ครบทุกกิจกรรมใน DFD (v1.2.0)

## Context

`dfd.pdf` คือ Data Flow Diagram ที่ทีมออกแบบระบบ CRM นี้ขึ้นมา — มี **5 กระบวนการหลัก**
แตกเป็น **14 กิจกรรมย่อย (Level-1 processes)** และ external entity 5 ตัว
(ฝ่ายการตลาด / ผู้สนใจ / ฝ่ายขาย / ลูกค้า / ฝ่ายบริการลูกค้า)

**คำถาม:** แอปปัจจุบันทดลองได้ครบทุกกิจกรรมไหม → **ยังไม่ครบ** (ดูตารางด้านล่าง)
ประมาณ 5/14 ครบ, 5/14 ทำได้บางส่วน, 4/14 ยังไม่มี — และ flow ที่ external entity
"ผู้สนใจ/ลูกค้า" เป็นผู้ **ส่งข้อมูลเข้า** ระบบ (คำสั่งซื้อ, สลิป, แจ้งปัญหา, ลงทะเบียนเอง)
ยังทดลองไม่ได้เลยเพราะแอปเป็นฝั่งพนักงานล้วน

**เป้าหมาย v1.2.0:** ปิดช่องว่างให้ทดลองครบทั้ง 14 กิจกรรม + เพิ่มหน้า **Portal จำลอง**
สำหรับสวมบทบาท "ผู้สนใจ/ลูกค้า"

> **สถานะ:** ✅ implement แล้วใน v1.2.0 (branch `feature/dfd-full-coverage`) —
> ครบทั้ง 14 กิจกรรม + หน้า Portal + ชุดทดสอบ pytest/Playwright (36 tests + 12 screenshot)

---

## 📊 Coverage Matrix — DFD กิจกรรม vs แอปปัจจุบัน

| # | กิจกรรม (DFD Level 1) | ตอนนี้ | หน้า / หมายเหตุ |
|---|---|---|---|
| 1.1 | รับข้อมูลแคมเปญ → D5 | ✅ | `pages/1` แท็บ "สร้างแคมเปญ" |
| 1.2 | ลงทะเบียนผู้สนใจ → D1 | ⚠️ | `pages/1` แท็บ "บันทึกผู้สนใจ" — มีแต่ฝั่งฝ่ายการตลาดกรอก; DFD มี flow "ผู้สนใจส่งข้อมูลการติดต่อเอง" ด้วย |
| 1.3 | ให้ข้อมูลสินค้า/โปรโมชันแก่ผู้สนใจ (จาก D5) | ❌ | ไม่มี action ส่ง/บันทึกการส่งโปรโมชันให้ lead รายคน |
| 2.1 | ดึงรายชื่อผู้สนใจที่ต้องติดตาม **ประจำวัน** → ฝ่ายขาย | ⚠️ | `pages/2` มี "คิว AI (lead scoring)" แต่ไม่ใช่ To-Do ตาม `Next_Action_Date`/ครบกำหนด |
| 2.2 | บันทึกกิจกรรมการติดตาม → D1 | ✅ | `pages/2` แท็บ "ค้นหา & บันทึกกิจกรรม" |
| 2.3 | ออกใบเสนอราคา → ผู้สนใจ + D2 | ✅ | `pages/3` แท็บ "ออกใบเสนอราคา" |
| 3.1 | ตรวจสอบความถูกต้องของ **คำสั่งซื้อ** (input จากผู้สนใจ) | ❌ | แอปข้ามจากใบเสนอราคา → ยืนยันเงินเลย ไม่มีขั้นรับ+ตรวจคำสั่งซื้อ |
| 3.2 | ตรวจสอบการรับชำระเงิน (input: หลักฐาน/สลิป) | ⚠️ | `pages/3` แท็บ 2 กรอกเลขอ้างอิงได้ แต่ไม่มีรับสลิป/ตรวจหลักฐาน + รวบ 3.1–3.3 เป็นขั้นเดียว |
| 3.3 | ออกใบเสร็จรับเงิน + บันทึกลูกค้า → D3 | ⚠️ | สร้าง `CUSTOMER` ได้ แต่ "ใบเสร็จ" เป็นข้อความ ไม่มีเอกสาร/ดาวน์โหลด |
| 4.1 | รับแจ้ง + บันทึกปัญหา (input จากลูกค้า) → D4 | ⚠️ | `pages/5` แท็บ "เปิดเคสใหม่" — staff กรอกแทน; DFD มี flow "ลูกค้าแจ้งเอง" |
| 4.2 | ประสานงาน + แก้ไขปัญหา → D4 | ✅ | `pages/5` แท็บ "คิวเคส & สนทนา" |
| 4.3 | แจ้งผลการบริการ + **ประเมินผล** → ลูกค้า + ประวัติสั่งซื้อ/รับบริการ | ⚠️ | ปิดเคสได้ แต่ไม่มีแจ้งผล/ให้คะแนน (rating); ประวัติมีบางส่วนใน `pages/4` |
| 5.1 | ออกรายงานประสิทธิภาพแคมเปญ → ฝ่ายการตลาด | ✅ | `pages/6` แท็บ 4 (Campaign ROI) |
| 5.2 | ออกรายงาน **สรุปยอดขาย** → ฝ่ายขาย | ❌ | ไม่มีหน้ารายงานสรุปยอดขายรวมเป็นชิ้นเดียว (กราฟกระจายอยู่หลายหน้า) |

**External entity inbound/outbound ที่ยังทดลองไม่ได้:** ผู้สนใจส่ง `คำสั่งซื้อ`/`หลักฐานชำระเงิน`/`ข้อมูลการติดต่อ`,
ลูกค้าส่ง `ข้อมูลแจ้งปัญหา` + รับ `ใบเสนอราคา`/`รายละเอียดโปรโมชัน`/`ใบเสร็จ`/`สถานะบริการ`

---

## แผนปรับปรุง (ทำครบรอบเดียว → v1.2.0)

### A. Schema + Seed (`db/schema.sql`, `db/seed_data.py`)
- `SALE.Sale_Status` CHECK: เพิ่มค่า **`'รอตรวจสอบคำสั่งซื้อ'`** (ระหว่าง `ออกใบเสนอราคาแล้ว` → `รอการตรวจสอบชำระเงิน` → `ปิดการขายสำเร็จ`) — รองรับ 3.1/3.2/3.3 เป็น 3 ขั้นแยก
- `SALE`: + `Payment_Slip TEXT` (ชื่อไฟล์สลิปที่อัปโหลด, nullable), + `Order_Confirmed_At TEXT` (3.1)
- `TICKET`: + `Service_Rating INTEGER CHECK (Service_Rating BETWEEN 1 AND 5)`, + `Service_Feedback TEXT` (4.3) — nullable
- `LEAD_ACTIVITY.Activity_Type` CHECK: เพิ่ม **`'ส่งโปรโมชัน'`** (1.3)
- `seed_data.py`: อัปเดต tuple/arity ให้ตรง; seed ให้มี SALE ค้างในทุกสถานะใหม่ (มีบางใบอยู่ที่ `รอตรวจสอบคำสั่งซื้อ`, `รอการตรวจสอบชำระเงิน` พร้อมสลิปตัวอย่าง) + ticket ปิดเคสบางเคสมี rating — เพื่อให้ทุกหน้ามีข้อมูลให้กดทดลองทันที
- `PRAGMA foreign_key_check` ท้ายสคริปต์ (มีอยู่แล้ว)
- โฟลเดอร์ `uploads/` (gitignore `uploads/`) สำหรับเก็บสลิป — helper `save_upload()` ใน `db/connection.py`

### B. Process 1.3 — ส่งข้อมูลสินค้า/โปรโมชันให้ผู้สนใจ  (`pages/1` หรือ `pages/2`)
- ใน `pages/2` (ติดตามการขาย) แท็บบันทึกกิจกรรม: เพิ่มปุ่ม **"📧 ส่งรายละเอียดโปรโมชัน"** ที่ lead ที่เลือก
  → insert `LEAD_ACTIVITY` type `'ส่งโปรโมชัน'` + Notes = ชื่อแคมเปญ/ส่วนลด/สินค้าที่สนใจ (ดึงจาก `CAMPAIGN` ของ lead)
- แสดง preview "เนื้อหาที่ส่ง" (ชื่อโปรโมชัน + Discount_Rate + รายการสินค้า) — คือ flow `รายละเอียดโปรโมชัน → ผู้สนใจ`

### C. Process 2.1 — To-Do List ประจำวัน  (`pages/2_📞_Sales_Followup.py`)
- เพิ่มแท็บแรก **"📅 คิวติดตามวันนี้"** (ก่อนแท็บ AI):
  - query lead ที่ `Followup_Status IN ('รอการติดต่อ','อยู่ระหว่างเสนอขาย')` และ
    `Next_Action_Date <= date('now')` (ครบกำหนด/เลยกำหนด) จาก activity ล่าสุด
  - แยก 3 กลุ่ม: เลยกำหนด / วันนี้ / ยังไม่เคยติดตาม
  - ปุ่มลัด "บันทึกกิจกรรม" กระโดดไปแท็บ 2 พร้อม lead ที่เลือก (`st.session_state`)
- reuse `SQL` pattern ใน `pages/2` เดิม + `analytics/lead_scoring.score_open_leads` สำหรับจัดลำดับในกลุ่ม

### D. Process 3.0 — แยก 3.1 / 3.2 / 3.3  (`pages/3_🧾_Order_Billing.py`)
เปลี่ยนจาก 3 แท็บ (`ออกใบเสนอราคา` / `ยืนยันชำระเงิน` / `ประวัติ`) เป็น **5 แท็บ**:
1. **ออกใบเสนอราคา** (2.3) — เดิม
2. **📥 รับ & ตรวจคำสั่งซื้อ (3.1)** — list SALE ที่ `ออกใบเสนอราคาแล้ว`; staff กด "ยืนยันคำสั่งซื้อถูกต้อง"
   → `Sale_Status='รอตรวจสอบคำสั่งซื้อ'`... จริง ๆ ควรเป็น: prospect ส่งคำสั่งซื้อ (ผ่าน Portal) → staff **ตรวจ** → `รอการตรวจสอบชำระเงิน`
   (ถ้าไม่ผ่าน Portal ก็ให้ staff กดแทนได้)
3. **💳 ตรวจสอบการชำระเงิน (3.2)** — list SALE ที่ `รอการตรวจสอบชำระเงิน` + แสดงสลิปที่ลูกค้าอัปโหลด (`Payment_Slip`);
   staff กรอกเลขอ้างอิง + กด "ยืนยันรับเงิน" → เตรียมออกใบเสร็จ
4. **🧾 ออกใบเสร็จ + บันทึกลูกค้า (3.3)** — กด → `Sale_Status='ปิดการขายสำเร็จ'`, สร้าง `CUSTOMER`,
   สร้าง **ใบเสร็จ HTML** ให้ `st.download_button` (เลขที่ใบเสร็จ, รายการสินค้า, ยอด, วันที่) — flow `ใบเสร็จ → ลูกค้า`
5. **ประวัติการขาย** — เดิม
- reuse `next_id`, `execute`, logic สร้าง CUSTOMER เดิมใน tab2 ปัจจุบัน

### E. Process 4.3 — แจ้งผล + ประเมินผลบริการ  (`pages/5` + `pages/4`)
- `pages/5` การ์ด "จัดการเคส": ตอนตั้งสถานะ `ปิดเคสสำเร็จ` เพิ่มช่อง "สรุปผลการแก้ไข" (→ `TICKET_MESSAGE` ปิดท้าย)
- เพิ่มแท็บ/ส่วน **"⭐ ประเมินผลบริการ"** — ให้คะแนน 1–5 + feedback (ปกติมาจากลูกค้าผ่าน Portal; staff กรอกแทนได้)
  → `UPDATE TICKET SET Service_Rating=?, Service_Feedback=?`
- `pages/4` (ข้อมูลลูกค้า): เพิ่มการ์ด **"ประวัติการสั่งซื้อและรับบริการ"** รวม SALE + TICKET + rating เฉลี่ย
  = flow `ประวัติการสั่งซื้อและรับบริการ`; ปุ่ม export CSV
- `pages/6` แท็บ 3 (Churn/Health): เสริม avg `Service_Rating` เป็นตัวแปร health (ถ้ามีเวลา — optional)

### F. Process 5.2 — รายงานสรุปยอดขาย  (`pages/6_📊_Analytics_Dashboard.py` เพิ่มแท็บ)
- เพิ่มแท็บ **"5️⃣ รายงานสรุปยอดขาย"** (role: admin, sales, marketing):
  - ยอดขายรวม / จำนวนบิล / ค่าเฉลี่ยต่อบิล (period filter: เดือน/ไตรมาส/ปี)
  - แยกตาม **พนักงานขาย** (ใช้ `SALE.Employee_ID` ที่เพิ่งเพิ่ม) — leaderboard
  - แยกตามสินค้า / แคมเปญ / ช่องทาง
  - ปุ่ม **"⬇️ ดาวน์โหลดรายงาน (CSV)"** = flow `รายงานสรุปยอดขาย → ฝ่ายขาย`
- reuse `SQL_TOP_PRODUCT`, `SQL_MONTHLY`, `channel_performance()` ใน `analytics/campaign_roi.py`

### G. หน้า Portal จำลอง ผู้สนใจ/ลูกค้า  (`pages/9_🌐_Portal.py` + `auth.py`)
- `auth.py`: เพิ่มปุ่มบนหน้า login **"🌐 เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)"**
  → set `st.session_state["user"] = {role: "guest", ...}`; `PAGE_DEFS` ให้ role `guest` เห็นเฉพาะ `pages/9`
- `pages/9_🌐_Portal.py` — เลือกว่าจะสวมบทเป็น Lead ไหน / Customer ไหน แล้วทำ:
  | แท็บ | flow DFD ที่ทดลอง |
  |---|---|
  | ลงทะเบียนความสนใจ | 1.2 (ผู้สนใจ → ข้อมูลการติดต่อ) |
  | ดูโปรโมชัน/ใบเสนอราคาที่ได้รับ | 1.3, 2.3 (ขารับ) |
  | ยืนยันคำสั่งซื้อ (จากใบเสนอราคา) | 3.1 (ผู้สนใจ → คำสั่งซื้อ) |
  | อัปโหลดสลิปชำระเงิน | 3.2 (ผู้สนใจ → หลักฐานชำระเงิน) |
  | ดูใบเสร็จ + ประวัติสั่งซื้อ/บริการ | 3.3, 4.3 (ขารับ) |
  | แจ้งปัญหา + ดูสถานะเคส + ให้คะแนนบริการ | 4.1, 4.3 (ลูกค้า → แจ้งปัญหา, ประเมิน) |
- reuse `execute`/`next_id`/`run_query`; INSERT LEAD/SALE-update/TICKET เดิม (ไม่มี Employee_ID จากฝั่งนี้ — 3.1 คำสั่งซื้อไม่แตะ Employee_ID, ticket เปิดโดยลูกค้า → `Employee_ID=NULL`)

### H. เอกสาร + verify (`README.md`, `bootstrap.py`, `data-dictionary-er.md`, `VERSION`)
- `VERSION` → `1.2.0`; README changelog + section "ทดลองครบทุกกิจกรรม DFD" พร้อม coverage matrix (ฉบับ ✅ ครบ)
- `bootstrap.py`: `REQUIRED_FILES += pages/9`; `REQUIRED_TABLES` เดิมพอ; เพิ่มเช็คคอลัมน์ใหม่ (optional)
- `data-dictionary-er.md`: เพิ่มคอลัมน์ `Payment_Slip`/`Order_Confirmed_At` (SALE), `Service_Rating`/`Service_Feedback` (TICKET) + สถานะใหม่
- `.gitignore`: + `uploads/`

---

## ไฟล์หลักที่แตะ

| ไฟล์ | การเปลี่ยนแปลง |
|---|---|
| `db/schema.sql` | + คอลัมน์/สถานะ (SALE, TICKET, LEAD_ACTIVITY) |
| `db/seed_data.py` | seed ข้อมูลให้ครบทุกสถานะใหม่ + rating |
| `db/connection.py` | + `save_upload()` helper |
| `auth.py` | + role `guest` + ปุ่ม Portal บนหน้า login + `PAGE_DEFS` |
| `pages/2_📞_Sales_Followup.py` | + แท็บ "คิวติดตามวันนี้" (2.1), + ปุ่มส่งโปรโมชัน (1.3) |
| `pages/3_🧾_Order_Billing.py` | 3 แท็บ → 5 แท็บ (3.1 / 3.2+สลิป / 3.3+ใบเสร็จ) |
| `pages/4_👤_Customer_Profile.py` | + การ์ด "ประวัติสั่งซื้อ+รับบริการ" (4.3) |
| `pages/5_🎫_Support_Ticket.py` | + สรุปผล + ประเมินผลบริการ (4.3) |
| `pages/6_📊_Analytics_Dashboard.py` | + แท็บ "รายงานสรุปยอดขาย" (5.2) |
| `pages/9_🌐_Portal.py` | **ใหม่** — external entity inbound/outbound |
| `tests/` | **ใหม่** — pytest (AppTest) + Playwright e2e + capture หลักฐาน |
| `requirements-dev.txt` | **ใหม่** — `pytest`, `pytest-playwright`, `playwright` |
| `.github/workflows/ci.yml` | **ใหม่** (optional) — seed + bootstrap --check + pytest |
| `README.md` `bootstrap.py` `data-dictionary-er.md` `VERSION` `.gitignore` `Makefile` | เอกสาร + verify + v1.2.0 + target `test` / `e2e` / `evidence` |

**ไม่แตะ:** `analytics/*.py` (logic ML/สูตร 4 งานเดิม), Views ทั้ง 4, `app.py` router, `docker/*`

---

## การทดสอบ — 3 ชั้น

```bash
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m playwright install chromium
python db/seed_data.py            # EMPLOYEE + ทุกสถานะใหม่, foreign_key_check ผ่าน
python bootstrap.py --check       # exit 0
make test        # ชั้น 1 + 2  (เร็ว, ไม่ใช้ browser)
make e2e         # ชั้น 3       (Playwright)
make evidence    # ชั้น 3 + ประกอบ docs/evidence/README.md
```

### ชั้น 1 — Smoke / logic  (`tests/test_smoke.py`, Streamlit `AppTest`, ~10s)
- ต่อยอดสคริปต์ matrix เดิม → committed pytest:
  - ทุกหน้า × ทุก role ที่มีสิทธิ์ → ไม่มี exception
  - role ไม่มีสิทธิ์ → เจอ `st.error` + `st.stop` (ไม่ crash)
  - role `guest` → เห็นเฉพาะ `pages/9`; role อื่นไม่เห็น `pages/9`
- `analytics` 4 โมดูล import + รัน `train()`/`build_*()` ได้ (metrics ไม่ต่ำผิดปกติ)

### ชั้น 2 — DFD flow (headless)  (`tests/test_dfd_flows.py`, `AppTest` ขับฟอร์ม, ~1–2 นาที)
1 test = 1 กิจกรรม DFD — เซ็ต `session_state["user"]`, กรอกฟอร์ม, กดปุ่ม, แล้ว **assert แถว/สถานะใน `db/crm.db`**
(fixture: re-seed ก่อนทุก test; รัน serial). ครอบคลุมทั้ง 14 กิจกรรม:

| กิจกรรม | ขับหน้า | assert |
|---|---|---|
| 1.1 | `pages/1` marketing1 → สร้างแคมเปญ | `CAMPAIGN.Employee_ID` = ผู้ล็อกอิน |
| 1.2 | `pages/1` + `pages/9` (guest) ลงทะเบียนเอง | `LEAD` เพิ่ม 2 แถว |
| 1.3 | `pages/2` sale1 → "ส่งรายละเอียดโปรโมชัน" | `LEAD_ACTIVITY.Activity_Type='ส่งโปรโมชัน'` |
| 2.1 | `pages/2` แท็บ "คิวติดตามวันนี้" | ตารางมีแถวกลุ่ม เลยกำหนด/วันนี้ |
| 2.2 | `pages/2` บันทึกกิจกรรม | `LEAD_ACTIVITY` + `LEAD.Followup_Status` เปลี่ยน |
| 2.3 | `pages/3` ออกใบเสนอราคา | `SALE.Sale_Status='ออกใบเสนอราคาแล้ว'` |
| 3.1 | `pages/9` ยืนยันคำสั่งซื้อ → `pages/3` แท็บ 3.1 | `Sale_Status='รอการตรวจสอบชำระเงิน'`, `Order_Confirmed_At` ไม่ว่าง |
| 3.2 | `pages/9` `set_input_files` สลิป → `pages/3` แท็บ 3.2 | `Payment_Slip` ไม่ว่าง + ไฟล์อยู่ใน `uploads/` |
| 3.3 | `pages/3` แท็บ 3.3 | `ปิดการขายสำเร็จ` + `CUSTOMER` ใหม่ + ได้ bytes ใบเสร็จ |
| 4.1 | `pages/9` (ลูกค้า) แจ้งปัญหา | `TICKET` ใหม่ `Employee_ID IS NULL` |
| 4.2 | `pages/5` cs1 ตอบแชท + เปลี่ยนสถานะ | `TICKET_MESSAGE` + `Ticket_Status` |
| 4.3 | `pages/5` ปิดเคส + `pages/9` ให้คะแนน 5 | `TICKET.Service_Rating=5`; `pages/4` การ์ดประวัติมีข้อมูล |
| 5.1 | `pages/6` แท็บ 4 | ตาราง ROI ไม่ว่าง |
| 5.2 | `pages/6` แท็บ "รายงานสรุปยอดขาย" | `download_button` คืน CSV ที่มีคอลัมน์ พนักงานขาย |

### ชั้น 3 — Playwright e2e + capture หลักฐาน  (`tests/e2e/`, ~3–5 นาที)
- `tests/e2e/conftest.py`:
  - fixture (session): re-seed DB → `subprocess.Popen(["streamlit","run","app.py","--server.port","8765","--server.headless","true"])` → poll `GET /_stcore/health` จน 200 → yield `base_url` → kill
  - fixture (function): `page` จาก `pytest-playwright`, `page.set_default_timeout(15000)` (Streamlit rerun ช้า)
- `tests/e2e/test_dfd_evidence.py` — 1 test/กิจกรรม เดินผ่าน UI จริง:
  - login: click ปุ่มที่มีข้อความ "เข้าใช้งานเป็น ... sale1" (ปรับ label ปุ่มใน `auth.py` ให้ไม่มี backtick ครอบ username เพื่อให้ selector ง่าย)
  - เมนู: `page.get_by_role("link", name="ใบเสนอราคา/ชำระเงิน").click()`
  - widget: `get_by_role("button"/"textbox"/"tab")`, `get_by_test_id("stFileUploaderDropzoneInput").set_input_files(...)`
  - หลังทุก action: `expect(page.get_by_text("...")).to_be_visible()` แล้ว
    `page.screenshot(path=f"docs/evidence/{activity}.png", full_page=True)`
- `tests/e2e/build_report.py` (รันโดย `make evidence`): สแกน `docs/evidence/*.png` → เขียน
  `docs/evidence/README.md` ตาราง 14 กิจกรรม + `![](x.png)` — เอาไปแปะภาคผนวกรายงานได้เลย
- `.gitignore`: `docs/evidence/*.png` (เก็บเฉพาะตอนส่งงาน / หรือ commit เป็นหลักฐานก็ได้)

**หมายเหตุความเสี่ยง:** Playwright + Streamlit เปราะพอควร (ไม่มี stable id, rerun async) →
ชั้น 1–2 เป็น **gate จริง** (ต้องเขียว), ชั้น 3 เป็น **best-effort visual evidence**
ถ้า e2e บาง step ไม่นิ่ง ให้ fallback เป็น screenshot ของหน้า + assert DB (เหมือนชั้น 2) แทน

### CI (optional) — `.github/workflows/ci.yml`
`python db/seed_data.py` → `python bootstrap.py --check` → `pytest tests/test_smoke.py tests/test_dfd_flows.py` → `python -m analytics.*`
(ชั้น 3 ข้ามใน CI หรือรันแยก job ที่ลง `playwright install --with-deps chromium`)

---

## Commit ที่วางแผน (branch `feature/dfd-full-coverage`)
1. `Add order-validation / payment-slip / service-rating columns to schema`
2. `Seed sample rows for every new sale status and rating`
3. `Split Order & Billing into 3.1 / 3.2 / 3.3 with receipt download`
4. `Add daily follow-up queue (2.1) and promo-send action (1.3)`
5. `Add service rating + combined order/service history (4.3)`
6. `Add sales summary report tab (5.2)`
7. `Add simulated Lead/Customer portal (guest role)`
8. `Add pytest smoke + DFD-flow test suites`
9. `Add Playwright e2e evidence capture + report builder`
10. `Docs + CI + bootstrap + version 1.2.0`
