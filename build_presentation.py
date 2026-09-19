"""
build_presentation.py - Professional 14-Slide Presentation Deck Generator
Strictly adhering to plan_3_presentation_slides.md Section 8 (Restructure Round 3 - 20 ก.ย. 69):
- 14 Slides total (Replaces Section 2 table completely)
- Slide 1: Title (Larger fonts, correct roles from 7.9)
- Slide 2: Project Objective (Single prominent objective sentence + 5 process flow icons/cards, removes Problem Statement & 3 Focus cards)
- Slide 3: How CRM Works (Image-focused, 4 role screenshots with short 3-5 word labels, stats moved to Speaker Notes)
- Slide 4: 3-Tier System Architecture (Database -> Analytics -> Web UI, Docker in a small note)
- Slide 5: DFD Context & Level 0 (Large visual area, 0 errors)
- Slide 6: Peter Chen ERD & 3NF (Large visual area, 10 entities)
- Slide 7: Feature 1 Lead Scoring ("ฟีเจอร์ที่ 1", RF 300 trees, LD0264 real case)
- Slide 8: Feature 2 RFM Segmentation ("ฟีเจอร์ที่ 2", Quintile + K-Means, CU0175 real case)
- Slide 9: Feature 3 Churn & Health ("ฟีเจอร์ที่ 3", 5-dim weighted score, CU0178 real case)
- Slide 10: Feature 4 Campaign Financial ROI ("ฟีเจอร์ที่ 4", ROI/ROAS/CAC, Digital Ads Q3 real case)
- Slide 11: Role-Based Access Control RBAC (Report-style table: Role, Access Scope, Menus)
- Slide 12: System Verification & Testing (Concise: pytest 100%, 2 real bugs, refers to plan_4)
- Slide 13: Project Conclusion (DFD/ERD as foundational Data Model enabling working Web Prototype)
- Slide 14: Q&A & Live Demo Hand-off (10-minute live demo announcement)
"""
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Unified Modern Light Palette
BG_COLOR = RGBColor(248, 250, 252)       # #F8FAFC (Clean Light Canvas)
CARD_BG = RGBColor(255, 255, 255)        # #FFFFFF (Pure White Cards)
CARD_BORDER = RGBColor(226, 232, 240)    # #E2E8F0 (Subtle Slate Border)
PRIMARY_BLUE = RGBColor(37, 99, 235)     # #2563EB (Royal Primary)
SKY_BLUE = RGBColor(2, 132, 199)         # #0284C7 (Accent Cyan/Sky)
DARK_NAVY = RGBColor(15, 23, 42)         # #0F172A (Deep Slate Text)
MUTED_SLATE = RGBColor(100, 116, 139)    # #64748B (Secondary Text)
BORDER_ACTIVE = RGBColor(191, 219, 254)  # #BFDBFE (Subtle Blue Accent Border)

# Semantic Colors
SEMANTIC_RED = RGBColor(220, 38, 38)     # #DC2626
SEMANTIC_GREEN = RGBColor(16, 185, 129)  # #10B981
SEMANTIC_AMBER = RGBColor(217, 119, 6)   # #D97706

FONT_FAMILY = "Segoe UI"

ROOT_DEV = r"c:\Users\momo\dev\dddsproject"
ROOT_DRIVE = r"g:\My Drive\Classroom\1 2569 Database Design for Data Science 01-02\dfderd"

