# 📸 แผนสคริปต์ Capture ภาพหลักฐานจริงต่อกิจกรรม (Real UI Evidence Capture Script Plan)

> **วิชา:** 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (Database Design for Data Science: DDDS)
> **โครงงาน:** ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM & Data Science Analytics Platform)
> **ที่มา:** แยกออกมาจาก `plan_2_user_manual.md` — เพราะ `user_manual.docx` ปัจจุบันใช้ **ภาพแผนภาพ DFD** (Context, Level 0, Process 1.0-5.0) ประกอบแต่ละบท ซึ่งเป็นภาพเชิงทฤษฎี **ไม่ใช่ภาพหน้าจอจริงของแต่ละกิจกรรม** — ตัวหนังสือ/คำอธิบายขั้นตอนใน `user_manual.docx` ใช้ได้ดีอยู่แล้ว แต่ขาดภาพ UI จริงประกอบทีละขั้นตอน (เช่น 2.1 การบันทึกและจัดการแคมเปญ ควรมีภาพหน้าจอฟอร์มกรอกแคมเปญจริง ไม่ใช่ภาพ DFD Process 1.0)
> **เกี่ยวข้องกับ:** `dddsproject_v1.2.1_page_naming_migration.md` (ควรรัน migration ชื่อไฟล์/URL ให้เสร็จก่อน แล้วค่อยรันสคริปต์นี้ — ดูข้อ 7.4 ของไฟล์นั้น) และ `plan_5_demo.md` หัวข้อ 4 (Demo Seed Data Checklist — ใช้ชุดข้อมูลเดียวกัน)

---

## 1. หลักการ (Principle)

แทนที่จะใช้ 1 ภาพ DFD ต่อ 1 บท (ภาพรวมเชิงทฤษฎี) ให้ถ่าย **1-2 ภาพหน้าจอจริงต่อ 1 กิจกรรมย่อย (Activity)** รวมทั้งหมด 14 กิจกรรมตาม DFD โดยแต่ละภาพต้องเห็น:

* ฟอร์ม/ปุ่ม/ตารางจริงที่ผู้ใช้ต้องกดในขั้นตอนนั้น (ไม่ใช่หน้าจอเปล่า)
* ถ้าเป็นขั้นตอนกรอกข้อมูล → ถ่าย **ก่อนกด (ฟอร์มกรอกครบ)** และ **หลังกด (ผลลัพธ์/ยืนยันสำเร็จ)** รวม 2 ภาพ
* ถ้าเป็นขั้นตอนแสดงผล/รายงาน (ไม่มีการกรอกฟอร์ม) → ถ่าย 1 ภาพที่มีข้อมูลตัวอย่างครบ อ่านแล้วเข้าใจได้ทันที

ภาพ DFD เดิม (Context, Level 0, Process 1.0-5.0) **ยังเก็บไว้ได้ 1 ภาพต่อบทเพื่อปูภาพรวม** แต่ให้ลดขนาด/ย้ายไปเป็นแค่ภาพประกอบสั้น ๆ ต้นบท ไม่ใช่ภาพหลักที่ใช้แทนการอธิบายขั้นตอน

---

## 2. ตารางแมป 14 กิจกรรม → ภาพที่ต้องถ่าย

