"""ประกอบ screenshot ใน docs/evidence/ เป็น README.md สำหรับแนบภาคผนวกรายงาน"""
import glob
import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


EVID = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "evidence")

CAPTION = {
    "00_login": "หน้าเลือกบัญชีผู้ใช้เพื่อเข้าสู่ระบบ (Context DFD — External Entity)",
    "menu_admin1": "เมนูของ admin — เห็นครบทุกกระบวนการ",
    "menu_marketing1": "เมนูของฝ่ายการตลาด",
    "menu_sale1": "เมนูของฝ่ายขาย",
    "menu_cs1": "เมนูของฝ่ายบริการลูกค้า",
    "1_1_campaign_form": "Process 1.1 — บันทึกแคมเปญโปรโมชันใหม่ (กรอกข้อมูลครบถ้วน)",
    "1_1_campaign_saved": "Process 1.1 — รายการแคมเปญในระบบหลังบันทึกสำเร็จ",
    "1_2_lead_form": "Process 1.2 — บันทึกข้อมูลผู้สนใจใหม่ (Lead Intake)",
    "1_2_lead_saved": "Process 1.2 — ระบบบันทึกผู้สนใจและออกรหัส Lead_ID สำเร็จ",
    "1_3_promo_sent": "Process 1.3 — จัดส่งโปรโมชันเจาะจงแก่ผู้สนใจ (ผูกกิจกรรมติดตาม)",
    "2_1_todo_queue": "Process 2.1 — คิวติดตามผู้สนใจประจำวัน (เลยกำหนด / วันนี้ / ยังไม่เคยติดตาม)",
    "2_1_ai_priority": "Process 2.1 — คิวงานจัดลำดับความสำคัญผู้สนใจด้วย Machine Learning (Hot / Warm / Cold)",
    "2_2_activity_form": "Process 2.2 — บันทึกกิจกรรมการติดต่อผู้สนใจ (Call / Line / Email / Meeting)",
    "2_2_activity_timeline": "Process 2.2 — ไทม์ไลน์ประวัติการติดต่อที่อัปเดตแบบเรียลไทม์",
    "2_3_quotation_form": "Process 2.3 — ออกใบเสนอราคา (เลือกสินค้า + คำนวณส่วนลดแคมเปญอัตโนมัติ)",
    "2_3_quotation_issued": "Process 2.3 — ใบเสนอราคาที่ออกสำเร็จพร้อมรหัสการขาย (SL)",
    "3_1_order_review": "Process 3.1 — ตรวจสอบและยืนยันคำสั่งซื้อจากใบเสนอราคา",
    "3_2_payment_check": "Process 3.2 — ตรวจสอบสลิปโอนเงินและการชำระเงินของลูกค้า",
    "3_3_receipt_issued": "Process 3.3 — ออกใบเสร็จรับเงินสมบูรณ์ + ยกระดับสถานะเป็นลูกค้า (CUSTOMER)",
    "4_1_ticket_form": "Process 4.1 — รับแจ้งและเปิดเคสปัญหาการใช้งาน (ระบุระดับความเร่งด่วน)",
    "4_1_ticket_created": "Process 4.1 — เคสปัญหาถูกบันทึกเข้าระบบพร้อมออกเลขที่ Ticket_ID",
    "4_2_ticket_chat": "Process 4.2 — ห้องสนทนาและบันทึกความคืบหน้าการแก้ไขปัญหาระหว่างเจ้าหน้าที่กับลูกค้า",
    "4_3_ticket_closed": "Process 4.3 — ปิดเคสสำเร็จพร้อมบันทึกสรุปผลการแก้ไข",
    "4_3_rating_given": "Process 4.3 — ลูกค้าประเมินความพึงพอใจและให้คะแนน 5 ดาวผ่าน Portal",
    "5_1_6_4_campaign_roi": "Process 5.1 — แดชบอร์ดวิเคราะห์ประสิทธิภาพและการประเมินความคุ้มค่าแคมเปญ (Campaign ROI)",
    "5_2_sales_report": "Process 5.2 — รายงานสรุปยอดขาย (Leaderboard รายบุคคล / สินค้า / ช่องทาง + ส่งออก CSV)",
    "portal_home": "Portal จำลอง — หน้าหลักมุมมองสำหรับผู้สนใจและลูกค้า (External Entity)",
    "6_1_lead_scoring": "AI Feature 1 — ผลการวิเคราะห์โมเดลพยากรณ์โอกาสปิดการขาย (Lead Scoring & ROC-AUC)",
    "6_2_rfm": "AI Feature 2 — การแบ่งกลุ่มลูกค้าเชิงกลยุทธ์ด้วย RFM Model & K-Means",
    "6_3_churn": "AI Feature 3 — ดัชนีประเมินสุขภาพความสัมพันธ์และสัญญาณเตือนความเสี่ยงการยกเลิก (Churn Risk)",
    # ภาพเดิมสำหรับ Backward compatibility
    "1_1_marketing": "Process 1.1 / 1.2 — รับข้อมูลแคมเปญ + ลงทะเบียนผู้สนใจ",
    "1_2_portal_register": "Process 1.2 — ผู้สนใจลงทะเบียนเองผ่าน Portal",
    "3_x_order_pipeline": "Process 3.1–3.3 — รับคำสั่งซื้อ / ตรวจชำระเงิน / ออกใบเสร็จ",
    "4_x_support": "Process 4.1–4.3 — รับแจ้ง / แก้ไข / ประเมินผลบริการ",
}


def main() -> None:
    files = sorted(glob.glob(os.path.join(EVID, "*.png")))
    lines = ["# หลักฐานการทดลอง (DFD Activity Evidence)\n",
             "สร้างอัตโนมัติจาก `pytest tests/e2e` (Playwright)\n"]
    for f in files:
        key = os.path.splitext(os.path.basename(f))[0]
        lines.append(f"## {CAPTION.get(key, key)}\n\n![{key}]({os.path.basename(f)})\n")
    out = os.path.join(EVID, "README.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"เขียน {out} ({len(files)} ภาพ)")


if __name__ == "__main__":
    main()
