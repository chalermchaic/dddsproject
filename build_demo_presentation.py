"""
build_demo_presentation.py - Generate Dedicated 17-Slide Live Demo Presentation
Output: docs/demo.pptx

Features:
- Dedicated Live Demo Deck (Separate from project slides)
- 3 Clear Business Cases across 17 slides
- Split-View Layout:
  * Left: Action guide, role, exact data inputs, visual observation guide, speaker talking points
  * Right: Large real screenshot image from docs/evidence/ (so anyone can understand without opening web)
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
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Unified Modern Light Palette
BG_COLOR = RGBColor(248, 250, 252)       # #F8FAFC
CARD_BG = RGBColor(255, 255, 255)        # #FFFFFF
CARD_BORDER = RGBColor(226, 232, 240)    # #E2E8F0
PRIMARY_BLUE = RGBColor(37, 99, 235)     # #2563EB
SKY_BLUE = RGBColor(2, 132, 199)         # #0284C7
DARK_NAVY = RGBColor(15, 23, 42)         # #0F172A
MUTED_SLATE = RGBColor(100, 116, 139)    # #64748B
BORDER_ACTIVE = RGBColor(191, 219, 254)  # #BFDBFE

SEMANTIC_RED = RGBColor(220, 38, 38)     # #DC2626
SEMANTIC_GREEN = RGBColor(16, 185, 129)  # #10B981
SEMANTIC_AMBER = RGBColor(217, 119, 6)   # #D97706

FONT_FAMILY = "Segoe UI"
ROOT_DEV = r"c:\Users\momo\dev\dddsproject"
EVIDENCE_DIR = os.path.join(ROOT_DEV, "docs", "evidence")


def create_demo_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    def add_slide_base(slide, tag, title, subtitle, slide_num, total_slides=17):
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, SLIDE_HEIGHT)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()

        # Accent Bar
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.32), Inches(0.22), Inches(0.22))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = PRIMARY_BLUE
        top_bar.line.fill.background()

        # Header Text
        tbox = slide.shapes.add_textbox(Inches(1.12), Inches(0.28), Inches(10.0), Inches(0.95))
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
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY

        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = FONT_FAMILY
            p2.font.size = Pt(10)
            p2.font.color.rgb = MUTED_SLATE

        # Slide Number Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.2), Inches(0.32), Inches(1.35), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = CARD_BG
        pill.line.color.rgb = CARD_BORDER
        ptf = pill.text_frame
        ptf.margin_top = ptf.margin_bottom = ptf.margin_left = ptf.margin_right = 0
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = f"DEMO {slide_num:02d} / {total_slides:02d}"
        pp.font.name = FONT_FAMILY
        pp.font.size = Pt(9)
        pp.font.bold = True
        pp.font.color.rgb = MUTED_SLATE

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    def add_split_demo_slide(slide_num, tag, title, subtitle, role, page_info,
                             action_items, observe_text, speaker_script, img_filename):
        s = prs.slides.add_slide(blank_layout)
        add_slide_base(s, tag, title, subtitle, slide_num)

        # Left Info Card
        card_w = Inches(4.5)
        card_h = Inches(5.6)
        card_x = Inches(0.8)
        card_y = Inches(1.45)

        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, card_y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_top = ctf.margin_left = ctf.margin_right = Inches(0.25)
        ctf.margin_bottom = Inches(0.2)

        # Role & Page Header
        p0 = ctf.paragraphs[0]
        p0.text = f"👤 {role}"
        p0.font.name = FONT_FAMILY
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = PRIMARY_BLUE

        p_page = ctf.add_paragraph()
        p_page.text = f"📍 {page_info}"
        p_page.font.name = FONT_FAMILY
        p_page.font.size = Pt(9)
        p_page.font.color.rgb = MUTED_SLATE
        p_page.space_before = Pt(2)

        # Section: Actions
        p_act_head = ctf.add_paragraph()
        p_act_head.text = "⌨️ ขั้นตอน & ข้อมูลที่ต้องดำเนินการ:"
        p_act_head.font.name = FONT_FAMILY
        p_act_head.font.size = Pt(9.5)
        p_act_head.font.bold = True
        p_act_head.font.color.rgb = DARK_NAVY
        p_act_head.space_before = Pt(8)

        for act_lbl, act_val in action_items:
            pa = ctf.add_paragraph()
            pa.text = f"• {act_lbl} {act_val}"
            pa.font.name = FONT_FAMILY
            pa.font.size = Pt(8.5)
            pa.font.color.rgb = DARK_NAVY
            pa.space_before = Pt(2)

        # Section: Observation
        p_obs_head = ctf.add_paragraph()
        p_obs_head.text = "🔍 สิ่งที่เห็นในภาพ (ดูรูปตามรู้เรื่องทันที):"
        p_obs_head.font.name = FONT_FAMILY
        p_obs_head.font.size = Pt(9.5)
        p_obs_head.font.bold = True
        p_obs_head.font.color.rgb = SKY_BLUE
        p_obs_head.space_before = Pt(8)

        p_obs_body = ctf.add_paragraph()
        p_obs_body.text = observe_text
        p_obs_body.font.name = FONT_FAMILY
        p_obs_body.font.size = Pt(8.3)
        p_obs_body.font.color.rgb = DARK_NAVY
        p_obs_body.space_before = Pt(2)

        # Section: Talking Points
        p_spk_head = ctf.add_paragraph()
        p_spk_head.text = "🗣️ บทพูดนำเสนอ (Speaker Script):"
        p_spk_head.font.name = FONT_FAMILY
        p_spk_head.font.size = Pt(9.5)
        p_spk_head.font.bold = True
        p_spk_head.font.color.rgb = SEMANTIC_AMBER
        p_spk_head.space_before = Pt(8)

        p_spk_body = ctf.add_paragraph()
        p_spk_body.text = f'"{speaker_script}"'
        p_spk_body.font.name = FONT_FAMILY
        p_spk_body.font.size = Pt(8.3)
        p_spk_body.font.color.rgb = MUTED_SLATE
        p_spk_body.space_before = Pt(2)

        # Right Screenshot Picture
        img_x = Inches(5.5)
        img_y = Inches(1.45)
        img_w = Inches(7.033)
        img_h = Inches(5.6)

        # Frame behind image
        iframe = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, img_x, img_y, img_w, img_h)
        iframe.fill.solid()
        iframe.fill.fore_color.rgb = CARD_BG
        iframe.line.color.rgb = CARD_BORDER
        iframe.line.width = Pt(1.5)

        img_path = os.path.join(EVIDENCE_DIR, img_filename)
        if os.path.exists(img_path):
            s.shapes.add_picture(img_path, img_x + Inches(0.08), img_y + Inches(0.08),
                                 width=img_w - Inches(0.16), height=img_h - Inches(0.16))

        set_notes(s, f"Speaker Note for Slide {slide_num}: {speaker_script}\nAction: {action_items}")
        return s

    # =========================================================================
    # SLIDE 1: หน้าปก Live Demo & Quick Start Guide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_base(s1, "LIVE DEMO MANUAL", "Smart CRM & Data Science Analytics: Live Demo Guide",
                   "คู่มือสาธิตการทำงานระบบจริงแบบทีละขั้นตอน (พร้อมภาพประกอบหน้าจอจริงทุกขั้นตอน)", 1)

    # Left: Quick Start & Tool
    card1_w = Inches(5.4)
    card1_h = Inches(5.6)
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), card1_w, card1_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = CARD_BORDER
    c1.line.width = Pt(1.5)
    c1_tf = c1.text_frame
    c1_tf.word_wrap = True
    c1_tf.margin_top = c1_tf.margin_left = c1_tf.margin_right = Inches(0.3)

    cp0 = c1_tf.paragraphs[0]
    cp0.text = "🚀 คำสั่งเปิดระบบเริ่มซ้อมทันที (Quick Start)"
    cp0.font.name = FONT_FAMILY
    cp0.font.size = Pt(14)
    cp0.font.bold = True
    cp0.font.color.rgb = PRIMARY_BLUE

    qstart = [
        ("1. คืนค่าฐานข้อมูลเริ่มต้น (เลือกวิธีใดวิธีหนึ่ง):",
         "• วิธี ก (Terminal): python db/seed_data.py\n• วิธี ข (บนหน้าเว็บ): กดปุ่ม '🔄 รีเซ็ตฐานข้อมูล Demo' บนหน้า Login หรือที่ Sidebar ได้ทันทีใน 2 วินาที!"),
        ("2. รันแอปพลิเคชันระบบต้นแบบ:",
         "• streamlit run app.py\n• เข้าใช้งานผ่านเบราว์เซอร์ที่: http://localhost:8501"),
        ("3. เทคนิคคนเดียวพูดไปคลิกไป (Solo Demo):",
         "• หน้าต่างซ้าย (ปกติ): Staff CRM (admin1, marketing1, sale1, cs1)\n• หน้าต่างขวา (Incognito): Customer Portal (guest)\n• สลับหน้าจอซ้าย-ขวาได้ทันที ไม่ต้องล็อกเอาท์เข้าออกซ้ำซ้อน"),
        ("4. โครงสร้างการนำเสนอ:",
         "• แบ่งเป็น 3 เคสหลัก ครอบคลุม 14 กิจกรรม DFD (Process 1.0 - 5.0)\n• ดูรูปตามสไลด์ก็เข้าใจขั้นตอนได้ทันที 100% แม้ไม่ต้องเปิดเว็บ!")
    ]
    for h, b in qstart:
        p1 = c1_tf.add_paragraph()
        p1.text = f"• {h}"
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = DARK_NAVY
        p1.space_before = Pt(8)
        p2 = c1_tf.add_paragraph()
        p2.text = f"  {b}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(8.8)
        p2.font.color.rgb = MUTED_SLATE

    # Right: Login Screenshot
    login_img = os.path.join(EVIDENCE_DIR, "00_login.png")
    if os.path.exists(login_img):
        s1.shapes.add_picture(login_img, Inches(6.5), Inches(1.45), width=Inches(6.033), height=Inches(5.6))
    set_notes(s1, "หน้าแรกเปิดระบบ: เลือกล็อกอินตาม Role หรือเข้า Portal จำลอง พร้อมปุ่ม Reset DB")

    # =========================================================================
    # SLIDE 2: ผังจำลอง 3 เคส & ไทม์ไลน์ 10 นาที
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_base(s2, "DEMO STORYLINE & ROADMAP", "ผังจำลอง 3 เคสธุรกิจ และเส้นทางกระแสข้อมูล (Storyline Map)",
                   "การบูรณาการ End-to-End ครอบคลุม 14 กิจกรรม DFD (Process 1.0 – 5.0) ภายใน 10 นาที", 2)

    cases = [
        ("เคสที่ 1: Lead-to-Customer with AI",
         "⏱️ 00:00 – 06:30 (สไลด์ 3 – 9)",
         PRIMARY_BLUE,
         "• ลูกค้าใหม่ลงทะเบียนผ่าน Portal\n• การตลาดผูกแคมเปญ ROI สูงสุด (CMP003)\n• ฝ่ายขายเปิดคิว AI พบ Hot Lead (LD0264 85%)\n• บันทึกโทรและออกใบเสนอราคา\n• ลูกค้าโอนเงินแนบสลิปผ่าน Portal\n• ฝ่ายขายตรวจสลิป ออกใบเสร็จ ยกระดับเป็น CUSTOMER ทางการ"),

        ("เคสที่ 2: Support & 5-Star Rating",
         "⏱️ 06:30 – 08:00 (สไลด์ 10 – 12)",
         SKY_BLUE,
         "• ลูกค้าแจ้งปัญหาผ่านระบบ (CU0178)\n• เจ้าหน้าที่เปิดเคส TK บันทึกความรุนแรง\n• แชทสนทนาสดแก้ไขปัญหาและปิดเคส\n• ลูกค้าประเมินความพึงพอใจ 5 ดาว ⭐⭐⭐⭐⭐\n• คะแนนส่งตรงไปคำนวณ Customer Health Score"),

        ("เคสที่ 3: Executive Real-time 4 AI",
         "⏱️ 08:00 – 10:00 (สไลด์ 13 – 17)",
         SEMANTIC_AMBER,
         "• ผู้บริหารเปิดดูแดชบอร์ดสรุปผลสด:\n  1. Lead Scoring: จัดกลุ่ม Hot/Warm/Cold\n  2. RFM: Champions (CU0175) vs At Risk (CU0178)\n  3. Customer Health & Churn: เตือนภัยความเสี่ยง\n  4. Campaign ROI: วิเคราะห์งบการตลาด (103%)\n• Export รายงานยอดขายเป็นไฟล์ CSV")
    ]

    for idx, (chead, ctime, ccolor, cdesc) in enumerate(cases):
        cx = Inches(0.8 + idx * 4.0)
        cbox = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, Inches(1.55), Inches(3.7), Inches(4.3))
        cbox.fill.solid()
        cbox.fill.fore_color.rgb = CARD_BG
        cbox.line.color.rgb = CARD_BORDER
        cbox.line.width = Pt(1.5)

        ctf = cbox.text_frame
        ctf.word_wrap = True
        ctf.margin_top = ctf.margin_left = ctf.margin_right = Inches(0.25)

        p = ctf.paragraphs[0]
        p.text = chead
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ccolor

        pt = ctf.add_paragraph()
        pt.text = ctime
        pt.font.name = FONT_FAMILY
        pt.font.size = Pt(9.5)
        pt.font.bold = True
        pt.font.color.rgb = DARK_NAVY
        pt.space_before = Pt(3)

        pd = ctf.add_paragraph()
        pd.text = cdesc
        pd.font.name = FONT_FAMILY
        pd.font.size = Pt(9.2)
        pd.font.color.rgb = MUTED_SLATE
        pd.space_before = Pt(10)

    # Bottom Cheat Sheet Banner
    bot_b = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.0), Inches(11.733), Inches(1.1))
    bot_b.fill.solid()
    bot_b.fill.fore_color.rgb = RGBColor(239, 246, 255)
    bot_b.line.color.rgb = PRIMARY_BLUE
    bot_b.line.width = Pt(1.5)
    btf = bot_b.text_frame
    btf.word_wrap = True
    btf.margin_top = Inches(0.12)
    btf.margin_left = Inches(0.25)
    btf.margin_right = Inches(0.25)

    bp0 = btf.paragraphs[0]
    bp0.text = "📋 Cheat Sheet รหัสจำลองที่ต้องใช้ตลอดการเดโม (แปะข้างคีย์บอร์ด):"
    bp0.font.name = FONT_FAMILY
    bp0.font.size = Pt(10.5)
    bp0.font.bold = True
    bp0.font.color.rgb = PRIMARY_BLUE

    bp1 = btf.add_paragraph()
    bp1.text = "• Lead AI Hot (85%): LD0264 (วิชัย ทองดี)  |  • แคมเปญ ROI สูงสุด (103%): CMP003  |  • ลูกค้า Churn Risk: CU0178 (ร้านสมหญิง)  |  • ลูกค้า Champions: CU0175  |  • Ticket 5 ดาว: TK0008"
    bp1.font.name = FONT_FAMILY
    bp1.font.size = Pt(9.5)
    bp1.font.color.rgb = DARK_NAVY
    bp1.space_before = Pt(2)
    set_notes(s2, "ผังภาพรวม 3 เคส 10 นาที แนะนำตัวละครและรหัสจำลองที่ใช้ตลอดการสาธิต")

    # =========================================================================
    # SLIDE 3: [เคส 1] 1.1 Portal: ลูกค้าลงทะเบียนเอง
    # =========================================================================
    add_split_demo_slide(
        slide_num=3,
        tag="CASE 1 · STEP 1.1 (PROCESS 1.2)",
        title="พอร์ทัลลูกค้า: สมชายลงทะเบียนขอรับโปรโมชัน (Lead Intake)",
        subtitle="จำลองลูกค้าภายนอกส่งข้อมูลเข้าสู่ระบบตาม DFD Process 1.0 (Store D1: LEAD)",
        role="ผู้สนใจภายนอก / ลูกค้า (Customer Portal: guest)",
        page_info="หน้า pages/9_portal.py · แท็บ ① 'ลงทะเบียนขอรับข้อมูล'",
        action_items=[
            ("กรอกชื่อ-นามสกุล:", "คุณสมชาย หมายมั่น"),
            ("เบอร์โทรศัพท์:", "081-999-8888"),
            ("อีเมลติดต่อ:", "somchai@email.com"),
            ("ช่องทางที่พบ:", "Facebook Ads"),
            ("กดปุ่ม:", "ส่งข้อมูลการติดต่อ")
        ],
        observe_text="เห็นแบบฟอร์มลงทะเบียนบน Portal เมื่อกดส่ง ระบบจะออกรหัส Lead ให้อัตโนมัติ และสถานะเริ่มต้นเป็น 'รอการติดต่อ'",
        speaker_script="จำลองมุมมองลูกค้าภายนอกลงทะเบียนขอโปรโมชันด้วยตนเองผ่าน Customer Portal ข้อมูลจะไหลเข้าสู่ Store D1: LEAD ตาม DFD 1.0 ทันที",
        img_filename="1_2_portal_register.png"
    )

    # =========================================================================
    # SLIDE 4: [เคส 1] 1.2 การตลาด: คัดกรอง & ส่งโปรโมชัน
    # =========================================================================
    add_split_demo_slide(
        slide_num=4,
        tag="CASE 1 · STEP 1.2 (PROCESS 1.1 & 1.3)",
        title="ฝ่ายการตลาด: คัดกรอง Lead และส่งโปรโมชันเจาะจง (Campaign Match)",
        subtitle="เชื่อมโยงผลวิเคราะห์ Campaign ROI (DFD 5.1) สู่การมอบโปรโมชัน (DFD 1.3)",
        role="ฝ่ายการตลาด (marketing1: ชนิกานต์ การตลาด)",
        page_info="หน้า pages/1_marketing.py · เมนู 'งานการตลาด'",
        action_items=[
            ("ตรวจสอบแคมเปญ:", "ดูแคมเปญ ROI สูงสุด CMP003 (Digital Ads Q3)"),
            ("เลือก Lead เป้าหมาย:", "คุณสมชาย หมายมั่น ที่เพิ่งลงทะเบียนเข้ามา"),
            ("ผูกสิทธิ์โปรโมชัน:", "มอบส่วนลดพิเศษ 15%"),
            ("กดปุ่ม:", "ส่งข้อมูลโปรโมชัน")
        ],
        observe_text="ในตารางแคมเปญแสดงผลการสร้างแคมเปญใหม่ และเมื่อส่งโปรโมชัน ระบบจะบันทึกประวัติลงใน Store D2: LEAD_ACTIVITY ทันที",
        speaker_script="ฝ่ายการตลาดใช้ข้อมูล Data Science จาก Campaign ROI ตัดสินใจเลือกแคมเปญที่มีผลตอบแทนสูงสุดให้ Lead เกิดการเชื่อมโยง DFD 1.0 และ 5.0",
        img_filename="1_1_campaign_saved.png"
    )

    # =========================================================================
    # SLIDE 5: [เคส 1] 1.3 ฝ่ายขาย: คิวงาน AI Lead Score
    # =========================================================================
    add_split_demo_slide(
        slide_num=5,
        tag="CASE 1 · STEP 1.3 (PROCESS 2.1)",
        title="ฝ่ายขาย: จัดลำดับคิวโทรด้วย AI Lead Scoring (AI Priority Queue)",
        subtitle="โมเดล Random Forest Classifier คัดกรอง Hot Lead ตาม DFD Process 2.1",
        role="ฝ่ายขาย (sale1: ณัฐวุฒิ ขายเก่ง)",
        page_info="หน้า pages/2_sales_followup.py · แท็บ '🔥 คิวงานจัดลำดับด้วย AI'",
        action_items=[
            ("เปิดแท็บคิว AI:", "ระบบคำนวณความน่าจะเป็นในการซื้อแบบ Real-time"),
            ("ระบุตัวตนเป้าหมาย:", "ค้นหา Lead 'LD0264' (นายวิชัย ทองดี)"),
            ("ตรวจสอบคะแนน AI:", "ได้คะแนน 85.4% จัดอยู่ในกลุ่ม '🔥 Hot Lead'"),
            ("ข้อมูลสนับสนุน:", "ช่องทาง Direct, มีประวัติติดตาม 4 ครั้ง")
        ],
        observe_text="หน้าจอแสดงคิวงานเรียงตามความเร่งด่วน โดยมีแถบสีแดงระบุกลุ่ม Hot Lead พร้อมแสดง % โอกาสปิดการขาย ชัดเจน",
        speaker_script="ฝ่ายขายไม่ต้องสุ่มโทร แต่เปิดคิวงาน AI ระบบพยากรณ์โอกาสซื้อด้วย Random Forest ทำให้ทีมขายโฟกัส Hot Lead ได้ตรงเป้าหมาย",
        img_filename="2_1_ai_priority.png"
    )

    # =========================================================================
    # SLIDE 6: [เคส 1] 1.4 ฝ่ายขาย: บันทึกกิจกรรมโทรศัพท์
    # =========================================================================
    add_split_demo_slide(
        slide_num=6,
        tag="CASE 1 · STEP 1.4 (PROCESS 2.2)",
        title="ฝ่ายขาย: บันทึกกิจกรรมการโทรและอัปเดตสถานะ (Activity Logging)",
        subtitle="บันทึกผลการปฏิสัมพันธ์ลงใน Store D2: LEAD_ACTIVITY ตาม DFD Process 2.2",
        role="ฝ่ายขาย (sale1)",
        page_info="หน้า pages/2_sales_followup.py · แท็บ '🔍 ค้นหา & บันทึกกิจกรรม'",
        action_items=[
            ("เลือก Lead:", "LD0264 (นายวิชัย ทองดี)"),
            ("ประเภทกิจกรรม:", "โทรศัพท์ (Phone Call)"),
            ("บันทึกผลการติดต่อ:", "โทรประสานงาน นำเสนอโซลูชัน ลูกค้าขอใบเสนอราคา"),
            ("อัปเดตสถานะ:", "เปลี่ยนเป็น 'อยู่ระหว่างเสนอขาย' ➔ กด 💾 บันทึก")
        ],
        observe_text="ฝั่งซ้ายเป็นฟอร์มบันทึกผล และฝั่งขวาจะขึ้นไทม์ไลน์ประวัติการติดต่อพร้อมเวลา Timestamp ที่อัปเดตทันที",
        speaker_script="ประวัติการติดต่อทุกครั้งถูกบันทึกอย่างเป็นระบบ ไทม์ไลน์ฝั่งขวาแสดงประวัติย้อนหลังช่วยให้การส่งต่องานในทีมขายราบรื่น",
        img_filename="2_2_activity_timeline.png"
    )

    # =========================================================================
    # SLIDE 7: [เคส 1] 1.5 ฝ่ายขาย: ออกใบเสนอราคา (SL)
    # =========================================================================
    add_split_demo_slide(
        slide_num=7,
        tag="CASE 1 · STEP 1.5 (PROCESS 2.3)",
        title="ฝ่ายขาย: ออกใบเสนอราคาและคำนวณส่วนลดอัตโนมัติ (Quotation)",
        subtitle="ออกเอกสารเสนอราคา บันทึกลง Store D3: SALE ตาม DFD Process 2.3",
        role="ฝ่ายขาย (sale1)",
        page_info="หน้า pages/3_order_billing.py · แท็บ '📝 ออกใบเสนอราคา'",
        action_items=[
            ("เลือกลูกค้า:", "LD0264 (นายวิชัย ทองดี)"),
            ("เลือกรายการสินค้า:", "Enterprise CRM License (12 เดือน)"),
            ("ระบบคำนวณอัตโนมัติ:", "หักส่วนลดแคมเปญ 15% คำนวณยอดสุทธิ"),
            ("กดปุ่มบันทึก:", "💾 ออกใบเสนอราคา ➔ ออกรหัส SL สำเร็จ")
        ],
        observe_text="ตารางแสดงรายการสินค้าและส่วนลด และขึ้นข้อความยืนยันการออกใบเสนอราคาพร้อมรหัสเอกสาร SL สถานะ 'ออกใบเสนอราคาแล้ว'",
        speaker_script="ระบบคำนวณส่วนลดตามแคมเปญให้อัตโนมัติ พร้อมออกเอกสารเสนอราคาที่มีความถูกต้องตามหลักบัญชีตาม DFD 2.3",
        img_filename="2_3_quotation_issued.png"
    )

    # =========================================================================
    # SLIDE 8: [เคส 1] 1.6 Portal: ยืนยันสั่งซื้อ & แนบสลิป
    # =========================================================================
    add_split_demo_slide(
        slide_num=8,
        tag="CASE 1 · STEP 1.6 (PROCESS 3.1 & 3.2)",
        title="พอร์ทัลลูกค้า: ยืนยันคำสั่งซื้อและอัปโหลดสลิปโอนเงิน (Order & Slip)",
        subtitle="ลูกค้าตรวจสอบใบเสนอราคาและส่งหลักฐานชำระเงินเข้า DFD Process 3.1–3.2",
        role="ผู้สนใจ / ลูกค้า (Customer Portal: guest สวมบท LD0264)",
        page_info="หน้า pages/9_portal.py · สลับตัวตนเป็น LD0264",
        action_items=[
            ("แท็บ ③ ตรวจใบเสนอราคา:", "ตรวจสอบยอดเงินแล้วกดปุ่ม 'ยืนยันสั่งซื้อ'"),
            ("แท็บ ④ อัปโหลดสลิป:", "แนบไฟล์หลักฐานการโอนเงินจำลอง slip.png"),
            ("ส่งหลักฐานชำระเงิน:", "กดปุ่มส่งหลักฐาน ➔ ระบบส่งสลิปให้ฝ่ายขายตรวจ")
        ],
        observe_text="ในระบบฝ่ายขาย (หน้า 3_order_billing.py แท็บ 3.2) จะปรากฏรูปภาพสลิปที่ลูกค้าแนบมา พร้อมปุ่มให้ฝ่ายขายกดตรวจสอบยืนยัน",
        speaker_script="ลูกค้าตรวจสอบความถูกต้องและส่งสลิปด้วยตนเองผ่าน Portal ข้อมูลไหลเข้าสู่ DFD Process 3.0 อัตโนมัติ",
        img_filename="3_2_payment_check.png"
    )

    # =========================================================================
    # SLIDE 9: [เคส 1] 1.7 ฝ่ายขาย: ตรวจรับเงิน ยกระดับสู่ CUSTOMER
    # =========================================================================
    add_split_demo_slide(
        slide_num=9,
        tag="CASE 1 · STEP 1.7 (PROCESS 3.3)",
        title="ฝ่ายขาย: ตรวจรับเงิน ยกระดับเป็น CUSTOMER & ออกใบเสร็จ (Closed-Won)",
        subtitle="เปลี่ยนสถานะเป็น 'ปิดการขายสำเร็จ' และบันทึก Store D4: CUSTOMER (DFD 3.3)",
        role="ฝ่ายขาย (sale1)",
        page_info="หน้า pages/3_order_billing.py · แท็บ '🧾 ออกใบเสร็จ + บันทึกลูกค้า'",
        action_items=[
            ("ตรวจสอบสลิป:", "ใส่เลขอ้างอิงโอนเงิน ➔ กดปุ่ม 'ยืนยันรับเงิน'"),
            ("ออกใบเสร็จรับเงิน:", "กดปุ่ม 'ออกใบเสร็จ' ➔ ดาวน์โหลดเอกสาร"),
            ("🌟 ไฮไลต์วิชาการสำคัญ:", "ระบบยกระดับ Lead เป็น CUSTOMER ทางการ (รหัส CUxxxx) อัตโนมัติ")
        ],
        observe_text="สถานะเปลี่ยนเป็น 'ปิดการขายสำเร็จ' มีปุ่มดาวน์โหลดใบเสร็จ และในฐานข้อมูลมีแถวใหม่เพิ่มในตาราง CUSTOMER",
        speaker_script="เมื่อตรวจรับเงินถูกต้อง ระบบยกระดับสถานะจาก Lead สู่ CUSTOMER ทางการทันทีก่อนออกใบเสร็จ ถือเป็นการปิดการขายสมบูรณ์",
        img_filename="3_3_receipt_issued.png"
    )

    # =========================================================================
    # SLIDE 10: [เคส 2] 2.1 บริการลูกค้า: เปิดเคสแจ้งปัญหา
    # =========================================================================
    add_split_demo_slide(
        slide_num=10,
        tag="CASE 2 · STEP 2.1 (PROCESS 4.1)",
        title="ฝ่ายบริการลูกค้า: รับแจ้งปัญหาและเปิดเคส (Ticket Registration)",
        subtitle="บันทึกข้อมูลเคสปัญหาลงใน Store D5: TICKET ตาม DFD Process 4.1",
        role="ฝ่ายบริการลูกค้า (cs1: ศุภชัย ซัพพอร์ต)",
        page_info="หน้า pages/5_support_ticket.py · แท็บ '➕ เปิดเคสใหม่'",
        action_items=[
            ("เลือกลูกค้า:", "CU0178 (ร้านสมหญิง การค้า)"),
            ("หัวข้อปัญหา:", "ไม่สามารถเปิดดูรายงานสรุปยอดขายรายไตรมาสได้"),
            ("ระดับความรุนแรง:", "Medium | หมวดหมู่: ระบบขัดข้อง"),
            ("กดปุ่ม:", "🎫 เปิดเคส ➔ ออกรหัสเคส TKxxxx สำเร็จ")
        ],
        observe_text="แสดงกล่องยืนยันเปิดเคสสำเร็จ พร้อมรหัสเคสใหม่ และสถานะตั้งต้นเป็น 'เปิดเคสใหม่' รอเจ้าหน้าที่เข้าดำเนินการ",
        speaker_script="ฝ่ายบริการลูกค้ารับแจ้งปัญหาและบันทึกเข้าระบบ โดยระบุระดับความรุนแรงและหมวดหมู่เพื่อจัดสรรเจ้าหน้าที่เข้าแก้ไข",
        img_filename="4_1_ticket_created.png"
    )

    # =========================================================================
    # SLIDE 11: [เคส 2] 2.2 บริการลูกค้า: แชทสนทนาสด & ปิดเคส
    # =========================================================================
    add_split_demo_slide(
        slide_num=11,
        tag="CASE 2 · STEP 2.2 (PROCESS 4.2)",
        title="ฝ่ายบริการลูกค้า: สนทนา ประสานงาน และแก้ไขปัญหา (Ticket Resolution)",
        subtitle="บันทึกข้อความลง Store D6: TICKET_MESSAGE ตาม DFD Process 4.2",
        role="ฝ่ายบริการลูกค้า (cs1)",
        page_info="หน้า pages/5_support_ticket.py · แท็บ '📥 คิวเคส & สนทนา'",
        action_items=[
            ("เลือกเคสปัญหา:", "เคสที่เพิ่งเปิดขึ้นมา"),
            ("พิมพ์ตอบในแชท:", "เจ้าหน้าที่กำลังรีเซ็ตแคชให้ คาดว่าจะใช้งานได้ใน 15 นาที"),
            ("บันทึกการแก้ไข:", "แก้ไขปัญหาเสร็จสิ้น ➔ เปลี่ยนสถานะเป็น 'ปิดเคสสำเร็จ'"),
            ("กดปุ่ม:", "💾 อัปเดตสถานะ")
        ],
        observe_text="เห็นหน้าต่างแชทที่มีข้อความสนทนาระหว่างลูกค้าและเจ้าหน้าที่ และสถานะเคสเปลี่ยนเป็นสีเขียว 'ปิดเคสสำเร็จ'",
        speaker_script="ระบบมีช่องทางสนทนาที่เก็บบันทึกประวัติการสื่อสารทั้งหมด เพื่อความโปร่งใสและตรวจสอบย้อนหลังได้ตาม DFD 4.2",
        img_filename="4_2_ticket_chat.png"
    )

    # =========================================================================
    # SLIDE 12: [เคส 2] 2.3 Portal: ปิดเคส & ประเมิน 5 ดาว
    # =========================================================================
    add_split_demo_slide(
        slide_num=12,
        tag="CASE 2 · STEP 2.3 (PROCESS 4.3)",
        title="พอร์ทัลลูกค้า: ประเมินความพึงพอใจการบริการ 5 ดาว (CSAT Feedback)",
        subtitle="บันทึก Service_Rating ตาม DFD 4.3 ส่งตรงไปคำนวณ Customer Health Score",
        role="ลูกค้า (Customer Portal: guest)",
        page_info="หน้า pages/9_portal.py · แท็บ '⑤ ใบเสร็จ · แจ้งปัญหา · ให้คะแนน'",
        action_items=[
            ("เลือกเคสปัญหา:", "เคสที่สถานะปิดสำเร็จแล้ว"),
            ("ให้คะแนนบริการ:", "เลือกคะแนนระดับ ⭐⭐⭐⭐⭐ (5 ดาวเต็ม)"),
            ("ข้อความชื่นชม:", "แก้ไขปัญหาได้อย่างรวดเร็ว ประทับใจมาก"),
            ("กดปุ่ม:", "⭐ ส่งคะแนน")
        ],
        observe_text="หน้าจอขึ้นข้อความขอบคุณ และคะแนน 5 ดาวจะถูกบันทึกลงฟิลด์ Service_Rating ในตาราง TICKET ของฐานข้อมูล",
        speaker_script="ลูกค้าประเมินความพึงพอใจผ่าน Portal โดยคะแนนนี้จะส่งตรงไปเป็นตัวแปรคำนวณ Customer Health Score ทันที",
        img_filename="4_3_rating_given.png"
    )

    # =========================================================================
    # SLIDE 13: [เคส 3] 3.1 AI Feature 1: Lead Scoring
    # =========================================================================
    add_split_demo_slide(
        slide_num=13,
        tag="CASE 3 · FEATURE 1 (ANALYTICS)",
        title="วิทยาศาสตร์ข้อมูล 1: พยากรณ์โอกาสปิดการขาย (Lead Scoring Model)",
        subtitle="โมเดล Random Forest Classifier 300 Trees พยากรณ์ความน่าจะเป็น ($0–100\%$) บน SQL Views",
        role="ผู้บริหาร / ฝ่ายวิเคราะห์ (admin1)",
        page_info="หน้า pages/6_analytics_dashboard.py · แท็บ 'Lead Scoring'",
        action_items=[
            ("ประสิทธิภาพโมเดล:", "ROC-AUC > 0.65, Accuracy และ F1-Score สูง"),
            ("การจัดกลุ่มโอกาสซื้อ:", "Hot (>70%), Warm (40-70%), Cold (<40%)"),
            ("ตารางจัดอันดับ Lead:", "แสดง Lead ที่มีคะแนนสูงสุด พร้อม Feature Importance")
        ],
        observe_text="แสดงกราฟ Probability Distribution จำแนกกลุ่ม Lead พร้อมตารางคะแนนพยากรณ์และตัวแปรที่มีอิทธิพลสูงสุด",
        speaker_script="Machine Learning ช่วยให้ผู้บริหารเห็นภาพรวมศักยภาพของ Lead ทั้งหมด และจัดสรรทรัพยากรทีมขายได้อย่างแม่นยำ",
        img_filename="6_1_lead_scoring.png"
    )

    # =========================================================================
    # SLIDE 14: [เคส 3] 3.2 AI Feature 2: RFM Segmentation
    # =========================================================================
    add_split_demo_slide(
        slide_num=14,
        tag="CASE 3 · FEATURE 2 (ANALYTICS)",
        title="วิทยาศาสตร์ข้อมูล 2: การจัดกลุ่มลูกค้าด้วย RFM (Customer Segmentation)",
        subtitle="Quintile Scoring + K-Means วิเคราะห์ Recency, Frequency, Monetary ลูกค้า 303 ราย",
        role="ผู้บริหาร / การตลาด (admin1)",
        page_info="หน้า pages/6_analytics_dashboard.py · แท็บ 'RFM Segmentation'",
        action_items=[
            ("กลุ่ม Champions:", "ชี้ CU0175 ซื้อ 5 ครั้ง ยอด 9.4 แสน ล่าสุด 15 วันก่อน"),
            ("กลุ่ม At Risk / Churn:", "ชี้ CU0178 เคยซื้อแต่หยุดไปนาน 548 วัน"),
            ("กลยุทธ์เฉพาะกลุ่ม:", "ระบบแนะนำกลยุทธ์ Upsell หรือ Win-back อัตโนมัติ")
        ],
        observe_text="เห็น Treemap แสดงสัดส่วนลูกค้าแต่ละกลุ่ม และ Scatter Plot 3 มิติ ชี้จุดตำแหน่งลูกค้ากลุ่ม Champions เทียบกับ At Risk",
        speaker_script="RFM ช่วยแยกแยะระหว่างลูกค้าชั้นดีและลูกค้าที่กำลังจะหายไป เพื่อให้ทีมการตลาดทำแคมเปญรักษาลูกค้าได้อย่างตรงจุด",
        img_filename="6_2_rfm.png"
    )

    # =========================================================================
    # SLIDE 15: [เคส 3] 3.3 AI Feature 3: Churn & Health Score
    # =========================================================================
    add_split_demo_slide(
        slide_num=15,
        tag="CASE 3 · FEATURE 3 (ANALYTICS)",
        title="วิทยาศาสตร์ข้อมูล 3: ดัชนีสุขภาพลูกค้าและการเตือนภัย Churn (Health Score)",
        subtitle="ประเมินความเสี่ยงล่วงหน้า 5 มิติ (Service, Sales, Recency, Ticket, Payment)",
        role="ผู้บริหาร / บริการลูกค้า (admin1)",
        page_info="หน้า pages/6_analytics_dashboard.py · แท็บ 'Customer Health & Churn'",
        action_items=[
            ("ตัวอย่างเสี่ยงสูง (At Risk):", "ร้านสมหญิง การค้า (CU0178) คะแนนสุขภาพต่ำ"),
            ("วิเคราะห์สาเหตุ:", "ไม่ซื้อนานเกินรอบ + มีเคสปัญหาค้างอยู่ 2 เคส"),
            ("ระบบเตือนภัยล่วงหน้า:", "แจ้งเตือนทีม CS เข้าไปดูแลทันทีก่อนลูกค้ายกเลิก")
        ],
        observe_text="เห็นเกจวัดคะแนนสุขภาพลูกค้า (Health Score Gauge) และรายชื่อลูกค้ากลุ่มเสี่ยงสูง (High Churn Risk) พร้อมสาเหตุ",
        speaker_script="ระบบไม่รอให้ลูกค้ายกเลิกสัญญา แต่ตรวจจับพฤติกรรมผิดปกติล่วงหน้าจาก 5 มิติ เพื่อให้ทีมงานเข้าแก้ไขได้ทันท่วงที",
        img_filename="6_3_churn.png"
    )

    # =========================================================================
    # SLIDE 16: [เคส 3] 3.4 AI Feature 4: Campaign Financial ROI
    # =========================================================================
    add_split_demo_slide(
        slide_num=16,
        tag="CASE 3 · FEATURE 4 (ANALYTICS)",
        title="วิทยาศาสตร์ข้อมูล 4: วิเคราะห์ความคุ้มค่าทางการเงิน (Campaign Financial ROI)",
        subtitle="คำนวณ ROI, ROAS, CAC, CPL และ Conversion Funnel 4 ขั้น วิเคราะห์ความคุ้มทุน",
        role="ผู้บริหาร / การตลาด (admin1)",
        page_info="หน้า pages/6_analytics_dashboard.py · แท็บ 'Campaign ROI'",
        action_items=[
            ("แคมเปญ ROI สูงสุด:", "CMP003 (Digital Ads Q3)"),
            ("งบประมาณแคมเปญ:", "฿80,000 | สร้างรายได้จริง ฿8,350,000"),
            ("ผลตอบแทนสุทธิ (ROI):", "103.4% ปิดการขายได้ 40 ราย (Conversion 37%)"),
            ("การตัดสินใจธุรกิจ:", "ผู้บริหารจัดสรรงบไตรมาสถัดไปสู่ช่องทางที่มี ROI สูงสุด")
        ],
        observe_text="เห็นกราฟเปรียบเทียบ ROI รายแคมเปญ และตารางแจกแจงเม็ดเงินลงทุน รายได้ และอัตราผลตอบแทนทางการเงินอย่างละเอียด",
        speaker_script="ฝ่ายการตลาดพิสูจน์ความคุ้มค่าของงบโฆษณาได้จริง แคมเปญ Digital Ads Q3 ให้ ROI เกิน 100% ตอบโจทย์การลงทุนของผู้บริหาร",
        img_filename="5_1_6_4_campaign_roi.png"
    )

    # =========================================================================
    # SLIDE 17: บทสรุป: รายงานยอดขาย & ความพร้อมส่งมอบ
    # =========================================================================
    add_split_demo_slide(
        slide_num=17,
        tag="EXECUTIVE SUMMARY & HAND-OFF",
        title="บทสรุปการสาธิตระบบ: รายงานยอดขายและส่งมอบผลงาน (Delivery Ready)",
        subtitle="บูรณาการฐานข้อมูล 3NF สู่ซอฟต์แวร์ต้นแบบที่ใช้งานได้จริง 100% พร้อมเปิดรับ Q&A",
        role="ผู้ดูแลระบบ / สรุปภาพรวม (admin1)",
        page_info="หน้า pages/6_analytics_dashboard.py · แท็บ 'รายงานสรุปยอดขาย'",
        action_items=[
            ("สรุปยอดขายรวม:", "กราฟแสดงแนวโน้มยอดขายรายเดือนและรายพนักงาน"),
            ("Export ข้อมูลรายงาน:", "ปุ่มดาวน์โหลดรายงานสรุปยอดขายเป็นไฟล์ CSV"),
            ("ความพร้อมส่งมอบ:", "ฐานข้อมูล 3NF, DFD 14 กิจกรรม Balanced 100%, Pytest 37/37 ผ่าน")
        ],
        observe_text="เห็นกราฟสรุปยอดขายรวม ปุ่ม Export รายงาน CSV และยืนยันความสมบูรณ์ของระบบแบบบูรณาการทั้ง 5 กระบวนการ",
        speaker_script="ทั้งหมดนี้คือ Smart CRM Analytics ที่ผสานทฤษฎีฐานข้อมูลเชิงสัมพันธ์ วิทยาศาสตร์ข้อมูล และซอฟต์แวร์ที่ทำงานได้จริง 100% ครับ",
        img_filename="5_2_sales_report.png"
    )

    out_pptx = os.path.join(ROOT_DEV, "docs", "demo.pptx")
    prs.save(out_pptx)
    print(f"✅ Successfully created dedicated Demo Deck: {out_pptx} (17 slides)!")


if __name__ == "__main__":
    create_demo_deck()