| # DFD | กิจกรรม | Login (Role) | หน้า → แท็บ (ตามชื่อไฟล์ v1.2.1) | สิ่งที่ต้องถ่าย | ชื่อไฟล์ภาพเสนอ |
|:---:|---|:---:|---|---|---|
| 1.1 | บันทึกและจัดการแคมเปญโปรโมชัน | marketing1 | `1_marketing` → "➕ สร้างแคมเปญ" | (ก) ฟอร์มกรอกแคมเปญครบทุกฟิลด์ก่อนกดบันทึก (ข) ตารางแคมเปญที่มีรายการใหม่ขึ้นหลังบันทึกสำเร็จ | `1_1_campaign_form.png`, `1_1_campaign_saved.png` |
| 1.2 | บันทึกข้อมูลผู้สนใจ (Lead Intake) | marketing1 | `1_marketing` → "🙋 บันทึกผู้สนใจใหม่" | (ก) ฟอร์มกรอกข้อมูลผู้สนใจก่อนบันทึก (ข) ข้อความยืนยัน/รหัส Lead_ID ที่ออกให้หลังบันทึก | `1_2_lead_form.png`, `1_2_lead_saved.png` |
| 1.3 | จัดส่งโปรโมชันแก่ผู้สนใจ | marketing1 | `1_marketing` (จุดแสดงการส่ง/สิทธิ์ที่ผูกกับ Lead) | 1 ภาพ: หน้าจอที่แสดงว่า Lead รายนั้นได้รับโปรโมชันที่เจาะจงแล้ว | `1_3_promo_sent.png` |
| 2.1 | คิวติดตามผู้สนใจประจำวัน + AI Priority Queue | sale1 | `2_sales_followup` → "📅 คิวติดตามวันนี้" และ "🔥 คิวงาน AI" | (ก) ตารางคิวที่มีตัวอย่างครบ 3 กลุ่ม (Overdue/Due Today/Never) (ข) แท็บ AI Priority ที่มีกลุ่ม Hot/Warm/Cold จริงพร้อมเปอร์เซ็นต์ | `2_1_todo_queue.png`, `2_1_ai_priority.png` |
| 2.2 | บันทึกกิจกรรมการติดต่อ (Lead Activity Logging) | sale1 | `2_sales_followup` → "🔍 ค้นหา & บันทึกกิจกรรม" | (ก) ฟอร์มกรอกกิจกรรมก่อนบันทึก (ข) ไทม์ไลน์คอลัมน์ขวาที่อัปเดตประวัติหลังบันทึก | `2_2_activity_form.png`, `2_2_activity_timeline.png` |
| 2.3 | ออกใบเสนอราคา (Quotation Generation) | sale1 | `3_order_billing` → "📝 ออกใบเสนอราคา" | (ก) หน้าจอเลือกสินค้า/ระบบคำนวณส่วนลดอัตโนมัติ (ข) ใบเสนอราคาที่ออกสำเร็จพร้อมรหัส SL | `2_3_quotation_form.png`, `2_3_quotation_issued.png` |
| 3.1 | รับ & ตรวจคำสั่งซื้อ | sale1 | `3_order_billing` → "📥 รับ & ตรวจคำสั่งซื้อ" | 1 ภาพ: รายการคำสั่งซื้อที่รอตรวจพร้อมรายละเอียด | `3_1_order_review.png` |
| 3.2 | ตรวจสอบการชำระเงิน | sale1 | `3_order_billing` → "💳 ตรวจสอบการชำระเงิน" | 1 ภาพ: สลิปโอนเงินที่ลูกค้าอัปโหลด พร้อมปุ่มยืนยัน | `3_2_payment_check.png` |
| 3.3 | ออกใบเสร็จ + บันทึกลูกค้า | sale1 | `3_order_billing` → "🧾 ออกใบเสร็จ + บันทึกลูกค้า" | 1 ภาพ: ใบเสร็จที่ออกสำเร็จ + สถานะยกระดับเป็น CUSTOMER | `3_3_receipt_issued.png` |
| 4.1 | รับแจ้งและเปิดเคสปัญหา | cs1 | `5_support_ticket` → "➕ เปิดเคสใหม่" | (ก) ฟอร์มเปิดเคสก่อนบันทึก (ข) รหัส Ticket ที่ออกให้หลังเปิดเคสสำเร็จ | `4_1_ticket_form.png`, `4_1_ticket_created.png` |
| 4.2 | ประสานงาน สนทนา บันทึกผลแก้ไข | cs1 | `5_support_ticket` → "📥 คิวเคส & สนทนา" | 1 ภาพ: หน้าต่างแชทที่มีข้อความสนทนาจริง + สถานะเปลี่ยนเป็น "กำลังแก้ไข" | `4_2_ticket_chat.png` |
| 4.3 | ปิดเคส แจ้งผล รับคะแนนประเมิน | cs1 + portal (ลูกค้าให้คะแนน) | `5_support_ticket` (ปิดเคส) + `9_portal` แท็บ ⑤ | (ก) หน้าจอปิดเคสสำเร็จ (ข) หน้าจอที่ลูกค้าให้คะแนน 5 ดาวผ่าน Portal | `4_3_ticket_closed.png`, `4_3_rating_given.png` |
| 5.1 | ตรวจสอบรายงานประสิทธิภาพแคมเปญ (Campaign ROI) | marketing1 | `6_analytics_dashboard` → แท็บ "Campaign ROI" | 1 ภาพ: แดชบอร์ด ROI ที่มีข้อมูลแคมเปญตัวอย่างครบ (ใช้ภาพเดียวกับหมวด 6.4 ในคู่มือ ไม่ต้องถ่ายซ้ำ) | `5_1_6_4_campaign_roi.png` |
| 5.2 | รายงานสรุปยอดขาย (Sales Performance Report) | sale1 หรือ admin1 | `6_analytics_dashboard` → แท็บ "รายงานสรุปยอดขาย" | 1 ภาพ: รายงานยอดขายจริงตามช่วงเวลาที่เลือก | `5_2_sales_report.png` |