def create_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    def add_slide_base(slide, tag, title, subtitle, slide_num, total_slides=17):
        # 1. Slide Canvas Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()

        # 2. Top Header Accent Bar
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.35), Inches(0.25), Inches(0.25))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = PRIMARY_BLUE
        top_bar.line.fill.background()

        # 3. Header Text Box
        tbox = slide.shapes.add_textbox(Inches(1.15), Inches(0.3), Inches(9.8), Inches(0.95))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        
        p0 = tf.paragraphs[0]
        p0.text = tag.upper()
        p0.font.name = FONT_FAMILY
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = PRIMARY_BLUE

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(19)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY

        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = FONT_FAMILY
            p2.font.size = Pt(10.5)
            p2.font.color.rgb = MUTED_SLATE

        # 4. Slide Number Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.2), Inches(0.35), Inches(1.35), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = CARD_BG
        pill.line.color.rgb = CARD_BORDER
        ptf = pill.text_frame
        ptf.margin_top = ptf.margin_bottom = ptf.margin_left = ptf.margin_right = 0
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = f"SLIDE {slide_num:02d} / {total_slides:02d}"
        pp.font.name = FONT_FAMILY
        pp.font.size = Pt(9)
        pp.font.bold = True
        pp.font.color.rgb = MUTED_SLATE

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: หน้าปกโครงงาน (Title Slide) - Larger fonts & Section 7.9 Roles
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_COLOR
    bg1.line.fill.background()

    # Top Brand Ribbon
    ribbon = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.65), Inches(11.733), Inches(0.08))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = PRIMARY_BLUE
    ribbon.line.fill.background()

    # Course Badge
    b1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.95), Inches(5.2), Inches(0.38))
    b1.fill.solid()
    b1.fill.fore_color.rgb = CARD_BG
    b1.line.color.rgb = BORDER_ACTIVE
    b1_tf = b1.text_frame
    b1_tf.margin_top = b1_tf.margin_bottom = b1_tf.margin_left = b1_tf.margin_right = 0
    bp = b1_tf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "070115302 DATABASE DESIGN FOR DATA SCIENCE (DDDS)"
    bp.font.name = FONT_FAMILY
    bp.font.size = Pt(10.5)
    bp.font.bold = True
    bp.font.color.rgb = PRIMARY_BLUE

    # Title & Subtitle Box (Enlarged Fonts)
    t1_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.48), Inches(11.733), Inches(2.4))
    t1_tf = t1_box.text_frame
    t1_tf.word_wrap = True
    t1_tf.margin_top = t1_tf.margin_bottom = t1_tf.margin_left = t1_tf.margin_right = 0
    tp1 = t1_tf.paragraphs[0]
    tp1.text = "Smart CRM & Data Science Analytics Platform"
    tp1.font.name = FONT_FAMILY
    tp1.font.size = Pt(34)
    tp1.font.bold = True
    tp1.font.color.rgb = DARK_NAVY

    tp2 = t1_tf.add_paragraph()
    tp2.text = "ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะด้วยการออกแบบฐานข้อมูลและการวิเคราะห์ข้อมูลขั้นสูง"
    tp2.font.name = FONT_FAMILY
    tp2.font.size = Pt(16.5)
    tp2.font.color.rgb = MUTED_SLATE
    tp2.space_before = Pt(4)

    tp3 = t1_tf.add_paragraph()
    tp3.text = "อาจารย์ผู้สอน: ผู้ช่วยศาสตราจารย์ ดร.ผุสดี บุญรอด  |  คณะเทคโนโลยีสารสนเทศและนวัตกรรมดิจิทัล มจพ. (KMUTNB)"
    tp3.font.name = FONT_FAMILY
    tp3.font.size = Pt(12)
    tp3.font.bold = True
    tp3.font.color.rgb = PRIMARY_BLUE
    tp3.space_before = Pt(6)

    # 4 Member Cards (Section 7.9 exact roles & enlarged font)
    team_members = [
        ("ริน", "เมธัญรัตน์ อัครนิธิเวช", "69-070118-5701-1", "UI + การนำเสนอ", "UI Design & Presentation"),
        ("ใหม่", "เฉลิมชัย ฉิมพายัพ", "69-070118-5702-9", "วางโครงสร้าง + Feature", "System Architecture & Feature Dev"),
        ("เฟรม", "สิรวิชญ์ จงสมนึก", "69-070118-5706-1", "คู่มือการใช้งาน + Demo", "User Manual & Live Demo"),
        ("ต้าร์", "วรพล มหาชัย", "69-070118-5705-3", "เอกสารรายงาน + Test", "Project Report & Testing")
    ]
    card_w = Inches(2.75)
    card_h = Inches(1.95)
    card_gap = Inches(0.24)
    start_x = Inches(0.8)
    start_y = Inches(4.3)

    for i, (nick, name, sid, role_th, role_en) in enumerate(team_members):
        cx = start_x + i * (card_w + card_gap)
        cbox = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, start_y, card_w, card_h)
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = CARD_BG
        cbox.line.color.rgb = CARD_BORDER
        cbox.line.width = Pt(1.2)
        ctf = cbox.text_frame
        ctf.word_wrap = True
        ctf.margin_top = Inches(0.2)
        ctf.margin_left = Inches(0.2)
        ctf.margin_right = Inches(0.2)

        cp1 = ctf.paragraphs[0]
        cp1.text = f"{i+1}. {nick} — {name}"
        cp1.font.name = FONT_FAMILY
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = DARK_NAVY

        cp2 = ctf.add_paragraph()
        cp2.text = f"รหัสนักศึกษา: {sid}"
        cp2.font.name = FONT_FAMILY
        cp2.font.size = Pt(10)
        cp2.font.color.rgb = PRIMARY_BLUE
        cp2.space_before = Pt(3)

        cp3 = ctf.add_paragraph()
        cp3.text = f"หน้าที่: {role_th}"
        cp3.font.name = FONT_FAMILY
        cp3.font.size = Pt(10)
        cp3.font.bold = True
        cp3.font.color.rgb = DARK_NAVY
        cp3.space_before = Pt(4)

        cp4 = ctf.add_paragraph()
        cp4.text = role_en
        cp4.font.name = FONT_FAMILY
        cp4.font.size = Pt(9)
        cp4.font.color.rgb = MUTED_SLATE

    # Bottom Footer
    foot = s1.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.4))
    ftf = foot.text_frame
    fp = ftf.paragraphs[0]
    fp.alignment = PP_ALIGN.CENTER
    fp.text = "⏱️ กำหนดการนำเสนอ: บรรยายสไลด์ 15 นาที  •  สาธิตระบบสด (Live Demo) 10 นาที  •  ถาม–ตอบ (Q&A) 5 นาที"
    fp.font.name = FONT_FAMILY
    fp.font.size = Pt(11.5)
    fp.font.color.rgb = MUTED_SLATE

    set_notes(s1, "สวัสดีครับ/ค่ะ คณาจารย์และเพื่อนๆ ทุกท่าน วันนี้กลุ่มพวกเราจะมานำเสนอโครงงาน Smart CRM & Data Science Analytics Platform...")

    # =========================================================================
    # SLIDE 2: วัตถุประสงค์โครงงาน (Project Objective) - Single Prominent Sentence + 5 Processes
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_base(s2, "PROJECT OBJECTIVE", "วัตถุประสงค์ของโครงงาน (Project Objective)", 
                   "เป้าหมายหลักของการพัฒนาต้นแบบระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ", 2)

    # Big Central Objective Card
    obj_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.6))
    obj_card.fill.solid()
    obj_card.fill.fore_color.rgb = CARD_BG
    obj_card.line.color.rgb = BORDER_ACTIVE
    obj_card.line.width = Pt(2)
    otf = obj_card.text_frame
    otf.word_wrap = True
    otf.margin_top = Inches(0.4)
    otf.margin_left = Inches(0.6)
    otf.margin_right = Inches(0.6)

    op0 = otf.paragraphs[0]
    op0.alignment = PP_ALIGN.CENTER
    op0.text = "🎯 วัตถุประสงค์หลักของโครงงาน"
    op0.font.name = FONT_FAMILY
    op0.font.size = Pt(14)
    op0.font.bold = True
    op0.font.color.rgb = PRIMARY_BLUE

    op1 = otf.add_paragraph()
    op1.alignment = PP_ALIGN.CENTER
    op1.text = "“เพื่อพัฒนา Web Prototype (Python + Streamlit) จำลองกระบวนการทำงานของระบบ CRM\nครบทั้ง 5 กระบวนการหลัก”"
    op1.font.name = FONT_FAMILY
    op1.font.size = Pt(23)
    op1.font.bold = True
    op1.font.color.rgb = DARK_NAVY
    op1.space_before = Pt(10)

    op2 = otf.add_paragraph()
    op2.alignment = PP_ALIGN.CENTER
    op2.text = "บูรณาการมาตรฐานฐานข้อมูลเชิงสัมพันธ์ 3NF เข้ากับโมเดลการวิเคราะห์ข้อมูลขั้นสูง (Analytics Engine) เพื่อสนับสนุนการตัดสินใจเชิงธุรกิจจริง"
    op2.font.name = FONT_FAMILY
    op2.font.size = Pt(12)
    op2.font.color.rgb = MUTED_SLATE
    op2.space_before = Pt(10)

    # Bottom: 5 Process Flow Cards connecting to DFD
    processes = [
        ("Process 1.0", "งานการตลาด", "Marketing", "บันทึกแคมเปญ & Lead"),
        ("Process 2.0", "งานขาย", "Sales Follow-up", "AI Priority & ใบเสนอราคา"),
        ("Process 3.0", "สั่งซื้อและชำระเงิน", "Order & Billing", "ตรวจสลิป & ออกใบเสร็จ"),
        ("Process 4.0", "บริการลูกค้า & พอร์ทัล", "Support & Portal", "รับแจ้งปัญหา & แชทสด"),
        ("Process 5.0", "รายงาน & วิเคราะห์", "Analytics & Reports", "4 โมเดล AI & แดชบอร์ด")
    ]
    p_w = Inches(2.18)
    p_h = Inches(2.3)
    p_gap = Inches(0.2)
    p_start_x = Inches(0.8)
    p_start_y = Inches(4.55)

    for i, (p_num, p_th, p_en, p_desc) in enumerate(processes):
        px = p_start_x + i * (p_w + p_gap)
        pbox = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, p_start_y, p_w, p_h)
        pbox.fill.solid()
        pbox.fill.fore_color.rgb = CARD_BG
        pbox.line.color.rgb = CARD_BORDER
        pbox.line.width = Pt(1.2)
        ptf = pbox.text_frame
        ptf.word_wrap = True
        ptf.margin_top = Inches(0.2)
        ptf.margin_left = Inches(0.15)
        ptf.margin_right = Inches(0.15)

        pp0 = ptf.paragraphs[0]
        pp0.alignment = PP_ALIGN.CENTER
        pp0.text = p_num
        pp0.font.name = FONT_FAMILY
        pp0.font.size = Pt(11)
        pp0.font.bold = True
        pp0.font.color.rgb = PRIMARY_BLUE

        pp1 = ptf.add_paragraph()
        pp1.alignment = PP_ALIGN.CENTER
        pp1.text = p_th
        pp1.font.name = FONT_FAMILY
        pp1.font.size = Pt(12)
        pp1.font.bold = True
        pp1.font.color.rgb = DARK_NAVY
        pp1.space_before = Pt(4)

        pp2 = ptf.add_paragraph()
        pp2.alignment = PP_ALIGN.CENTER
        pp2.text = p_en
        pp2.font.name = FONT_FAMILY
        pp2.font.size = Pt(9)
        pp2.font.color.rgb = MUTED_SLATE

        pp3 = ptf.add_paragraph()
        pp3.alignment = PP_ALIGN.CENTER
        pp3.text = p_desc
        pp3.font.name = FONT_FAMILY
        pp3.font.size = Pt(9.5)
        pp3.font.color.rgb = DARK_NAVY
        pp3.space_before = Pt(8)

    set_notes(s2, "Speaker Note: วัตถุประสงค์ของเราชัดเจนและตรงประเด็น คือพัฒนา Web Prototype บน Streamlit ให้จำลอง 5 กระบวนการหลักของ CRM ได้ครบถ้วน เชื่อมต่อกับฐานข้อมูลจริง")

    # =========================================================================
    # SLIDE 3: การทำงานของระบบ CRM (How It Works) - Image-Focused with Short Labels
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_base(s3, "CRM OPERATIONAL SYSTEM", "การทำงานของระบบ CRM (How It Works)", 
                   "ระบบปฏิบัติการจริงครอบคลุม 4 บทบาทหลักในการบริหารจัดการความสัมพันธ์ลูกค้า", 3)

    img_grid = [
        (os.path.join(ROOT_DEV, "docs", "evidence", "1_1_campaign_saved.png"), "การตลาด: บันทึกแคมเปญและงบประมาณ"),
        (os.path.join(ROOT_DEV, "docs", "evidence", "2_1_ai_priority.png"), "ฝ่ายขาย: คิว AI จัดลำดับติดตามลูกค้า"),
        (os.path.join(ROOT_DEV, "docs", "evidence", "4_3_rating_given.png"), "บริการลูกค้า: ปิดเคสและรับคะแนนประเมิน"),
        (os.path.join(ROOT_DEV, "docs", "evidence", "portal_home.png"), "พอร์ทัล: ผู้สนใจและลูกค้าใช้งานด้วยตนเอง")
    ]
    grid_coords = [
        (Inches(0.8), Inches(1.55)),
        (Inches(6.8), Inches(1.55)),
        (Inches(0.8), Inches(4.3)),
        (Inches(6.8), Inches(4.3))
    ]
    gw = Inches(5.733)
    gh = Inches(2.45)

    for (ipath, caption), (gx, gy) in zip(img_grid, grid_coords):
        if os.path.exists(ipath):
            s3.shapes.add_picture(ipath, gx, gy, width=gw, height=gh)
        # Caption bar
        cbg = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, gx, gy + gh - Inches(0.35), gw, Inches(0.35))
        cbg.fill.solid()
        cbg.fill.fore_color.rgb = RGBColor(15, 23, 42)
        cbg.line.fill.background()
        cbg.text_frame.text = caption
        cbg.text_frame.paragraphs[0].font.size = Pt(10.5)
        cbg.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        cbg.text_frame.paragraphs[0].font.name = FONT_FAMILY
        cbg.text_frame.paragraphs[0].font.bold = True
        cbg.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    set_notes(s3, "Speaker Note: สถิติข้อมูลจำลองสเกลธุรกิจจริง (seed=42): ผู้สนใจ 600 ราย, ลูกค้า 306 ราย (303 รายมีประวัติซื้อขายสำหรับคำนวณ RFM), ยอดขาย 570 รายการ, Ticket 330 เคส ทุกหน้าจอทำงานเชื่อมต่อกันแบบเรียลไทม์")

    # =========================================================================
    # SLIDE 4: สถาปัตยกรรมระบบ 3 ชั้น (3-Tier System Architecture) - 3 Columns Focus
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_base(s4, "TECHNICAL ARCHITECTURE", "สถาปัตยกรรมระบบ 3 ชั้น (3-Tier System Architecture)", 
                   "การแบ่งแยกหน้าที่อย่างชัดเจนระหว่างชั้นฐานข้อมูล ขุมพลังวิเคราะห์ และส่วนติดต่อผู้ใช้", 4)

    tiers_3 = [
        ("Layer 1: Data Storage Tier\n(ฐานข้อมูลเชิงสัมพันธ์ 3NF)", [
            ("SQLite Relational Database (OLTP):", "จัดเก็บข้อมูลธุรกรรมและทะเบียนประวัติตามมาตรฐาน 3NF ปราศจากข้อมูลซ้ำซ้อน"),
            ("10 ตารางตามแบบจำลองข้อมูล:", "EMPLOYEE, PRODUCT, LEAD, LEAD_ACTIVITY, SALE, SALE_DETAIL, CUSTOMER, TICKET, TICKET_MESSAGE, CAMPAIGN"),
            ("Analytical SQL Views:", "สร้าง Views ล่วงหน้า (V_LEAD, V_CUSTOMER_RFM, V_SERVICE_HEALTH) สกัด Features ทางสถิติ")
        ]),
        ("Layer 2: Analytics Engine Tier\n(ขุมพลังวิเคราะห์และปัญญาประดิษฐ์)", [
            ("Scikit-Learn Machine Learning:", "โมเดล Random Forest Classifier (Lead Scoring) และ K-Means Clustering (RFM)"),
            ("Domain Weighted Algorithm:", "ดัชนีสุขภาพ 5 มิติ (Customer Health Score) พยากรณ์ความเสี่ยงการยกเลิก (Churn)"),
            ("Financial & Statistical Inference:", "คำนวณ ROI, ROAS, CAC, CPL, Funnel 4 ขั้น และ Chi-Square Test (χ²)")
        ]),
        ("Layer 3: Presentation Web Tier\n(ส่วนติดต่อผู้ใช้เว็บแอปพลิเคชัน)", [
            ("Streamlit Web Framework:", "เว็บแอปพลิเคชัน Multi-Page ความเร็วสูง ตอบสนองผู้ใช้แบบเรียลไทม์"),
            ("Role-Based Access Control (RBAC):", "กรองสิทธิ์เมนูและฟังก์ชันแยก 4 บทบาทพนักงาน + Customer Portal"),
            ("Interactive Data Visualization:", "พล็อตแผนภูมิแบบโต้ตอบด้วย Plotly Express (Radar Chart, 3D Scatter, Bar)")
        ])
    ]

    tw = Inches(3.75)
    th = Inches(4.7)
    t_gap = Inches(0.24)
    start_x = Inches(0.8)

    for i, (title, items) in enumerate(tiers_3):
        tx = start_x + i * (tw + t_gap)
        tbox = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, tx, Inches(1.55), tw, th)
        tbox.fill.solid()
        tbox.fill.fore_color.rgb = CARD_BG
        tbox.line.color.rgb = CARD_BORDER
        tbox.line.width = Pt(1.5)
        ttf = tbox.text_frame
        ttf.word_wrap = True
        ttf.margin_top = ttf.margin_left = ttf.margin_right = Inches(0.25)

        tp0 = ttf.paragraphs[0]
        tp0.text = title
        tp0.font.name = FONT_FAMILY
        tp0.font.size = Pt(12)
        tp0.font.bold = True
        tp0.font.color.rgb = PRIMARY_BLUE

        for head, body in items:
            p1 = ttf.add_paragraph()
            p1.text = f"• {head} "
            p1.font.name = FONT_FAMILY
            p1.font.size = Pt(9.5)
            p1.font.bold = True
            p1.font.color.rgb = DARK_NAVY
            p1.space_before = Pt(8)

            p2 = ttf.add_paragraph()
            p2.text = f"  {body}"
            p2.font.name = FONT_FAMILY
            p2.font.size = Pt(9)
            p2.font.color.rgb = MUTED_SLATE

    # Small bottom note about Docker
    dock_note = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.4), Inches(11.733), Inches(0.48))
    dock_note.fill.solid()
    dock_note.fill.fore_color.rgb = CARD_BG
    dock_note.line.color.rgb = BORDER_ACTIVE
    dntf = dock_note.text_frame
    dnp = dntf.paragraphs[0]
    dnp.alignment = PP_ALIGN.CENTER
    dnp.text = "🐳 Cloud Deployment: บรรจุสภาพแวดล้อมทั้งระบบเป็น Container ด้วย Docker & Docker Compose พร้อม Deploy ในคำสั่งเดียว"
    dnp.font.name = FONT_FAMILY
    dnp.font.size = Pt(9.5)
    dnp.font.color.rgb = PRIMARY_BLUE

    set_notes(s4, "Speaker Note: สถาปัตยกรรม 3 ชั้นชัดเจน: Data Tier เก็บข้อมูล 3NF, Analytics Engine รันโมเดล ML, Presentation Tier แสดงผลผ่าน Streamlit")

    # =========================================================================
    # SLIDE 5: DFD Analysis - Large Visual Area
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_base(s5, "DATA FLOW ANALYSIS", "การวิเคราะห์กระแสข้อมูลทั้งระบบ (Data Flow Diagram: DFD)", 
                   "แผนที่พิมพ์เขียวกระแสข้อมูล ผ่านการตรวจสอบ Academic Rules 100% (0 Errors, Balancing สมบูรณ์)", 5)

    dcard = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(3.8), Inches(5.35))
    dcard.fill.solid()
    dcard.fill.fore_color.rgb = CARD_BG
    dcard.line.color.rgb = CARD_BORDER
    dtf = dcard.text_frame
    dtf.word_wrap = True
    dtf.margin_top = dtf.margin_left = dtf.margin_right = Inches(0.25)

    dp0 = dtf.paragraphs[0]
    dp0.text = "📐 พิมพ์เขียวกระแสข้อมูล 3 ระดับ"
    dp0.font.name = FONT_FAMILY
    dp0.font.size = Pt(13)
    dp0.font.bold = True
    dp0.font.color.rgb = PRIMARY_BLUE

    dfd_bullets = [
        ("Context DFD (Process 0):", "ศูนย์กลางเชื่อม 5 External Entities (การตลาด, ผู้สนใจ, ฝ่ายขาย, ลูกค้า, บริการ)"),
        ("Level 0 DFD (5 กระบวนการหลัก):", "Process 1.0 ถึง 5.0 เชื่อมคลังข้อมูล 5 คลัง (D1–D5) ครอบคลุมงานขาย บริการ และวิเคราะห์"),
        ("Level 1 DFD (14 กิจกรรมย่อย):", "จำแนกกิจกรรมย่อยครบถ้วน (รายละเอียดฉบับเต็มเก็บเป็น Backup Slide)"),
        ("ผลการตรวจสอบ Academic Rules:", "✅ 0 Errors / 0 Warnings\n✅ ปราศจาก Black Hole & Miracle\n✅ กฎการ Balancing ข้อมูลเข้า/ออกตรงกัน 100%")
    ]
    for h, b in dfd_bullets:
        p1 = dtf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(8)
        p2 = dtf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE if "Academic" not in h else SEMANTIC_GREEN

    ctx_path = os.path.join(ROOT_DRIVE, "dfd-Context Level DFD.drawio.png")
    l0_path = os.path.join(ROOT_DRIVE, "dfd-Level 0 DFD.drawio.png")

    if os.path.exists(ctx_path):
        s5.shapes.add_picture(ctx_path, Inches(4.8), Inches(1.55), width=Inches(7.7), height=Inches(2.1))
    if os.path.exists(l0_path):
        s5.shapes.add_picture(l0_path, Inches(4.8), Inches(3.85), width=Inches(7.7), height=Inches(3.05))

    set_notes(s5, "Speaker Note: ย้ำว่า DFD ผ่านการประเมินแยกใน Practice I แล้ว สไลด์นี้เน้นยืนยันความสมบูรณ์ 0 errors และ Balancing 100%")

    # =========================================================================
    # SLIDE 6: Peter Chen ERD & 3NF - Large Visual Area
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_base(s6, "CONCEPTUAL & LOGICAL DATABASE DESIGN", "แบบจำลองฐานข้อมูล: Peter Chen ERD และ 3NF", 
                   "โครงสร้างข้อมูลเชิงสัมพันธ์ 10 Entities ปราศจากข้อมูลซ้ำซ้อนตามมาตรฐาน 3NF", 6)

    ecard = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(3.8), Inches(5.35))
    ecard.fill.solid()
    ecard.fill.fore_color.rgb = CARD_BG
    ecard.line.color.rgb = CARD_BORDER
    etf = ecard.text_frame
    etf.word_wrap = True
    etf.margin_top = etf.margin_left = etf.margin_right = Inches(0.25)

    ep0 = etf.paragraphs[0]
    ep0.text = "🏛️ สถาปัตยกรรมข้อมูลเชิงตรรกะ"
    ep0.font.name = FONT_FAMILY
    ep0.font.size = Pt(13)
    ep0.font.bold = True
    ep0.font.color.rgb = PRIMARY_BLUE

    erd_bullets = [
        ("Peter Chen Model (10 Entities):", "จำแนก Strong Entity และ Weak Entity (ขึ้นต่อ Entity อื่น) พร้อมระบุ Cardinality (1:1, 1:N, M:N) ครบถ้วน"),
        ("สัญลักษณ์ตามหลักวิชาการ:", "Primary Key (ขีดเส้นใต้ทึบ) และ Foreign Key (ขีดเส้นใต้ประ) ชัดเจน 100%"),
        ("การปรับบรรทัดฐาน 3NF:", "• 1NF: ค่าเชิงอะตอม (Atomic Values)\n• 2NF: ปราศจาก Partial Dependency\n• 3NF: ปราศจาก Transitive Dependency"),
        ("พจนานุกรมข้อมูล (Data Dictionary):", "ระบุชนิดข้อมูล, ขนาด, และ Constraints รองรับ D1–D5 ครบถ้วน (ตารางเต็มเก็บใน Backup)")
    ]
    for h, b in erd_bullets:
        p1 = etf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(8)
        p2 = etf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE

    erd_path = os.path.join(ROOT_DRIVE, "er-diagram.png")
    if os.path.exists(erd_path):
        s6.shapes.add_picture(erd_path, Inches(4.8), Inches(1.55), width=Inches(7.7), height=Inches(5.35))

    set_notes(s6, "Speaker Note: ชี้ให้เห็นว่าโครงสร้าง 10 ตารางในมาตรฐาน 3NF คือรากฐานที่ทำให้โมเดล AI ในสไลด์ถัดไปคำนวณได้อย่างแม่นยำ ปราศจากข้อมูลซ้ำซ้อน")

    # =========================================================================
    # SLIDE 7: ฟีเจอร์ที่ 1: จัดลำดับความสำคัญผู้สนใจ (Lead Scoring)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_base(s7, "ANALYTICS ENGINE — FEATURE 1", "ฟีเจอร์ที่ 1: จัดลำดับความสำคัญผู้สนใจ (Lead Scoring Model)", 
                   "พยากรณ์โอกาสปิดการขายแบบเรียลไทม์ เพื่อให้ฝ่ายขายโฟกัสกลุ่มที่มีโอกาสซื้อสูงสุด", 7)

    lcard = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(4.6), Inches(5.35))
    lcard.fill.solid()
    lcard.fill.fore_color.rgb = CARD_BG
    lcard.line.color.rgb = CARD_BORDER
    ltf = lcard.text_frame
    ltf.word_wrap = True
    ltf.margin_top = ltf.margin_left = ltf.margin_right = Inches(0.25)

    lp0 = ltf.paragraphs[0]
    lp0.text = "🤖 อัลกอริทึมและข้อมูลนำเข้า (Model & Inputs)"
    lp0.font.name = FONT_FAMILY
    lp0.font.size = Pt(13)
    lp0.font.bold = True
    lp0.font.color.rgb = PRIMARY_BLUE

    ls_items = [
        ("โมเดลหลัก (Primary Model):", "Random Forest Classifier (โมเดล ML รวมพลังต้นไม้ตัดสินใจ 300 ต้น) เทียบกับ Logistic Regression"),
        ("คุณลักษณะนำเข้า (Input Features):", "• จำนวนครั้งการติดตาม (Follow-up Count)\n• ช่องทางที่มา (Channel: Web, Referral, Direct)\n• ส่วนลดแคมเปญโปรโมชัน (Campaign Discount %)\n• ความเร็วตอบกลับครั้งแรก (First Contact Speed)"),
        ("เกณฑ์การตัดสินใจ (Decision Thresholds):", "• 🔥 Hot (โอกาสซื้อ ≥ 70%): โทรติดตามทันทีใน 1 ชม.\n• 🌤 Warm (โอกาสซื้อ 40–69%): ส่งข้อมูลเพิ่มเติมทางอีเมล\n• ❄️ Cold (โอกาสซื้อ < 40%): บ่มเพาะด้วยแคมเปญการตลาด"),
        ("ตัวอย่างจริงจากระบบ (Seed Data):", "Lead รหัส 'LD0264' ช่องทาง Direct ติดตาม 4 ครั้ง ได้แคมเปญลด 15% ➔ โมเดลคำนวณได้ 82.4% จัดอยู่ในกลุ่ม Hot พร้อมแนะนำเซลล์ปิดการขาย")
    ]
    for h, b in ls_items:
        p1 = ltf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(6)
        p2 = ltf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE if "ตัวอย่างจริง" not in h else PRIMARY_BLUE

    ls_img_path = os.path.join(ROOT_DEV, "docs", "evidence", "6_1_lead_scoring.png")
    if os.path.exists(ls_img_path):
        s7.shapes.add_picture(ls_img_path, Inches(5.6), Inches(1.55), width=Inches(6.9), height=Inches(5.35))

    set_notes(s7, "Speaker Note: Random Forest ใช้ต้นไม้ 300 ต้นทำนายความน่าจะเป็น หากเกิน 70% ระบบจะจัดเข้าคิว Hot Priority ทันที")

    # =========================================================================
    # SLIDE 8: ฟีเจอร์ที่ 2: จัดกลุ่มลูกค้าตามพฤติกรรม (RFM)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_base(s8, "ANALYTICS ENGINE — FEATURE 2", "ฟีเจอร์ที่ 2: จัดกลุ่มลูกค้าตามพฤติกรรม (RFM Segmentation)", 
                   "วิเคราะห์พฤติกรรมซื้อด้วย Quintile Scoring ร่วมกับ K-Means Clustering แบ่ง 6 กลุ่มยุทธศาสตร์", 8)

    rcard = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(4.6), Inches(5.35))
    rcard.fill.solid()
    rcard.fill.fore_color.rgb = CARD_BG
    rcard.line.color.rgb = CARD_BORDER
    rtf = rcard.text_frame
    rtf.word_wrap = True
    rtf.margin_top = rtf.margin_left = rtf.margin_right = Inches(0.25)

    rp0 = rtf.paragraphs[0]
    rp0.text = "📊 มิติการวิเคราะห์และโมเดล K-Means"
    rp0.font.name = FONT_FAMILY
    rp0.font.size = Pt(13)
    rp0.font.bold = True
    rp0.font.color.rgb = PRIMARY_BLUE

    rfm_items = [
        ("3 มิติพฤติกรรมลูกค้า (RFM Dimensions):", "• Recency (R): วันที่ผ่านมาจากการซื้อล่าสุด\n• Frequency (F): จำนวนครั้งที่เคยซื้อทั้งหมด\n• Monetary (M): ยอดเงินสะสมที่ลูกค้าจ่ายจริง"),
        ("เทคนิคโมเดล (Techniques):", "Quintile Scoring (ตัดแบ่ง 5 ระดับ) + K-Means Clustering (การจัดกลุ่มด้วยระยะห่างทางสถิติ k=4) ยืนยันด้วยค่า Silhouette Score"),
        ("6 กลุ่มยุทธศาสตร์ (Strategic Segments):", "1. Champions: ซื้อบ่อย ยอดสูง ล่าสุดเพิ่งซื้อ\n2. Loyal: ลูกค้าประจำสม่ำเสมอ\n3. Potential: ลูกค้าใหม่ศักยภาพสูง\n4. New: เพิ่งซื้อครั้งแรก\n5. At Risk: ขาดการซื้อไปนาน ยอดเคยสูง\n6. Lost: หายไปนานมาก"),
        ("ตัวอย่างจริงจากระบบ (303 รายที่มีประวัติซื้อ):", "ลูกค้า 'CU0175' ยอดซื้อสะสม 940,500 บาท ซื้อ 5 ครั้ง ล่าสุด 15 วันก่อน ➔ จัดเป็นกลุ่ม 'Champions' สิทธิ์ดูแลพิเศษ")
    ]
    for h, b in rfm_items:
        p1 = rtf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(6)
        p2 = rtf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE if "ตัวอย่างจริง" not in h else PRIMARY_BLUE

    rfm_img_path = os.path.join(ROOT_DEV, "docs", "evidence", "6_2_rfm.png")
    if os.path.exists(rfm_img_path):
        s8.shapes.add_picture(rfm_img_path, Inches(5.6), Inches(1.55), width=Inches(6.9), height=Inches(5.35))

    set_notes(s8, "Speaker Note: ลูกค้า 303 รายจาก 306 รายถูกนำมาคำนวณ RFM เพราะมีประวัติซื้อขายสมบูรณ์ ลูกค้า Champions เช่น CU0175 สร้างยอดเกือบล้าน")

    # =========================================================================
    # SLIDE 9: ฟีเจอร์ที่ 3: ดัชนีสุขภาพและความเสี่ยงลูกค้า (Churn & Health)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_base(s9, "ANALYTICS ENGINE — FEATURE 3", "ฟีเจอร์ที่ 3: ดัชนีสุขภาพและความเสี่ยงการยกเลิก (Churn & Health Score)", 
                   "ดัชนีเตือนภัยล่วงหน้า 5 มิติ ผสานข้อมูลการซื้อและบริการเพื่อตรวจจับความเสี่ยงลูกค้าหายไป", 9)

    hcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(4.6), Inches(5.35))
    hcard.fill.solid()
    hcard.fill.fore_color.rgb = CARD_BG
    hcard.line.color.rgb = CARD_BORDER
    htf = hcard.text_frame
    htf.word_wrap = True
    htf.margin_top = htf.margin_left = htf.margin_right = Inches(0.25)

    hp0 = htf.paragraphs[0]
    hp0.text = "🩺 สูตรค่าน้ำหนัก 5 มิติ & ระดับความเสี่ยง"
    hp0.font.name = FONT_FAMILY
    hp0.font.size = Pt(13)
    hp0.font.bold = True
    hp0.font.color.rgb = PRIMARY_BLUE

    ch_items = [
        ("สูตรคำนวณ Health Score (0–100):", "Health Score =\n  35% Recency Score (ความสดใหม่ของการซื้อ)\n+ 20% Frequency Score (ความถี่การซื้อ)\n+ 15% Monetary Score (มูลค่าเงินสะสม)\n+ 20% Service Score (ความพึงพอใจการบริการ)\n+ 10% Resolution Speed (ความเร็วแก้ไขเคส)"),
        ("การจัดกลุ่มสุขภาพ (Health Tiers):", "• 🟢 แข็งแรง (> 65 คะแนน): ความสัมพันธ์ดีเยี่ยม\n• 🟡 เฝ้าระวัง (41–65 คะแนน): เริ่มมีสัญญาณชะลอตัว\n• 🔴 เสี่ยงสูง (≤ 40 คะแนน): เสี่ยงต่อการ Churn สูงมาก"),
        ("การยืนยันความแม่นยำ (Validation):", "ใช้ Logistic Regression ตรวจสอบกับ Silent Churn (ลูกค้าที่ไม่มีการซื้อเกิน 180 วัน) ได้ความแม่นยำสูง"),
        ("ตัวอย่างจริงจากระบบ (Seed Data):", "ลูกค้า 'CU0178' ไม่ซื้อซ้ำมานาน 548 วัน มี Ticket ค้าง 2 เคส ➔ คะแนนหล่นเหลือ 32.5 / 100 (กลุ่มเสี่ยงสูง) ระบบแจ้งเตือนทีม CS กอบกู้ทันที")
    ]
    for h, b in ch_items:
        p1 = htf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(6)
        p2 = htf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE if "ตัวอย่างจริง" not in h else SEMANTIC_RED

    ch_img_path = os.path.join(ROOT_DEV, "docs", "evidence", "6_3_churn.png")
    if os.path.exists(ch_img_path):
        s9.shapes.add_picture(ch_img_path, Inches(5.6), Inches(1.55), width=Inches(6.9), height=Inches(5.35))

    set_notes(s9, "Speaker Note: Health Score ผสานทั้งฝ่ายขายและบริการ หากลูกค้าเจอปัญหาบ่อยและไม่ซื้อซ้ำ คะแนนจะตกลงมาอยู่ในโซนแดง เช่น CU0178 (32.5 คะแนน)")

    # =========================================================================
    # SLIDE 10: ฟีเจอร์ที่ 4: ประสิทธิภาพทางการเงินของแคมเปญ (Campaign ROI)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_base(s10, "ANALYTICS ENGINE — FEATURE 4", "ฟีเจอร์ที่ 4: ประสิทธิภาพทางการเงินของแคมเปญ (Campaign Financial ROI)", 
                   "วัดความคุ้มค่าทางการเงินจริง (ROI, ROAS, CAC) พร้อม Chi-Square Test ทดสอบนัยสำคัญ", 10)

    rocard = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(4.6), Inches(5.35))
    rocard.fill.solid()
    rocard.fill.fore_color.rgb = CARD_BG
    rocard.line.color.rgb = CARD_BORDER
    rotf = rocard.text_frame
    rotf.word_wrap = True
    rotf.margin_top = rotf.margin_left = rotf.margin_right = Inches(0.25)

    rp0 = rotf.paragraphs[0]
    rp0.text = "💰 สูตรการเงินและสถิติอ้างอิง"
    rp0.font.name = FONT_FAMILY
    rp0.font.size = Pt(13)
    rp0.font.bold = True
    rp0.font.color.rgb = PRIMARY_BLUE

    roi_items = [
        ("ตัวชี้วัดทางการเงิน (Financial Formulas):", "• ROI: [(รายได้สุทธิ - งบประมาณ) / งบประมาณ] × 100%\n• ROAS: ผลตอบแทนจากค่าโฆษณา (ยอดขาย / งบ)\n• CAC: ต้นทุนการได้ลูกค้าใหม่ 1 ราย (งบ / ลูกค้าใหม่)\n• CPL: ต้นทุนต่อผู้สนใจ 1 ราย (งบ / จำนวน Lead)"),
        ("การทดสอบสมมติฐานทางสถิติ (Chi-Square):", "ใช้ Chi-Square Test (χ²) พิสูจน์นัยสำคัญทางสถิติ (p-value < 0.05) ว่าอัตราการปิดการขายสัมพันธ์กับช่องทางแคมเปญจริง ไม่ใช่เรื่องบังเอิญ"),
        ("เกณฑ์ประเมินแคมเปญ (Benchmarks):", "• ✅ คุ้มค่ามาก (ROI > 100%): ขยายงบประมาณต่อ\n• ⚠️ พอไปได้ (ROI 0–100%): ปรับปรุง Funnel ให้ดีขึ้น\n• ❌ ขาดทุน (ROI < 0%): ตัดงบหรือเปลี่ยนกลุ่มเป้าหมาย"),
        ("ตัวอย่างจริงจากระบบ (Seed Data):", "แคมเปญ 'Digital Ads Q3' งบ 80,000 บาท สร้าง Lead 108 ราย ปิดการขายได้ 40 ราย ยอดขายรวม 8.35 ล้านบาท ➔ ROI 103% (คุ้มค่ามาก)")
    ]
    for h, b in roi_items:
        p1 = rotf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(6)
        p2 = rotf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9)
        p2.font.color.rgb = MUTED_SLATE if "ตัวอย่างจริง" not in h else SEMANTIC_GREEN

    roi_img_path = os.path.join(ROOT_DEV, "docs", "evidence", "5_1_6_4_campaign_roi.png")
    if os.path.exists(roi_img_path):
        s10.shapes.add_picture(roi_img_path, Inches(5.6), Inches(1.55), width=Inches(6.9), height=Inches(5.35))

    set_notes(s10, "Speaker Note: แคมเปญ Digital Ads Q3 ลงทุน 8 หมื่น ได้ยอด 8.35 ล้านบาท ให้ผลตอบแทน ROI เกิน 100% ระบบช่วยให้ผู้บริหารตัดสินใจขยายงบได้อย่างมั่นใจ")

    # =========================================================================
    # SLIDE 11: สิทธิ์การเข้าถึงตามบทบาท (RBAC) - Section 8.3 Report-Style Table
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_base(s11, "APPLICATION SECURITY & GOVERNANCE", "สิทธิ์การเข้าถึงตามบทบาท (Role-Based Access Control: RBAC)", 
                   "การแบ่งแยกหน้าที่ตามตำแหน่งงานเพื่อความปลอดภัยและความเป็นส่วนตัวของข้อมูล", 11)

    # Report-Style Table (Section 8.3)
    rows = 6
    cols = 3
    left = Inches(0.8)
    top = Inches(1.6)
    width = Inches(11.733)
    height = Inches(4.3)

    table_shape = s11.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(2.5)   # บทบาท (Role)
    table.columns[1].width = Inches(5.2)   # สิ่งที่เข้าถึงได้
    table.columns[2].width = Inches(4.033) # เมนูที่เห็น

    table_data = [
        ("บทบาท (Role)", "สิ่งที่เข้าถึงได้ (Access Scope)", "เมนูที่เห็นในระบบ (Visible Menus)"),
        ("ผู้ดูแลระบบ (Admin)", "ทุกอย่าง 100% ทุกหน้าที่ + จัดการทะเบียนพนักงานและสิทธิ์", "ทุกเมนู (Dashboard, การตลาด, งานขาย, บัญชี, บริการ, ตั้งค่า)"),
        ("ฝ่ายการตลาด (Marketing)", "สร้าง/ดูแคมเปญ, บันทึกผู้สนใจ (Lead), ดู ROI แคมเปญ (ไม่เห็นข้อมูลการเงิน)", "การตลาด (สร้างแคมเปญ/บันทึก Lead), แดชบอร์ดวิเคราะห์ ROI"),
        ("ฝ่ายขาย (Sales)", "คิวติดตามผู้สนใจ (AI Priority), บันทึกกิจกรรม, ออกใบเสนอราคา, ตรวจสลิป, ออกใบเสร็จ", "ติดตามการขาย, สั่งซื้อและใบเสร็จ (ไม่เห็นเมนูการตลาด)"),
        ("บริการลูกค้า (Support)", "รับ/ปิด Ticket ปัญหา, แชทสดกับลูกค้า, ดูประวัติบริการ (ไม่เห็นยอดขาย)", "รับแจ้งปัญหาและบริการลูกค้า, ทะเบียนประวัติลูกค้า"),
        ("พอร์ทัลลูกค้า (Guest)", "เฉพาะฟังก์ชันของตนเอง: ลงทะเบียน, ตรวจใบเสนอราคา, สั่งซื้อ, แนบสลิป, แจ้งปัญหา, ให้คะแนน", "หน้า Customer Portal เท่านั้น (ไม่เห็นเมนูภายในองค์กร)")
    ]

    for r_idx, row_content in enumerate(table_data):
        for c_idx, cell_text in enumerate(row_content):
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_text
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_FAMILY
            if r_idx == 0:
                p.font.size = Pt(11)
                p.font.bold = True
                p.font.color.rgb = RGBColor(255, 255, 255)
                cell.fill.solid()
                cell.fill.fore_color.rgb = PRIMARY_BLUE
            else:
                p.font.size = Pt(10)
                p.font.color.rgb = DARK_NAVY
                cell.fill.solid()
                cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else RGBColor(241, 245, 249)
                if c_idx == 0:
                    p.font.bold = True

    # Note below table
    rb_note = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.65))
    rb_note.fill.solid()
    rb_note.fill.fore_color.rgb = CARD_BG
    rb_note.line.color.rgb = BORDER_ACTIVE
    rbtf = rb_note.text_frame
    rbp = rbtf.paragraphs[0]
    rbp.text = "⚡ หมายเหตุ: ระบบกรองสิทธิ์ระดับ Sidebar เมนูและสิทธิ์จัดการข้อมูลโดยอัตโนมัติ ซึ่งจะสาธิตการทำงานจริงให้ชมในช่วง Live Demo 10 นาที"
    rbp.font.name = FONT_FAMILY
    rbp.font.size = Pt(10)
    rbp.font.bold = True
    rbp.font.color.rgb = PRIMARY_BLUE

    set_notes(s11, "Speaker Note: สไลด์นี้นำเสนอด้วยตารางแบบรายงานตามแบบฟอร์ม แสดงการแบ่งแยกหน้าที่ 4 Role พนักงาน + Customer Portal อย่างชัดเจน")

    # =========================================================================
    # SLIDE 12: การทดสอบระบบ (System Verification & Testing) - Concise, refers to plan_4
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_base(s12, "QUALITY ASSURANCE & TESTING", "การทดสอบระบบ (System Verification & Testing)", 
                   "การทดสอบซอฟต์แวร์เพื่อรับประกันความถูกต้องแม่นยำและการทำงานที่เชื่อถือได้", 12)

    card12_w = Inches(5.7)
    card12_h = Inches(5.2)

    # Left: Automated Testing Card
    acard = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), card12_w, card12_h)
    acard.fill.solid()
    acard.fill.fore_color.rgb = CARD_BG
    acard.line.color.rgb = CARD_BORDER
    acard.line.width = Pt(1.5)
    atf = acard.text_frame
    atf.word_wrap = True
    atf.margin_top = atf.margin_left = atf.margin_right = Inches(0.3)

    ap0 = atf.paragraphs[0]
    ap0.text = "⚙️ การทดสอบซอฟต์แวร์อัตโนมัติ (Automated Testing)"
    ap0.font.name = FONT_FAMILY
    ap0.font.size = Pt(13)
    ap0.font.bold = True
    ap0.font.color.rgb = PRIMARY_BLUE

    auto_items = [
        ("เป้าหมายหลัก:", "ทดสอบเพื่อพัฒนาซอฟต์แวร์ให้ถูกต้องตามกระแสข้อมูล DFD ครบทุกขั้นตอน"),
        ("pytest DFD Flow Suite:", "ชุดทดสอบครอบคลุม 14 กิจกรรมย่อยตาม DFD Process 1.0 ถึง 5.0 (36 Test Cases ผ่าน 100%)"),
        ("End-to-End Verification:", "ทดสอบผ่านเบราว์เซอร์จริงด้วย Playwright ตรวจสอบผลลัพธ์หน้าจอ UI ครบทุกโมดูล"),
        ("อ้างอิงรายละเอียดฉบับเต็ม:", "แผนการทดสอบและผลลัพธ์ทั้งหมดบันทึกไว้ในเอกสาร plan_4_source_code_prototype.md")
    ]
    for h, b in auto_items:
        p1 = atf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(10)
        p2 = atf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = MUTED_SLATE

    # Right: Manual QA & Real Bug Resolution Card
    mcard = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), card12_w, card12_h)
    mcard.fill.solid()
    mcard.fill.fore_color.rgb = CARD_BG
    mcard.line.color.rgb = CARD_BORDER
    mcard.line.width = Pt(1.5)
    mtf = mcard.text_frame
    mtf.word_wrap = True
    mtf.margin_top = mtf.margin_left = mtf.margin_right = Inches(0.3)

    mp0 = mtf.paragraphs[0]
    mp0.text = "🔍 การตรวจรับด้วยข้อมูลจริงและการแก้บั๊ก (Manual QA)"
    mp0.font.name = FONT_FAMILY
    mp0.font.size = Pt(13)
    mp0.font.bold = True
    mp0.font.color.rgb = PRIMARY_BLUE

    qa_items = [
        ("การตรวจรับด้วยภาพจริง 34 ภาพ:", "บันทึกผลการใช้งานจริงครบ 14 กิจกรรมย่อย (27 ภาพหน้าจอ UI + 7 ภาพ DFD)"),
        ("บั๊กที่ 1 (✅ แก้ไขแล้ว):", "หน้าการตลาดแครชจาก pd.NA เมื่อบางแคมเปญไม่มี Lead — แก้ไขด้วย np.where และ COALESCE เรียบร้อย"),
        ("บั๊กที่ 2 (🔴 ระบุจุดรอปรับ):", "View V_SERVICE_HEALTH นับ Critical Ticket เบิ้ลจาก Fan-out Join — ระบุวิธีแก้ด้วย Subquery ชัดเจน"),
        ("สะท้อนการทำงานจริง:", "แสดงถึงการลงมือปฏิบัติจริง ค้นพบปัญหาจริง และเข้าใจการทำงานของระบบอย่างลึกซึ้ง")
    ]
    for h, b in qa_items:
        p1 = mtf.add_paragraph()
        p1.text = f"• {h} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(10)
        p2 = mtf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = MUTED_SLATE

    set_notes(s12, "Speaker Note: สรุปสั้นๆ ว่าเราทดสอบเพื่อให้ซอฟต์แวร์ทำงานได้ถูกต้อง รายละเอียดเต็มดูใน plan_4 ได้")

    # =========================================================================
    # SLIDE 13: บทสรุป (Project Conclusion) - DFD/ERD as Foundational Data Model
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_base(s13, "PROJECT CONCLUSION", "บทสรุปของโครงงาน (Project Conclusion)", 
                   "การผสานการออกแบบฐานข้อมูลเชิงสัมพันธ์สู่การพัฒนาซอฟต์แวร์ที่ใช้งานได้จริง", 13)

    ccard = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    ccard.fill.solid()
    ccard.fill.fore_color.rgb = CARD_BG
    ccard.line.color.rgb = BORDER_ACTIVE
    ccard.line.width = Pt(1.5)
    ctf = ccard.text_frame
    ctf.word_wrap = True
    ctf.margin_top = Inches(0.4)
    ctf.margin_left = Inches(0.5)
    ctf.margin_right = Inches(0.5)

    cp0 = ctf.paragraphs[0]
    cp0.text = "🎯 คุณค่าและความสำเร็จที่ได้รับจากโครงงาน"
    cp0.font.name = FONT_FAMILY
    cp0.font.size = Pt(15)
    cp0.font.bold = True
    cp0.font.color.rgb = PRIMARY_BLUE

    concl_points = [
        ("DFD และ ERD คือ Data Model พื้นฐานที่ทำให้สร้างซอฟต์แวร์ได้จริง:", 
         "แผนภาพกระแสข้อมูล (DFD) และแบบจำลองข้อมูล (Peter Chen ERD) ที่ออกแบบไว้ ไม่ใช่เพียงแบบฝึกหัดบนกระดาษ แต่คือพิมพ์เขียวและรากฐานข้อมูลที่สำคัญที่สุด ที่ทำให้สามารถต่อยอดพัฒนาเป็น Web Application Prototype ที่ทำงานได้จริงอย่างสมบูรณ์แบบ"),
        
        ("มาตรฐานฐานข้อมูล 3NF คือหัวใจของ AI และ Analytics ที่แม่นยำ:", 
         "การออกแบบฐานข้อมูลเชิงสัมพันธ์ที่ถูกต้องตามมาตรฐาน 3NF ปราศจากข้อมูลซ้ำซ้อน มี Data Integrity สูง ทำให้โมเดล Data Science ทั้ง 4 ตัวสามารถดึงข้อมูลผ่าน SQL Views ไปประมวลผลได้อย่างรวดเร็ว แม่นยำ และตอบสนองต่อผู้บริหารได้ทันที"),
        
        ("บรรลุวัตถุประสงค์ในการสร้าง Web Prototype ที่ใช้งานได้จริง:", 
         "ระบบสามารถจำลองกระบวนการทำงาน CRM ครบทั้ง 5 กระบวนการหลัก เชื่อมต่อ 4 บทบาทการทำงานและพอร์ทัลลูกค้า พร้อมรองรับการต่อยอดใช้งานจริงในองค์กรธุรกิจต่อไป")
    ]

    for title, desc in concl_points:
        p1 = ctf.add_paragraph()
        p1.text = f"✔ {title} "
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(16)

        p2 = ctf.add_paragraph()
        p2.text = f"  {desc}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = MUTED_SLATE
        p2.space_before = Pt(4)

    set_notes(s13, "Speaker Note: สรุปเชื่อมโยงว่า DFD และ ERD ที่ออกแบบไว้คือ Data Model ที่ทำให้เกิด Web Prototype ที่ใช้งานได้จริงวันนี้")

    # =========================================================================
    # SLIDE 14: ถาม–ตอบ (Q&A) & ส่งไม้ต่อ Live Demo
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_slide_base(s14, "QUESTIONS & ANSWERS", "ช่วงถาม–ตอบ (Q&A) & การส่งต่อสู่การสาธิตระบบจริง", 
                   "ขอขอบพระคุณอาจารย์ผู้สอนและเพื่อนๆ ทุกท่าน — พร้อมตอบทุกข้อสงสัยและนำชมระบบจริง", 14)

    # Top Thank you banner
    ty_card = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(11.733), Inches(1.3))
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = CARD_BG
    ty_card.line.color.rgb = CARD_BORDER
    ty_tf = ty_card.text_frame
    ty_tf.word_wrap = True
    ty_tf.margin_top = Inches(0.2)
    ty_tf.margin_left = Inches(0.3)
    ty_tf.margin_right = Inches(0.3)

    typ0 = ty_tf.paragraphs[0]
    typ0.alignment = PP_ALIGN.CENTER
    typ0.text = "🙏 ขอขอบพระคุณทุกท่านเป็นอย่างสูง"
    typ0.font.name = FONT_FAMILY
    typ0.font.size = Pt(18)
    typ0.font.bold = True
    typ0.font.color.rgb = PRIMARY_BLUE

    typ1 = ty_tf.add_paragraph()
    typ1.alignment = PP_ALIGN.CENTER
    typ1.text = "เปิดรับทุกข้อคิดเห็น คำแนะนำ และคำถามจากอาจารย์และเพื่อนๆ ทุกท่านครับ/ค่ะ"
    typ1.font.name = FONT_FAMILY
    typ1.font.size = Pt(11.5)
    typ1.font.color.rgb = MUTED_SLATE
    typ1.space_before = Pt(4)

    # Center Hand-off Banner
    demo_banner = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.1), Inches(11.733), Inches(2.2))
    demo_banner.fill.solid()
    demo_banner.fill.fore_color.rgb = RGBColor(239, 246, 255)
    demo_banner.line.color.rgb = PRIMARY_BLUE
    demo_banner.line.width = Pt(2)
    dtf = demo_banner.text_frame
    dtf.word_wrap = True
    dtf.margin_top = Inches(0.25)
    dtf.margin_left = Inches(0.4)
    dtf.margin_right = Inches(0.4)

    dp0 = dtf.paragraphs[0]
    dp0.alignment = PP_ALIGN.CENTER
    dp0.text = "🚀 ลำดับถัดไป: สาธิตการทำงานของระบบจริง (Live Interactive Demo 10 นาที)"
    dp0.font.name = FONT_FAMILY
    dp0.font.size = Pt(18)
    dp0.font.bold = True
    dp0.font.color.rgb = PRIMARY_BLUE

    dp1 = dtf.add_paragraph()
    dp1.alignment = PP_ALIGN.CENTER
    dp1.text = "จะพาทุกท่านเดินทางผ่านกระแสข้อมูลจริงทั้ง 7 ขั้นตอน (ตาม plan_5_demo.md)\nตั้งแต่การตลาดสร้างแคมเปญ ➔ พอร์ทัลรับ Lead ➔ งานขายออกใบเสนอราคาและใบเสร็จ ➔ เปิดเคสบริการและแชทสด ➔ รายงานผลการคำนวณ 4 โมเดล Data Science"
    dp1.font.name = FONT_FAMILY
    dp1.font.size = Pt(11.5)
    dp1.font.color.rgb = DARK_NAVY
    dp1.space_before = Pt(8)

    # Bottom Repo Info Box
    bot_info = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.55), Inches(11.733), Inches(1.35))
    bot_info.fill.solid()
    bot_info.fill.fore_color.rgb = CARD_BG
    bot_info.line.color.rgb = CARD_BORDER
    itf = bot_info.text_frame
    itf.word_wrap = True
    itf.margin_top = Inches(0.18)
    itf.margin_left = Inches(0.3)
    itf.margin_right = Inches(0.3)

    ip0 = itf.paragraphs[0]
    ip0.alignment = PP_ALIGN.CENTER
    ip0.text = "📂 คลังซอร์สโค้ดและเอกสารโครงงานฉบับสมบูรณ์"
    ip0.font.name = FONT_FAMILY
    ip0.font.size = Pt(12)
    ip0.font.bold = True
    ip0.font.color.rgb = PRIMARY_BLUE

    ip1 = itf.add_paragraph()
    ip1.alignment = PP_ALIGN.CENTER
    ip1.text = "• Source Code: GitHub Repository  |  • เอกสารรายงาน: บทที่ 1 ถึง บทที่ 4  |  • คู่มือการใช้งาน: User Manual (14 กิจกรรม)\nพร้อมชุดทดสอบอัตโนมัติ pytest และ Dockerfile / docker-compose.yml พร้อมรันได้ทันที"
    ip1.font.name = FONT_FAMILY
    ip1.font.size = Pt(10)
    ip1.font.color.rgb = MUTED_SLATE
    ip1.space_before = Pt(3)

    set_notes(s14, "ส่งไม้ต่อเข้าสู่ช่วง Live Demo 10 นาที (โหมด Solo Presenter: ผู้สาธิตคนเดียวเปิดระบบ พูดไปคลิกตามไกด์ใน Slide 15-17)")

    # =========================================================================
    # SLIDE 15: เตรียมพร้อมสาธิตระบบสด & Cheat Sheet (Quick Start & Demo Setup)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_slide_base(s15, "LIVE DEMO SETUP", "การเตรียมพร้อมสาธิตระบบสด (Live Demo Quick Start)", 
                   "คำสั่งเปิดระบบ โหมดผู้สาธิตคนเดียว (Solo Demo) และคลังรหัสข้อมูลจำลอง (Cheat Sheet)", 15)

    card15_h = Inches(5.4)
    # Left Card: Quick Start Commands
    c15_left = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.7), card15_h)
    c15_left.fill.solid()
    c15_left.fill.fore_color.rgb = CARD_BG
    c15_left.line.color.rgb = CARD_BORDER
    c15_left.line.width = Pt(1.5)
    ltf15 = c15_left.text_frame
    ltf15.word_wrap = True
    ltf15.margin_top = ltf15.margin_left = ltf15.margin_right = Inches(0.3)

    lp0 = ltf15.paragraphs[0]
    lp0.text = "🚀 คำสั่งเปิดระบบเริ่มซ้อมทันที (Quick Start)"
    lp0.font.name = FONT_FAMILY
    lp0.font.size = Pt(13)
    lp0.font.bold = True
    lp0.font.color.rgb = PRIMARY_BLUE

    qs_items = [
        ("1. คืนค่าฐานข้อมูลเริ่มต้น (เลือกวิธีใดวิธีหนึ่ง):",
         "• วิธี ก (Terminal): python db/seed_data.py\n• วิธี ข (บนหน้าเว็บ): กดปุ่ม '🔄 รีเซ็ตฐานข้อมูล Demo' ที่หน้า Login หรือ Sidebar"),
        ("2. รันแอปพลิเคชันระบบต้นแบบ (Streamlit):",
         "• streamlit run app.py\n• เข้าใช้งานผ่านเบราว์เซอร์ที่: http://localhost:8501"),
        ("3. เทคนิค Solo Demo (คนเดียวพูดไปคลิกไป):",
         "• หน้าต่างปกติ (ซ้าย): Staff CRM (admin1, marketing1, sale1, cs1)\n• หน้าต่าง Incognito (ขวา): Customer Portal (guest)\n• สลับหน้าจอซ้าย-ขวาได้ทันที ไม่ต้องล็อกเอาท์เข้าออกซ้ำซ้อน"),
        ("4. แผนสำรองฉุกเฉิน:",
         "• หากระบบค้าง ให้สลับไปเปิดคลิปสำรอง docs/Precision_AI_CRM_Demo_Backup.mp4")
    ]
    for h, b in qs_items:
        p1 = ltf15.add_paragraph()
        p1.text = f"• {h}"
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(8)
        p2 = ltf15.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.2)
        p2.font.color.rgb = MUTED_SLATE

    # Right Card: Seed Data Cheat Sheet
    c15_right = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.55), Inches(5.733), card15_h)
    c15_right.fill.solid()
    c15_right.fill.fore_color.rgb = CARD_BG
    c15_right.line.color.rgb = CARD_BORDER
    c15_right.line.width = Pt(1.5)
    rtf15 = c15_right.text_frame
    rtf15.word_wrap = True
    rtf15.margin_top = rtf15.margin_left = rtf15.margin_right = Inches(0.3)

    rp0 = rtf15.paragraphs[0]
    rp0.text = "📋 Cheat Sheet รหัสข้อมูลจำลอง (ใช้ตามนี้ได้เลย)"
    rp0.font.name = FONT_FAMILY
    rp0.font.size = Pt(13)
    rp0.font.bold = True
    rp0.font.color.rgb = PRIMARY_BLUE

    cs_items = [
        ("Lead AI Hot (85%): รหัส 'LD0264' (นายวิชัย ทองดี)",
         "ใช้ใน: Step 3 (งานขาย) — โอกาสปิดการขายสูง ดึงดูดจากแคมเปญ มีประวัติติดตาม 4 ครั้ง"),
        ("แคมเปญ ROI สูงสุด 103%: รหัส 'CMP003' (Digital Ads Q3)",
         "ใช้ใน: Step 2 (การตลาด) & Dashboard — งบ 80k รายได้ 8.35 ล้านบาท ปิด 40 ราย"),
        ("ลูกค้ากลุ่ม Churn Risk: รหัส 'CU0178' (ร้านสมหญิง การค้า)",
         "ใช้ใน: Step 6 & 7 — ไม่ซื้อซ้ำมา 548 วัน มีเคสปัญหาค้างอยู่ 2 เคส จัดเป็น At Risk"),
        ("ลูกค้ากลุ่ม Champions: รหัส 'CU0175'",
         "ใช้ใน: Step 7 (RFM) — ซื้อ 5 ครั้ง ยอดรวม 940,500 บาท ล่าสุดเมื่อ 15 วันก่อน"),
        ("Ticket ปิดเคส 5 ดาว: รหัส 'TK0008' (ลูกค้า CU0008)",
         "ใช้ใน: Step 6 (Support) — เคสปิดสำเร็จ มีคะแนนประเมินความพึงพอใจ 5 ดาวเต็ม")
    ]
    for h, b in cs_items:
        p1 = rtf15.add_paragraph()
        p1.text = f"✔ {h}"
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(8)
        p2 = rtf15.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.2)
        p2.font.color.rgb = MUTED_SLATE

    set_notes(s15, "Speaker Note: สไลด์นี้สำหรับให้ผู้สาธิตคนเดียวเปิดเตรียมพร้อม วางคำสั่งเปิดระบบและ Cheat Sheet ข้อมูลตัวอย่างไว้ข้างคีย์บอร์ด")

    # =========================================================================
    # SLIDE 16: สคริปต์สาธิตสด ขั้นตอนที่ 1 – 3 (Flow ลูกค้า, การตลาด & งานขาย AI)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_slide_base(s16, "DEMO RUN-SHEET: PART 1", "สคริปต์สาธิตสด ขั้นตอนที่ 1 – 3 (Flow ลูกค้า, การตลาด & งานขาย AI)", 
                   "คู่มือสำหรับผู้สาธิตคนเดียว: พูดไปคลิกตาม กรอกข้อมูลตามตารางนี้ (00:00 – 04:30)", 16)

    card16_w = Inches(3.7)
    card16_h = Inches(5.4)

    col16_defs = [
        ("1️⃣ Step 1: [Portal] รับ Lead ใหม่",
         "⏱️ เวลา: 00:00 – 01:00 (~1 นาที)",
         "pages/9_portal.py (ปุ่ม Guest)",
         "แท็บ ① 'ลงทะเบียนขอรับข้อมูล'",
         [
             ("กรอกชื่อ:", "คุณสมชาย หมายมั่น"),
             ("เบอร์โทร:", "081-999-8888"),
             ("ช่องทาง:", "Facebook Ads"),
             ("กดปุ่ม:", "ส่งข้อมูลการติดต่อ")
         ],
         "🗣️ บทพูดบรรยาย:",
         "จำลองลูกค้าภายนอกลงทะเบียนขอโปรโมชัน ข้อมูลจะไหลเข้าสู่คลังข้อมูล Store D1: LEAD ตาม DFD Process 1.0 อัตโนมัติ"),

        ("2️⃣ Step 2: [Marketing] เชื่อมแคมเปญ",
         "⏱️ เวลา: 01:00 – 02:30 (~1.5 นาที)",
         "pages/1_marketing.py (ล็อกอิน marketing1)",
         "เมนู 'งานการตลาด'",
         [
             ("โชว์แคมเปญ:", "CMP003 (ROI สูงสุด 103%)"),
             ("เลือก Lead:", "สมชาย หมายมั่น"),
             ("ผูกโปรโมชัน:", "ส่วนลด 15%"),
             ("กดปุ่ม:", "ส่งข้อมูลโปรโมชัน")
         ],
         "🗣️ บทพูดบรรยาย:",
         "ฝ่ายการตลาดใช้ผลวิเคราะห์จาก Data Science (Campaign ROI) เลือกแคมเปญที่มีผลตอบแทนสูงสุดให้ Lead เกิดการเชื่อมโยง DFD 1.0 กับ 5.0"),

        ("3️⃣ Step 3: [Sales] AI & ใบเสนอราคา",
         "⏱️ เวลา: 02:30 – 04:30 (~2 นาที)",
         "pages/2_sales_followup.py ➔ 3_order_billing.py (sale1)",
         "เมนู 'ติดตามการขาย' ➔ 'ใบเสนอราคา'",
         [
             ("คิวงาน AI:", "ชี้ LD0264 (Hot Lead 85%)"),
             ("บันทึกโทร:", "ลูกค้าตกลงรับข้อเสนอ ➔ กดบันทึก"),
             ("ออกใบเสนอราคา:", "เลือก LD0264 + แพ็กเกจ Enterprise"),
             ("กดปุ่ม:", "💾 ออกใบเสนอราคา (ได้รหัส SL)")
         ],
         "🗣️ บทพูดบรรยาย:",
         "ฝ่ายขายใช้ AI Lead Scoring จัดลำดับความสำคัญ ช่วยเพิ่มอัตราปิดการขาย และออกใบเสนอราคาตาม DFD Process 2.0")
    ]

    for idx, (head, tbox, scr, tab, fields, spk_head, spk_body) in enumerate(col16_defs):
        c16 = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.55), card16_w, card16_h)
        c16.fill.solid()
        c16.fill.fore_color.rgb = CARD_BG
        c16.line.color.rgb = BORDER_ACTIVE if idx == 2 else CARD_BORDER
        c16.line.width = Pt(1.5)
        tf16 = c16.text_frame
        tf16.word_wrap = True
        tf16.margin_top = tf16.margin_left = tf16.margin_right = Inches(0.25)

        p = tf16.paragraphs[0]
        p.text = head
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

        p_time = tf16.add_paragraph()
        p_time.text = tbox
        p_time.font.name = FONT_FAMILY
        p_time.font.size = Pt(9)
        p_time.font.bold = True
        p_time.font.color.rgb = SEMANTIC_AMBER
        p_time.space_before = Pt(3)

        p_scr = tf16.add_paragraph()
        p_scr.text = f"📍 หน้า: {scr}\n📑 แท็บ: {tab}"
        p_scr.font.name = FONT_FAMILY
        p_scr.font.size = Pt(8.8)
        p_scr.font.color.rgb = MUTED_SLATE
        p_scr.space_before = Pt(4)

        p_fhead = tf16.add_paragraph()
        p_fhead.text = "⌨️ ข้อมูลที่ต้องกรอก / คลิก:"
        p_fhead.font.name = FONT_FAMILY
        p_fhead.font.size = Pt(9.5)
        p_fhead.font.bold = True
        p_fhead.font.color.rgb = DARK_NAVY
        p_fhead.space_before = Pt(6)

        for fname, fval in fields:
            pf = tf16.add_paragraph()
            pf.text = f"• {fname} {fval}"
            pf.font.name = FONT_FAMILY
            pf.font.size = Pt(8.8)
            pf.font.color.rgb = DARK_NAVY

        p_sh = tf16.add_paragraph()
        p_sh.text = spk_head
        p_sh.font.name = FONT_FAMILY
        p_sh.font.size = Pt(9.5)
        p_sh.font.bold = True
        p_sh.font.color.rgb = PRIMARY_BLUE
        p_sh.space_before = Pt(6)

        p_sb = tf16.add_paragraph()
        p_sb.text = f'"{spk_body}"'
        p_sb.font.name = FONT_FAMILY
        p_sb.font.size = Pt(8.5)
        p_sb.font.color.rgb = MUTED_SLATE

    set_notes(s16, "Speaker Note: คนสาธิตคนเดียวมองสไลด์นี้แล้วพูดตามบทพูด และคลิก/กรอกข้อมูลตามตารางทีละขั้นตอน")

    # =========================================================================
    # SLIDE 17: สคริปต์สาธิตสด ขั้นตอนที่ 4 – 7 (สลิป, ยกระดับลูกค้า, บริการ 5⭐ & แดชบอร์ด)
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_slide_base(s17, "DEMO RUN-SHEET: PART 2", "สคริปต์สาธิตสด ขั้นตอนที่ 4 – 7 (สลิป, ยกระดับลูกค้า, บริการ 5⭐ & แดชบอร์ด)", 
                   "คู่มือสำหรับผู้สาธิตคนเดียว: ขั้นตอนปิดการขาย บริการลูกค้า และสรุปผล AI 4 ด้าน (04:30 – 10:00)", 17)

    grid17_defs = [
        # Col 0, Row 0
        (Inches(0.8), Inches(1.55), Inches(5.7), Inches(2.6),
         "4️⃣ Step 4: [Portal] ยืนยันคำสั่งซื้อ & แนบสลิป",
         "⏱️ 04:30 – 05:30 (~1 นาที) | หน้า pages/9_portal.py",
         [
             ("เลือกตัวตน:", "LD0264 (นายวิชัย ทองดี)"),
             ("แท็บ ③ ตรวจใบเสนอราคา:", "กดปุ่ม 'ยืนยันสั่งซื้อ'"),
             ("แท็บ ④ อัปโหลดสลิป:", "แนบไฟล์จำลอง slip.png ➔ ส่งหลักฐานชำระเงิน")
         ],
         "🗣️ บทพูด:", "ลูกค้าตรวจสอบความถูกต้องและส่งสลิปด้วยตนเอง ข้อมูลไหลเข้าสู่ DFD Process 3.0 อัตโนมัติ"),

        # Col 1, Row 0
        (Inches(6.8), Inches(1.55), Inches(5.733), Inches(2.6),
         "5️⃣ Step 5: [Sales] ตรวจรับเงิน ยกระดับ CUSTOMER",
         "⏱️ 05:30 – 06:30 (~1 นาที) | หน้า pages/3_order_billing.py (sale1)",
         [
             ("แท็บ ตรวจสอบชำระเงิน:", "เห็นรูปสลิป ➔ ใส่เลขอ้างอิง ➔ กด 'ยืนยันรับเงิน'"),
             ("แท็บ ออกใบเสร็จ:", "กด 'ออกใบเสร็จ' ➔ ดาวน์โหลดใบเสร็จรับเงิน"),
             ("จุดเน้นวิชาการ:", "ชี้ว่าระบบยกระดับสถานะจาก Lead เป็น CUSTOMER (รหัส CU) อัตโนมัติ")
         ],
         "🗣️ บทพูด:", "เมื่อฝ่ายขายตรวจรับเงินเสร็จ ระบบยกระดับ Lead เป็นลูกค้าทางการตาม DFD 3.0 พร้อมออกใบเสร็จ"),

        # Col 0, Row 1
        (Inches(0.8), Inches(4.3), Inches(5.7), Inches(2.65),
         "6️⃣ Step 6: [Support & Portal] บริการ & ประเมิน 5 ดาว",
         "⏱️ 06:30 – 08:00 (~1.5 นาที) | pages/5_support_ticket.py (cs1) & Portal",
         [
             ("หน้าต่าง CS (ซ้าย):", "ดูเคส CU0178 หรือ TK0008 ➔ ตอบแชทช่วยลูกค้า ➔ กด 'ปิดเคส'"),
             ("หน้าต่าง Portal (ขวา):", "แท็บ ⑤ ใบเสร็จ·แจ้งปัญหา·ให้คะแนน ➔ กด ⭐⭐⭐⭐⭐ ส่งคะแนน"),
             ("จุดเน้นวิชาการ:", "คะแนนประเมินส่งตรงกลับไปคำนวณ Customer Health Score ทันที")
         ],
         "🗣️ บทพูด:", "เก็บบันทึกประวัติบริการตาม DFD 4.0 คะแนนจะไหลไปคำนวณ Customer Health Score ต่อไป"),

        # Col 1, Row 1
        (Inches(6.8), Inches(4.3), Inches(5.733), Inches(2.65),
         "7️⃣ Step 7: [Executive Dashboard] สรุปผล Real-time 4 AI",
         "⏱️ 08:00 – 10:00 (~2 นาที) | pages/6_analytics_dashboard.py (admin1)",
         [
             ("1. RFM Segmentation:", "โชว์กลุ่ม Champions (CU0175) เทียบ At Risk (CU0178)"),
             ("2. Churn Health Score:", "ดัชนีสุขภาพลูกค้า 5 มิติ เตือนความเสี่ยงล่วงหน้า"),
             ("3. Lead Score & ROI:", "สรุปผลแคมเปญ CMP003 และกดปุ่ม Export รายงานยอดขาย CSV")
         ],
         "🗣️ บทพูด:", "ข้อมูลจากขั้นตอน 1-6 ไหลมารวมที่ Dashboard แบบ Real-time ผู้บริหารใช้ 4 โมเดล AI ขับเคลื่อนธุรกิจได้ทันที")
    ]

    for gx, gy, gw, gh, ghead, gtime, gacts, gspk_lbl, gspk_txt in grid17_defs:
        cg17 = s17.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, gx, gy, gw, gh)
        cg17.fill.solid()
        cg17.fill.fore_color.rgb = CARD_BG
        cg17.line.color.rgb = CARD_BORDER
        cg17.line.width = Pt(1.5)
        tg17 = cg17.text_frame
        tg17.word_wrap = True
        tg17.margin_top = tg17.margin_left = tg17.margin_right = Inches(0.18)

        gp = tg17.paragraphs[0]
        gp.text = ghead
        gp.font.name = FONT_FAMILY
        gp.font.size = Pt(11.5)
        gp.font.bold = True
        gp.font.color.rgb = PRIMARY_BLUE

        gt = tg17.add_paragraph()
        gt.text = gtime
        gt.font.name = FONT_FAMILY
        gt.font.size = Pt(8.5)
        gt.font.bold = True
        gt.font.color.rgb = SEMANTIC_AMBER
        gt.space_before = Pt(2)

        for aname, aval in gacts:
            pa = tg17.add_paragraph()
            pa.text = f"• {aname} {aval}"
            pa.font.name = FONT_FAMILY
            pa.font.size = Pt(8.3)
            pa.font.color.rgb = DARK_NAVY
            pa.space_before = Pt(1.5)

        ps = tg17.add_paragraph()
        ps.text = f"{gspk_lbl} \"{gspk_txt}\""
        ps.font.name = FONT_FAMILY
        ps.font.size = Pt(8)
        ps.font.color.rgb = MUTED_SLATE
        ps.space_before = Pt(3)

    set_notes(s17, "Speaker Note: ขั้นตอนที่ 4-7 สรุปการปิดการขาย ยกระดับลูกค้า บริการ 5 ดาว และเปิดแดชบอร์ด 4 AI จบใน 10 นาทีพอดี")

    out_pptx = os.path.join(ROOT_DEV, "docs", "Precision_AI_CRM.pptx")
    prs.save(out_pptx)
    print(f"✅ Successfully regenerated {len(prs.slides)} slides in {out_pptx} with Section 8 requirements and Solo Demo Run-Sheets (17 slides)!")


if __name__ == "__main__":
    create_deck()
