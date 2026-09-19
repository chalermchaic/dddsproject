#!/usr/bin/env python3
"""
build_user_manual_docx.py
สคริปต์สร้างคู่มือการใช้งานระบบ (User Manual) ฉบับสมบูรณ์ในรูปแบบ Word (.docx)
โครงการ: ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM & Data Science Analytics Platform)
วิชา: 070115302 การออกแบบฐานข้อมูลสำหรับวิทยาศาสตร์ข้อมูล (DDDS)

ครอบคลุม 14 กิจกรรมย่อยตาม DFD Process 1.0 - 5.0 + AI Analytics 4 ด้าน
แทรกภาพหน้าจอ UI จริงจาก docs/evidence/ ครบถ้วน 27 ภาพ
ตัดเนื้อหาเกินขอบเขต (ปกซ้ำซ้อน, ทฤษฎีกว้างๆ, Docker) พร้อมนำไปผนวกท้ายเล่มรายงาน
"""
import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
EVID = ROOT / "docs" / "evidence"
OUTPUT_DOCX = ROOT / "docs" / "user_manual.docx"

# Color Palette (Deep Navy / Professional Theme)
PRIMARY_COLOR = RGBColor(15, 23, 42)     # #0F172A
SECONDARY_COLOR = RGBColor(30, 58, 138)  # #1E3A8A
ACCENT_COLOR = RGBColor(14, 116, 144)    # #0E7490
TEXT_DARK = RGBColor(51, 65, 85)         # #334155
MUTED_TEXT = RGBColor(100, 116, 139)     # #64748B
BG_LIGHT_HEX = "F8FAFC"
HEADER_BG_HEX = "1E3A8A"


def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_callout(doc, text_prefix, text_body, alert_type="NOTE"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.5)
    
    border_color = "0E7490" if alert_type == "NOTE" else "E11D48"
    bg_color = "F0F9FF" if alert_type == "NOTE" else "FFF1F2"
    
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r1 = p.add_run(f"{text_prefix}: ")
    r1.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = SECONDARY_COLOR
    
    r2 = p.add_run(text_body)
    r2.font.size = Pt(10)
    r2.font.color.rgb = TEXT_DARK


def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(8)
        for r in h.runs:
            r.font.color.rgb = SECONDARY_COLOR
            r.font.size = Pt(16)
            r.bold = True
    elif level == 2:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        for r in h.runs:
            r.font.color.rgb = PRIMARY_COLOR
            r.font.size = Pt(13)
            r.bold = True
    elif level == 3:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        for r in h.runs:
            r.font.color.rgb = ACCENT_COLOR
            r.font.size = Pt(11)
            r.bold = True
    return h


def add_image_if_exists(doc, img_name, caption_text, width=Inches(5.8)):
    img_path = EVID / f"{img_name}.png"
    if not img_path.exists():
        print(f"⚠️  คำเตือน: ไม่พบไฟล์ภาพ {img_path.name}")
        p = doc.add_paragraph(f"[รูปภาพ: {img_name}.png - ไม่พบไฟล์]")
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        return
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=width)
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(10)
    run_cap = p_cap.add_run(f"รูปที่: {caption_text}")
    run_cap.font.size = Pt(9.5)
    run_cap.font.italic = True
    run_cap.font.color.rgb = MUTED_TEXT