รวม **~20 ภาพ** (บางกิจกรรมมี 2 ภาพ ก่อน/หลัง) แทนที่ภาพ DFD 5 ภาพ + ภาพเมนูกว้าง ๆ 12 ภาพเดิมที่ไม่ได้ลงรายละเอียดระดับกิจกรรม

### ภาพเสริมที่แนะนำให้ทำแบบเดียวกัน (ไม่บังคับ แต่ควรทำถ้ามีเวลา)

* **Portal (บทที่ 5):** ปัจจุบันมีแค่ `portal_home.png` ภาพเดียวคลุมทั้ง 5 แท็บ — แนะนำถ่ายแยกทีละแท็บ (① ลงทะเบียน ② ตรวจใบเสนอราคา ③ ยืนยันคำสั่งซื้อ ④ อัปโหลดสลิป ⑤ ให้คะแนน) เพื่อให้เห็น UI จริงของแต่ละฟังก์ชัน
* **Analytics Dashboard (บทที่ 6):** ปัจจุบันมีแค่ภาพ DFD Process 5.0 — แนะนำถ่ายแยกทีละแท็บ (Lead Scoring, RFM, Churn/Health) เพิ่มเติมจาก Campaign ROI ที่มีอยู่แล้ว

---

## 3. ข้อมูลตัวอย่างที่ต้องเตรียมก่อนถ่าย (Seed Data Dependency)

ใช้ชุดข้อมูลเดียวกับ **หัวข้อ 4 ของ `plan_5_demo.md` (Demo Seed Data Checklist)** เพื่อไม่ต้องเตรียมข้อมูลซ้ำสองที่:

* Lead ตัวอย่างที่ยังไม่เคยติดต่อ + Lead ที่เลยกำหนดนัด + Lead ที่ครบกำหนดวันนี้ (สำหรับภาพ 2.1)
* Lead ที่ควรได้ Lead Score สูง ~80-90% (สำหรับภาพ 2.1 กลุ่ม Hot)
* แคมเปญที่ ROI สูงชัดเจน 1 แคมเปญ (สำหรับภาพ 1.1, 5.1)
* ลูกค้าที่มี Churn Risk ต่ำ 1 ราย (ถ้าจะถ่ายภาพเสริม Churn/Health)
* Ticket ตัวอย่างที่พร้อมปิดเคสให้เห็นคะแนน 5 ดาว (สำหรับภาพ 4.3)
* บัญชี 4 Role (marketing1, sale1, cs1, admin1) + บัญชี Portal จำลอง — Login ไว้ล่วงหน้า

---

## 4. แผนสคริปต์ Automation (Playwright)

**เป้าหมาย:** เขียนสคริปต์ตัวเดียว รันครั้งเดียวได้ภาพครบทุกกิจกรรม แทนการเปิดแอปถ่ายมือทีละภาพ (ซึ่งเสี่ยงพลาด/ไม่สม่ำเสมอ) และรันซ้ำได้ทุกครั้งที่ UI เปลี่ยน (idempotent)

**ที่ตั้งไฟล์เสนอ:** `tests/e2e/capture_manual_evidence.py` (แยกจาก `test_dfd_evidence.py` เดิมที่เป็นชุด Assert สำหรับทดสอบ ไม่ใช่ชุดสำหรับสร้างภาพประกอบคู่มือ — แต่ควรใช้ Login Helper/Fixture เดิมจากไฟล์นั้นถ้ามี เพื่อไม่ต้องเขียนใหม่)

**โครงสคริปต์ (Pseudocode/Skeleton — ต้องปรับ selector ให้ตรงกับโค้ดจริงของหน้านั้น ๆ):**

