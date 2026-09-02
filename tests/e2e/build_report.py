"""ประกอบ screenshot ใน docs/evidence/ เป็น README.md สำหรับแนบภาคผนวกรายงาน"""
import glob
import os

EVID = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "evidence")

CAPTION = {
    "00_login": "หน้าเลือกบัญชีผู้ใช้ (Context DFD — external entity)",
    "menu_admin1": "เมนูของ admin — เห็นครบทุกกระบวนการ",
    "menu_marketing1": "เมนูของฝ่ายการตลาด",
    "menu_sale1": "เมนูของฝ่ายขาย",
    "menu_cs1": "เมนูของฝ่ายบริการลูกค้า",
    "1_1_marketing": "Process 1.1 / 1.2 — รับข้อมูลแคมเปญ + ลงทะเบียนผู้สนใจ",
    "1_2_portal_register": "Process 1.2 — ผู้สนใจลงทะเบียนเองผ่าน Portal",
    "2_1_todo_queue": "Process 2.1 — คิวติดตามประจำวัน",
    "3_x_order_pipeline": "Process 3.1–3.3 — รับคำสั่งซื้อ / ตรวจชำระเงิน / ออกใบเสร็จ",
    "4_x_support": "Process 4.1–4.3 — รับแจ้ง / แก้ไข / ประเมินผลบริการ",
    "5_2_sales_report": "Process 5.2 — รายงานสรุปยอดขาย",
    "portal_home": "Portal — มุมผู้สนใจ/ลูกค้า",
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