def build_manual_document():
    doc = Document()
    
    # Page setup
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.9)
        sec.right_margin = Inches(0.9)
    
    # Title Section (Compact Academic Header)
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("คู่มือการใช้งานระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ")
    run_title.font.size = Pt(20)
    run_title.bold = True
    run_title.font.color.rgb = SECONDARY_COLOR
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(12)
    run_sub = p_sub.add_run("Smart CRM & Data Science Analytics Platform (v1.2.1) — ภาคผนวกคู่มือปฏิบัติการ")
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = MUTED_TEXT
    
    add_callout(
        doc,
        "โครงสร้างคู่มือฉบับกระชับ",
        "คู่มือนี้จัดทำขึ้นสำหรับแนบเป็นภาคผนวกในเล่มรายงานโครงงานวิชา DDDS โดยอธิบายลำดับการใช้งานจริงครบทั้ง 14 กิจกรรมย่อยตาม Data Flow Diagram (Process 1.0 ถึง 5.0) พร้อมหน้าต่าง Customer Portal จำลอง และการประมวลผลโมเดล Data Science 4 ด้าน โดยอ้างอิงจากภาพหน้าจอระบบจริงทั้งหมด"
    )
    
    # -------------------------------------------------------------
    # หมวดที่ 1: การเข้าสู่ระบบและการควบคุมสิทธิ์ (Auth & RBAC)
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "1. การเข้าสู่ระบบและการควบคุมสิทธิ์การใช้งาน (Auth & RBAC)", level=1)
    
    p = doc.add_paragraph(
        "ระบบ Smart CRM ใช้สถาปัตยกรรมแบบ Role-Based Access Control (RBAC) โดยเชื่อมโยงบัญชีผู้ใช้เข้ากับตาราง EMPLOYEE เพื่อจำกัดการเข้าถึงหน้าจอและฟังก์ชันการทำงานตามหน้าที่ความรับผิดชอบอย่างปลอดภัย นอกจากนี้ยังมีปุ่มเข้าใช้งานแบบ Guest เพื่อจำลองมุมมองของลูกค้าภายนอก (Customer Portal)"
    )
    p.paragraph_format.space_after = Pt(6)
    
    add_image_if_exists(doc, "00_login", "1.1 หน้าจอหลักในการเลือกบัญชีผู้ใช้เข้าสู่ระบบ (Authentication Portal)")
    
    p_tbl = doc.add_paragraph("ตารางที่ 1.1: สิทธิ์การเข้าถึงเมนูและหน้าจอการทำงานของแต่ละบทบาท")
    p_tbl.paragraph_format.space_before = Pt(6)
    p_tbl.paragraph_format.space_after = Pt(4)
    p_tbl.paragraph_format.keep_with_next = True
    
    table = doc.add_table(rows=6, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["บทบาท (Role)", "บัญชีตัวอย่าง", "หน้าจอที่เข้าถึงได้", "หน้าที่รับผิดชอบหลัก"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        set_cell_background(cell, HEADER_BG_HEX)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(9.5)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
    
    role_data = [
        ("Admin (ผู้ดูแลระบบ)", "admin1 (ธนวัฒน์)", "ครบทุกหน้า (1-6)", "ตรวจสอบภาพรวม, สิทธิ์, วิเคราะห์ระดับบริหาร"),
        ("Marketing (ฝ่ายการตลาด)", "marketing1 (ชนิกานต์)", "Home, Marketing, Profile, Dashboard", "จัดการแคมเปญ, รับ Lead, ติดตาม Campaign ROI"),
        ("Sales (ฝ่ายขาย)", "sale1 (ณัฐวุฒิ)", "Home, Sales, Billing, Profile, Dashboard", "คิวงาน AI, บันทึกติดต่อ, ออกใบเสนอราคา/ใบเสร็จ"),
        ("Support (ฝ่ายบริการ)", "cs1 (ศุภชัย)", "Home, Profile, Support, Dashboard", "รับเคสปัญหา, สนทนาประสานงาน, สรุปผลบริการ"),
        ("Guest (ลูกค้าจำลอง)", "ผู้สนใจ / ลูกค้า", "Customer Portal (หน้า 9)", "ลงทะเบียน, ยืนยันคำสั่งซื้อ, แนบสลิป, ให้คะแนน"),
    ]
    for row_idx, rdata in enumerate(role_data, start=1):
        bg = BG_LIGHT_HEX if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(rdata):
            cell = table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            run = p.add_run(text)
            run.font.size = Pt(9)
            run.font.color.rgb = TEXT_DARK
    
    # -------------------------------------------------------------
    # หมวดที่ 2: กระบวนการที่ 1.0 — การจัดการการตลาดและผู้สนใจ
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "2. กระบวนการที่ 1.0: งานการตลาดและการลงทะเบียนผู้สนใจ", level=1)
    
    p = doc.add_paragraph(
        "กระบวนการที่ 1.0 รับผิดชอบการบริหารงบประมาณและโปรโมชันแคมเปญ (Data Store: CAMPAIGN) รวมถึงการรวบรวมข้อมูลผู้สนใจ (Data Store: LEAD) ทั้งจากพนักงานการตลาดและจากการลงทะเบียนด้วยตนเองผ่าน Portal"
    )
    p.paragraph_format.space_after = Pt(6)
    
    # 1.1
    add_heading_with_spacing(doc, "กิจกรรม 1.1: บันทึกและจัดการแคมเปญโปรโมชัน", level=2)
    p = doc.add_paragraph(
        "พนักงานการตลาดล็อกอินด้วยบัญชี `marketing1` เข้าสู่หน้า 'งานการตลาด' (1_marketing.py) เลือกแท็บ '➕ สร้างแคมเปญ' กรอกชื่อแคมเปญ รายละเอียด งบประมาณ เปอร์เซ็นต์ส่วนลด และช่วงเวลาใช้งาน จากนั้นกดปุ่ม '💾 บันทึกแคมเปญ' ข้อมูลจะถูกบันทึกลงตาราง CAMPAIGN พร้อมคำนวณรหัส CMP อัตโนมัติ"
    )
    add_image_if_exists(doc, "1_1_campaign_form", "2.1 ฟอร์มบันทึกแคมเปญโปรโมชันใหม่พร้อมกำหนดงบประมาณและส่วนลด")
    add_image_if_exists(doc, "1_1_campaign_saved", "2.2 รายการแคมเปญในระบบหลังบันทึกสำเร็จพร้อมแสดงงบและสถานะ")
    
    # 1.2
    add_heading_with_spacing(doc, "กิจกรรม 1.2: ลงทะเบียนและบันทึกข้อมูลผู้สนใจ (Lead Intake)", level=2)
    p = doc.add_paragraph(
        "การรับผู้สนใจเข้าสู่ระบบสามารถดำเนินการได้ 2 รูปแบบ:\n"
        "1. ฝ่ายการตลาดกรอกเอง: ในแท็บ '🙋 บันทึกผู้สนใจใหม่' กรอกชื่อ เบอร์โทร ช่องทางที่พบ (Facebook, Google Ads ฯลฯ) และเลือกแคมเปญที่ดึงดูดใจ\n"
        "2. ผู้สนใจลงทะเบียนด้วยตนเอง: เข้าสู่หน้า Customer Portal (แท็บ ① ลงทะเบียน) เพื่อส่งข้อมูลความสนใจเข้ามาในระบบโดยตรง"
    )
    add_image_if_exists(doc, "1_2_lead_form", "2.3 ฟอร์มบันทึกผู้สนใจรายใหม่โดยฝ่ายการตลาด")
    add_image_if_exists(doc, "1_2_lead_saved", "2.4 ยืนยันการบันทึกผู้สนใจสำเร็จพร้อมออกรหัส Lead_ID ทันที")
    add_image_if_exists(doc, "1_2_portal_register", "2.5 มุมมองผู้สนใจลงทะเบียนขอข้อมูลด้วยตนเองผ่านหน้า Customer Portal")
    
    # 1.3
    add_heading_with_spacing(doc, "กิจกรรม 1.3: ส่งข้อมูลโปรโมชันเจาะจงแก่ผู้สนใจ", level=2)
    p = doc.add_paragraph(
        "ระบบเปิดโอกาสให้พนักงานส่งโปรโมชันที่เหมาะสมกับผู้สนใจแต่ละราย โดยเชื่อมโยงส่วนลดของแคมเปญและสร้างประวัติกิจกรรม (LEAD_ACTIVITY) ประเภท 'ส่งโปรโมชัน' เพื่อให้ฝ่ายขายสามารถติดตามต่อได้อย่างมีประสิทธิผล"
    )
    add_image_if_exists(doc, "1_3_promo_sent", "2.6 หน้าจอการจัดส่งข้อมูลโปรโมชันเจาะจงแก่ผู้สนใจพร้อมบันทึกประวัติการติดต่อ")
    
    # -------------------------------------------------------------
    # หมวดที่ 3: กระบวนการที่ 2.0 & 3.0 — งานขาย การเสนอราคา และการรับชำระเงิน
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "3. กระบวนการที่ 2.0 & 3.0: งานขาย การติดตาม และการรับชำระเงิน", level=1)
    
    p = doc.add_paragraph(
        "กระบวนการงานขายครอบคลุมการติดตามผู้สนใจตามลำดับความสำคัญของ Machine Learning การบันทึกกิจกรรมติดต่อ การออกใบเสนอราคา ตรวจสอบคำสั่งซื้อ ยืนยันสลิปโอนเงิน และการออกใบเสร็จรับเงินเพื่อยกระดับผู้สนใจเป็นลูกค้าทางการ (Data Store: CUSTOMER)"
    )
    
    # 2.1
    add_heading_with_spacing(doc, "กิจกรรม 2.1: คิวติดตามผู้สนใจประจำวัน & AI Priority Queue", level=2)
    p = doc.add_paragraph(
        "พนักงานขายล็อกอิน `sale1` เข้าหน้า 'ติดตามการขาย' (2_sales_followup.py) จะพบระบบจัดคิวงาน 2 รูปแบบ:\n"
        "1. คิวติดตามประจำวัน (To-Do): แบ่งผู้สนใจตามกำหนดเวลา ได้แก่ กลุ่มเลยกำหนดนัด, กลุ่มที่ต้องติดต่อวันนี้, และกลุ่มที่ยังไม่เคยได้รับการติดต่อ\n"
        "2. คิวงาน AI Lead Scoring: โมเดล Random Forest จัดกลุ่มผู้สนใจเป็น Hot (>70%), Warm (40-70%), และ Cold (<40%) เพื่อให้ทีมขายเลือกโฟกัสกลุ่มที่มีโอกาสปิดการขายสูงสุดก่อน"
    )
    add_image_if_exists(doc, "2_1_todo_queue", "3.1 คิวงานติดตามผู้สนใจประจำวันตามกำหนดนัดหมาย (To-Do Queue)")
    add_image_if_exists(doc, "2_1_ai_priority", "3.2 คิวงานจัดลำดับความสำคัญผู้สนใจด้วย Machine Learning (AI Priority Queue)")
    
    # 2.2
    add_heading_with_spacing(doc, "กิจกรรม 2.2: บันทึกกิจกรรมการติดต่อผู้สนใจ (Lead Activity Logging)", level=2)
    p = doc.add_paragraph(
        "เมื่อโทรหรือส่งข้อความหาผู้สนใจ พนักงานขายเลือกแท็บ '🔍 ค้นหา & บันทึกกิจกรรม' เลือกช่องทาง (โทรศัพท์, LINE, อีเมล, ประชุม) ระบุผลการพูดคุย และตั้งวันนัดติดตามครั้งถัดไป ระบบจะบันทึกลงตาราง LEAD_ACTIVITY และอัปเดตไทม์ไลน์ประวัติการติดต่อทางคอลัมน์ขวาแบบเรียลไทม์"
    )
    add_image_if_exists(doc, "2_2_activity_form", "3.3 ฟอร์มบันทึกผลการติดต่อผู้สนใจพร้อมกำหนดวันนัดหมายครั้งถัดไป")
    add_image_if_exists(doc, "2_2_activity_timeline", "3.4 ไทม์ไลน์แสดงประวัติการติดต่อย้อนหลังของ Lead รายนั้นอย่างต่อเนื่อง")
    
    # 2.3
    add_heading_with_spacing(doc, "กิจกรรม 2.3: การออกใบเสนอราคา (Quotation Generation)", level=2)
    p = doc.add_paragraph(
        "เข้าสู่หน้า 'คำสั่งซื้อ & บิล' (3_order_billing.py) แท็บ '📝 ออกใบเสนอราคา' เลือกผู้สนใจ เลือกรหัสสินค้าและจำนวน ระบบจะดึงส่วนลดจากแคมเปญที่ผู้สนใจผูกไว้อัตโนมัติ พร้อมคำนวณยอดสุทธิและสร้างเอกสารใบเสนอราคา (รหัส SALE: สถานะ 'ออกใบเสนอราคาแล้ว')"
    )
    add_image_if_exists(doc, "2_3_quotation_form", "3.5 หน้าจอเลือกสินค้าและคำนวณส่วนลดอัตโนมัติในการออกใบเสนอราคา")
    add_image_if_exists(doc, "2_3_quotation_issued", "3.6 ใบเสนอราคาที่สร้างสำเร็จพร้อมรหัสการขาย (SL) และรายละเอียดครบถ้วน")
    
    # 3.1 - 3.3
    add_heading_with_spacing(doc, "กิจกรรม 3.1–3.3: ตรวจสอบคำสั่งซื้อ ตรวจสลิปโอนเงิน และออกใบเสร็จ", level=2)
    p = doc.add_paragraph(
        "การเปลี่ยนคำสั่งซื้อเป็นยอดขายสำเร็จแบ่งเป็น 3 ขั้นตอนย่อยอย่างรัดกุม:\n"
        "• กิจกรรม 3.1 (ตรวจคำสั่งซื้อ): ฝ่ายขายตรวจรายการสินค้าที่ลูกค้าส่งคำสั่งซื้อเข้ามา แล้วกดยืนยันเพื่อรอรับชำระเงิน\n"
        "• กิจกรรม 3.2 (ตรวจสลิปโอนเงิน): ฝ่ายขายเปิดดูรูปภาพสลิปที่ลูกค้าอัปโหลดผ่าน Portal ตรวจสอบยอดเงิน และกดยืนยันการรับเงิน\n"
        "• กิจกรรม 3.3 (ออกใบเสร็จรับเงิน): ระบบเปลี่ยนสถานะการขายเป็น 'ปิดการขายสำเร็จ' พร้อมยกระดับ Lead เป็น CUSTOMER อัตโนมัติ และสร้างเอกสารใบเสร็จรับเงินให้ดาวน์โหลด"
    )
    add_image_if_exists(doc, "3_1_order_review", "3.7 หน้าจอรับและตรวจสอบความถูกต้องของคำสั่งซื้อ (Process 3.1)")
    add_image_if_exists(doc, "3_2_payment_check", "3.8 หน้าจอดูดอกเบี้ย/สลิปหลักฐานการโอนเงินที่ลูกค้าแนบมา (Process 3.2)")
    add_image_if_exists(doc, "3_3_receipt_issued", "3.9 หน้าจอออกใบเสร็จรับเงินและระบบยกระดับเป็น CUSTOMER ทันที (Process 3.3)")
    
    # -------------------------------------------------------------
    # หมวดที่ 4: กระบวนการที่ 4.0 — การบริการลูกค้าและการประเมินความพึงพอใจ
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "4. กระบวนการที่ 4.0: บริการหลังการขายและประเมินผลบริการ", level=1)
    
    p = doc.add_paragraph(
        "กระบวนการที่ 4.0 รับผิดชอบการรับเรื่องร้องเรียน การแก้ไขปัญหาทางเทคนิค (Data Store: TICKET & TICKET_MESSAGE) และการเปิดให้ลูกค้าประเมินความพึงพอใจ 1-5 ดาวเพื่อนำไปใช้คำนวณ Customer Health Score"
    )
    
    # 4.1
    add_heading_with_spacing(doc, "กิจกรรม 4.1: รับแจ้งและเปิดเคสปัญหา (Ticket Intake)", level=2)
    p = doc.add_paragraph(
        "เจ้าหน้าที่บริการลูกค้าล็อกอิน `cs1` เข้าสู่หน้า 'รับแจ้งปัญหา' (5_support_ticket.py) สามารถเปิดเคสใหม่โดยเลือกลูกค้า ระบุหมวดหมู่ปัญหา (ระบบขัดข้อง, สินค้าชำรุด, สอบถามการใช้งาน) และเลือกระดับความเร่งด่วน โดยลูกค้าสามารถแจ้งเคสผ่าน Portal เองได้เช่นกัน"
    )
    add_image_if_exists(doc, "4_1_ticket_form", "4.1 ฟอร์มเปิดเคสแจ้งปัญหาพร้อมระบุหมวดหมู่และความเร่งด่วน")
    add_image_if_exists(doc, "4_1_ticket_created", "4.2 เคสปัญหาถูกบันทึกเข้าระบบพร้อมออกรหัส Ticket_ID (TK)")
    
    # 4.2
    add_heading_with_spacing(doc, "กิจกรรม 4.2: ประสานงาน สนทนา และบันทึกผลการแก้ไขปัญหา", level=2)
    p = doc.add_paragraph(
        "ในแท็บ 'คิวเคส & สนทนา' เจ้าหน้าที่และลูกค้าสามารถส่งข้อความโต้ตอบกันในห้องสนทนาของตั๋วใบนั้นได้แบบสองทาง ทุกข้อความจะบันทึกลงตาราง TICKET_MESSAGE พร้อมระบุผู้ส่งและเวลาอย่างชัดเจน"
    )
    add_image_if_exists(doc, "4_2_ticket_chat", "4.3 ห้องสนทนาและบันทึกความคืบหน้าระหว่างเจ้าหน้าที่กับลูกค้า")
    
    # 4.3
    add_heading_with_spacing(doc, "กิจกรรม 4.3: ปิดเคส สรุปผล และประเมินความพึงพอใจ 5 ดาว", level=2)
    p = doc.add_paragraph(
        "เมื่อแก้ปัญหาเสร็จสิ้น เจ้าหน้าที่กดยืนยัน 'ปิดเคสสำเร็จ' พร้อมระบุสรุปผลการแก้ไข จากนั้นในฝั่งลูกค้าเมื่อเข้าสู่ Customer Portal แท็บ ⑤ จะพบรายการเคสที่ปิดแล้ว และสามารถให้คะแนนดาว (1-5) พร้อมข้อคิดเห็นกลับมายังระบบได้"
    )
    add_image_if_exists(doc, "4_3_ticket_closed", "4.4 เจ้าหน้าที่สรุปแนวทางแก้ไขและยืนยันปิดเคสบริการสำเร็จ")
    add_image_if_exists(doc, "4_3_rating_given", "4.5 ลูกค้าประเมินผลความพึงพอใจและให้คะแนน 5 ดาวผ่าน Customer Portal")
    
    # -------------------------------------------------------------
    # หมวดที่ 5: พอร์ทัลจำลองสำหรับลูกค้า (Customer Portal)
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "5. หน้าพอร์ทัลจำลองสำหรับลูกค้าภายนอก (Customer Portal)", level=1)
    
    p = doc.add_paragraph(
        "เพื่อจำลองการไหลของข้อมูล (Inbound & Outbound Data Flows) จาก External Entity 'ผู้สนใจ' และ 'ลูกค้า' เข้าสู่ระบบอย่างสมบูรณ์ตาม DFD ทางทีมพัฒนาได้สร้างหน้า `9_portal.py` โดยแบ่งเป็น 5 แถบการทำงานหลัก:"
    )
    p.paragraph_format.space_after = Pt(4)
    
    portal_points = [
        "① ลงทะเบียนขอข้อมูลโปรโมชัน: ส่งข้อมูลติดต่อและความต้องการสินค้าเข้าสู่ตาราง LEAD",
        "② ตรวจสอบใบเสนอราคา: สวมบทบาทเป็นผู้สนใจเพื่อดูใบเสนอราคาที่ฝ่ายขายออกให้",
        "③ ยืนยันคำสั่งซื้อ: กดยืนยันการสั่งซื้อเพื่อส่งคำขอต่อไปยังฝ่ายขาย",
        "④ อัปโหลดสลิปหลักฐานการโอนเงิน: แนบไฟล์รูปภาพสลิปจริงเข้าสู่โฟลเดอร์ uploads/",
        "⑤ ประเมินความพึงพอใจบริการ: ให้คะแนน 1-5 ดาวสำหรับเคสซัพพอร์ตที่ปิดเรียบร้อยแล้ว",
    ]
    for pt in portal_points:
        p_pt = doc.add_paragraph(style='List Bullet')
        p_pt.paragraph_format.space_before = Pt(2)
        p_pt.paragraph_format.space_after = Pt(2)
        r = p_pt.add_run(pt)
        r.font.size = Pt(10)
        r.font.color.rgb = TEXT_DARK
    
    add_image_if_exists(doc, "portal_home", "5.1 หน้าหลักศูนย์บริการตนเองสำหรับผู้สนใจและลูกค้า (Customer Portal)")
    
    # -------------------------------------------------------------
    # หมวดที่ 6: การวิเคราะห์ข้อมูลและแดชบอร์ด AI (Analytics Engine)
    # -------------------------------------------------------------
    add_heading_with_spacing(doc, "6. การวิเคราะห์ข้อมูลและแดชบอร์ด AI (Data Science Analytics)", level=1)
    
    p = doc.add_paragraph(
        "ในหน้า 'แดชบอร์ดอัจฉริยะ' (6_analytics_dashboard.py) รวบรวมการประมวลผลทางวิทยาศาสตร์ข้อมูล 4 มิติ และรายงานยอดขายเชิงบริหาร (Process 5.1 & 5.2):"
    )
    
    # 6.1
    add_heading_with_spacing(doc, "ฟีเจอร์ AI ที่ 1: โมเดลพยากรณ์โอกาสปิดการขาย (Lead Scoring)", level=2)
    p = doc.add_paragraph(
        "ใช้ Machine Learning (Random Forest / Logistic Regression) คำนวณความน่าจะเป็นที่ผู้สนใจจะซื้อสินค้า โดยวิเคราะห์จากความถี่กิจกรรม จำนวนช่องทางที่โต้ตอบ ระยะเวลาการตอบกลับ และส่วนลดของแคมเปญ พร้อมแสดงกราฟ ROC-AUC (~0.84) และ Feature Importance"
    )
    add_image_if_exists(doc, "6_1_lead_scoring", "6.1 แดชบอร์ด AI Lead Scoring แสดงผล ROC-AUC Curve และปัจจัยที่มีอิทธิพลต่อการซื้อ")
    
    # 6.2
    add_heading_with_spacing(doc, "ฟีเจอร์ AI ที่ 2: การแบ่งกลุ่มลูกค้าเชิงกลยุทธ์ (RFM Segmentation)", level=2)
    p = doc.add_paragraph(
        "คำนวณคะแนน Recency (วันซื้อล่าสุด), Frequency (ความถี่ในการซื้อ), และ Monetary (ยอดซื้อรวม) จัดกลุ่มลูกค้าออกเป็น Champions, Loyal, At Risk, Lost พร้อมแสดงตาราง Segment Matrix และคำแนะนำเชิงกลยุทธ์การตลาดรายกลุ่ม"
    )
    add_image_if_exists(doc, "6_2_rfm", "6.2 แดชบอร์ดแบ่งกลุ่มลูกค้า RFM Matrix และการกระจายตัวของมูลค่าลูกค้า")
    
    # 6.3
    add_heading_with_spacing(doc, "ฟีเจอร์ AI ที่ 3: ดัชนีสุขภาพลูกค้าและความเสี่ยงการยกเลิก (Churn & Health Score)", level=2)
    p = doc.add_paragraph(
        "ประเมิน Customer Health Score (0-100) จาก 5 มิติ ได้แก่ ความสดใหม่ของการซื้อ ความถี่ ยอดเงิน จำนวนเคสปัญหา และความเร็วในการแก้ไขปัญหา พร้อมแสดง Radar Chart แจกแจงจุดแข็ง/จุดอ่อน และส่งสัญญาณเตือนลูกค้ากลุ่มเสี่ยงสูง (🔴 High Risk)"
    )
    add_image_if_exists(doc, "6_3_churn", "6.3 แดชบอร์ดประเมินสุขภาพลูกค้า Customer Health Score และการเตือนความเสี่ยง Churn")
    
    # 6.4
    add_heading_with_spacing(doc, "ฟีเจอร์ที่ 4: การวิเคราะห์ความคุ้มค่าแคมเปญ (Process 5.1: Campaign ROI)", level=2)
    p = doc.add_paragraph(
        "คำนวณผลตอบแทนจากงบประมาณแคมเปญการตลาด เปรียบเทียบ Cost per Lead (CPL), อัตราการปิดการขาย (Conversion Rate) และ ROI สุทธิ เพื่อชี้วัดว่าแคมเปญใดสร้างกำไรสูงสุดแก่บริษัท"
    )
    add_image_if_exists(doc, "5_1_6_4_campaign_roi", "6.4 การประเมินผลตอบแทนแคมเปญการตลาด (Campaign ROI & Efficiency)")
    
    # 5.2
    add_heading_with_spacing(doc, "กิจกรรม 5.2: รายงานสรุปยอดขายเชิงบริหาร (Sales Performance Report)", level=2)
    p = doc.add_paragraph(
        "สรุปยอดขายรวม จำนวนใบเสร็จ และค่าเฉลี่ยต่อบิล สามารถกรองตามช่วงเวลา (เดือน/ไตรมาส/ปี) พร้อมแสดง Leaderboard อันดับพนักงานขายยอดเยี่ยม ยอดขายแยกตามประเภทสินค้า และปุ่มดาวน์โหลดรายงานในรูปแบบไฟล์ CSV"
    )
    add_image_if_exists(doc, "5_2_sales_report", "6.5 รายงานสรุปยอดขาย Leaderboard พนักงานขาย และปุ่มส่งออกรายงาน CSV")
    
    # Save output docx
    doc.save(str(OUTPUT_DOCX))
    print(f"✅ สร้างเอกสารสำเร็จ: {OUTPUT_DOCX}")
    return OUTPUT_DOCX


if __name__ == "__main__":
    build_manual_document()