```python
"""
capture_manual_evidence.py
สร้างภาพหลักฐาน UI จริงต่อกิจกรรม สำหรับใช้ประกอบ user_manual.docx
รันหลังจาก dddsproject v1.2.1 (page naming migration) เสร็จแล้วเท่านั้น
"""
from playwright.sync_api import sync_playwright
import os

BASE_URL = "http://localhost:8501"
OUT_DIR = "docs/evidence"

# ตารางนี้คือแปลงร่างจากตารางข้อ 2 ด้านบนเป็นข้อมูล — แก้ selector ให้ตรงจริง
ACTIVITIES = [
    {
        "id": "1_1_campaign_form",
        "role": "marketing1",
        "page": "marketing",              # ตาม url_path ใหม่จาก v1.2.1
        "tab": "➕ สร้างแคมเปญ",
        "fill": lambda page: fill_campaign_form(page),   # ฟังก์ชันกรอกฟอร์มตัวอย่าง
        "action": None,                    # ยังไม่กดบันทึก แค่ถ่ายฟอร์ม
    },
    {
        "id": "1_1_campaign_saved",
        "role": "marketing1",
        "page": "marketing",
        "tab": "➕ สร้างแคมเปญ",
        "fill": lambda page: fill_campaign_form(page),
        "action": lambda page: page.click("text=💾 บันทึกแคมเปญ"),  # กดบันทึกก่อนถ่าย
    },
    # ... เพิ่มครบทั้ง ~20 รายการตามตารางข้อ 2 ...
]

def login_as(page, role_username: str):
    page.goto(BASE_URL)
    page.click(f"text=เข้าใช้งานเป็น {role_username}")  # ปรับ selector ตามจริง
    page.wait_for_load_state("networkidle")

def goto_tab(page, page_slug: str, tab_label: str):
    page.goto(f"{BASE_URL}/{page_slug}")
    page.click(f"text={tab_label}")
    page.wait_for_load_state("networkidle")

def capture(page, filename: str):
    path = os.path.join(OUT_DIR, f"{filename}.png")
    page.screenshot(path=path, full_page=True)
    print(f"[OK] {path}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        current_role = None
        for item in ACTIVITIES:
            if item["role"] != current_role:
                login_as(page, item["role"])
                current_role = item["role"]
            goto_tab(page, item["page"], item["tab"])
            if item.get("fill"):
                item["fill"](page)
            if item.get("action"):
                item["action"](page)
                page.wait_for_timeout(500)  # รอ toast/ผลลัพธ์ขึ้นก่อนถ่าย
            capture(page, item["id"])
        browser.close()

if __name__ == "__main__":
    run()
```

**หมายเหตุสำคัญ:** โครงนี้เป็น**ต้นแบบ (template)** — ฟังก์ชัน `fill_campaign_form()` และ selector ข้อความปุ่ม/แท็บ ต้องเปิดโค้ดจริงใน `pages/1_marketing.py` ฯลฯ มาเทียบก่อนใส่ให้ตรง 100% (ชื่อปุ่ม/label ในโค้ดต้นทางคือของจริง ไม่ใช่ที่เดาไว้ในตารางข้อ 2)

---

## 5. ขั้นตอนการทำงาน (Action Steps)

1. รอให้ `dddsproject_v1.2.1_page_naming_migration.md` ทำเสร็จและทดสอบผ่านก่อน (URL/ชื่อไฟล์นิ่งแล้ว)
2. เตรียม Seed Data ตามข้อ 3 ให้ครบ (เชื่อมกับ `plan_5_demo.md` หัวข้อ 4)
3. เปิดโค้ดจริงของแต่ละหน้าใน `pages/` มาไล่เทียบ label ปุ่ม/แท็บ/ฟอร์ม แล้วเติมลงสคริปต์ต้นแบบข้อ 4 ให้ครบทั้ง ~20 รายการ
4. รันสคริปต์ `python tests/e2e/capture_manual_evidence.py` ได้ภาพลง `docs/evidence/` ทั้งหมด
5. ไล่เปิดภาพทีละภาพเช็คว่าอ่านง่าย ข้อมูลไม่หลุด (เช่น เลขบัตร/ข้อมูลอ่อนไหวถ้ามี) และเห็นสิ่งที่ต้องการสื่อชัดเจน
6. แก้ `build_user_manual_docx.py` ให้แทรกภาพใหม่เหล่านี้ **ต่อท้ายคำอธิบายขั้นตอนของแต่ละ Process โดยตรง** (แทนที่จะกระจุกไว้แค่ภาพ DFD ต้นบท) แล้ว re-generate `user_manual.docx`
7. อัปเดต `plan_2_user_manual.md` หัวข้อ 4 (คลังภาพหลักฐาน) ให้ชื่อไฟล์ตรงกับภาพชุดใหม่ทั้งหมด

---

## 6. เกณฑ์ตรวจรับ (Definition of Done)

* [ ] ทุก 14 กิจกรรมมีภาพ UI จริงอย่างน้อย 1 ภาพ (ขั้นตอนกรอกฟอร์มมี 2 ภาพก่อน/หลัง)
* [ ] ไม่มีภาพ DFD เหลืออยู่เป็นภาพหลักของกิจกรรมใด ๆ (DFD เก็บไว้ได้แค่ภาพรวมต้นบท 1 ภาพ)
* [ ] ภาพทุกภาพถ่ายหลัง migration v1.2.1 เสร็จแล้ว (URL/เมนูในภาพเป็นเวอร์ชันล่าสุด)
* [ ] `user_manual.docx` แทรกภาพใหม่ต่อท้ายคำอธิบายแต่ละขั้นตอนแล้ว re-generate เรียบร้อย
* [ ] `plan_2_user_manual.md` หัวข้อ 4 อัปเดตชื่อไฟล์ภาพให้ตรงกับชุดใหม่
