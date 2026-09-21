"""
Portal จำลอง — สวมบทเป็น "ผู้สนใจ / ลูกค้า" (external entity ใน DFD)
ทดลอง flow ที่ส่งข้อมูล *เข้า* ระบบ: ลงทะเบียน (1.2), ยืนยันคำสั่งซื้อ (3.1),
อัปโหลดสลิป (3.2), แจ้งปัญหา (4.1), ให้คะแนนบริการ (4.3)
"""
from datetime import date, datetime

import pandas as pd
import streamlit as st

import auth
from db.connection import execute, next_id, run_query, save_upload

auth.guard("guest")
auth.breadcrumb("Portal ผู้สนใจ/ลูกค้า")
st.title("🌐 Portal ผู้สนใจ / ลูกค้า")
st.caption("หน้านี้จำลองมุมของบุคคลภายนอก (Lead / Customer) ตาม Context DFD")

CHANNELS = ["Facebook", "Line", "Google", "Direct"]
CATS = ["ระบบขัดข้อง", "สินค้าชำรุด", "ขอข้อมูลเพิ่ม"]
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------- เลือกตัวตน ----------
leads = run_query("""
    SELECT l.Lead_ID, l.Full_Name, l.Followup_Status, c.Customer_ID
    FROM LEAD l LEFT JOIN CUSTOMER c ON c.Lead_ID = l.Lead_ID
    ORDER BY l.Created_At DESC LIMIT 400""")
opts = ["— ยังไม่เลือก —"] + [f"{r.Lead_ID} — {r.Full_Name}" for r in leads.itertuples()]
pick = st.selectbox("เลือกตัวตนของคุณ (Lead)", opts,
                    index=st.session_state.get("portal_idx", 0))
me = None if pick.startswith("—") else leads[leads.Lead_ID == pick.split(" — ")[0]].iloc[0]
if me is not None:
    st.session_state["portal_idx"] = opts.index(pick)
    tag = f"ลูกค้า {me.Customer_ID}" if pd.notna(me.Customer_ID) else "ยังเป็นผู้สนใจ"
    st.info(f"คุณคือ **{me.Full_Name}** ({me.Lead_ID}) · {tag}")

t1, t2, t3, t4, t5 = st.tabs([
    "① ลงทะเบียนความสนใจ", "② โปรโมชัน & ใบเสนอราคา",
    "③ ยืนยันคำสั่งซื้อ", "④ อัปโหลดสลิป", "⑤ ใบเสร็จ · แจ้งปัญหา · ให้คะแนน"])

# ============ 1.2 ลงทะเบียนความสนใจเอง ============
with t1:
    st.markdown("**Process 1.2** — ผู้สนใจส่ง *ข้อมูลการติดต่อ* เข้าระบบเอง")
    camps = run_query("SELECT Campaign_ID, Campaign_Name FROM CAMPAIGN "
                      "WHERE Campaign_Status='เปิดใช้งานอยู่' ORDER BY Start_Date DESC")
    cmap = {f"{r.Campaign_ID} — {r.Campaign_Name}": r.Campaign_ID for r in camps.itertuples()}
    with st.form("portal_reg", clear_on_submit=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        full = c1.text_input("ชื่อ-นามสกุล *")
        tel = c2.text_input("เบอร์โทรศัพท์ *", max_chars=20)
        c3, c4 = st.columns(2)
        email = c3.text_input("อีเมล")
        channel = c4.selectbox("รู้จักเราจากช่องทาง", CHANNELS)
        camp = st.selectbox("แคมเปญที่สนใจ", ["— ไม่ระบุ —"] + list(cmap))
        if st.form_submit_button("📨 ส่งข้อมูลการติดต่อ", type="primary",
                                 use_container_width=True):
            if not full.strip() or not tel.strip():
                st.error("กรุณากรอกชื่อและเบอร์โทรศัพท์")
            else:
                lid = next_id("LEAD", "Lead_ID", "LD", 4)
                execute("""INSERT INTO LEAD (Lead_ID, Full_Name, Telephone, Email,
                           Source_Channel, Campaign_ID, Followup_Status)
                           VALUES (?,?,?,?,?,?, 'รอการติดต่อ')""",
                        (lid, full.strip(), tel.strip(), email or None, channel,
                         cmap.get(camp)))
                st.cache_data.clear()
                st.success(f"✅ ลงทะเบียนแล้ว — รหัสผู้สนใจของคุณคือ {lid} "
                           "(ทีมขายจะติดต่อกลับ)")

# ============ 1.3 / 2.3 (ขารับ) ============
with t2:
    if me is None:
        st.warning("เลือกตัวตนของคุณด้านบนก่อน")
    else:
        st.markdown("**Process 1.3** — รายละเอียดสินค้า/โปรโมชันที่ได้รับ")
        promo = run_query("""SELECT c.Campaign_Name, c.Discount_Rate, c.Promotion_Details
                             FROM LEAD l JOIN CAMPAIGN c ON c.Campaign_ID=l.Campaign_ID
                             WHERE l.Lead_ID=?""", (me.Lead_ID,))
        if promo.empty:
            st.caption("— ไม่ได้มาจากแคมเปญ —")
        else:
            p = promo.iloc[0]
            st.success(f"🎁 {p.Campaign_Name} · ส่วนลด {p.Discount_Rate:.0f}%\n\n"
                       f"{p.Promotion_Details or ''}")
        acts = run_query("""SELECT Activity_Date, Notes FROM LEAD_ACTIVITY
                            WHERE Lead_ID=? AND Activity_Type='ส่งโปรโมชัน'
                            ORDER BY Activity_Date DESC""", (me.Lead_ID,))
        if not acts.empty:
            st.markdown("**ข้อเสนอที่ทีมขายส่งมาให้:**")
            for r in acts.itertuples():
                st.markdown(f"- _{r.Activity_Date[:10]}_ — {r.Notes}")

        st.divider()
        st.markdown("**Process 2.3** — ใบเสนอราคาที่ได้รับ")
        q = run_query("""SELECT Sale_ID, Quotation_No, Quotation_Date, Total_Amount, Sale_Status
                         FROM SALE WHERE Lead_ID=? ORDER BY Quotation_Date DESC""",
                      (me.Lead_ID,))
        if q.empty:
            st.caption("ยังไม่มีใบเสนอราคา")
        else:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.dataframe(q.rename(columns={
                    "Quotation_No": "เลขที่", "Quotation_Date": "วันที่",
                    "Total_Amount": "ยอดรวม", "Sale_Status": "สถานะ"}),
                    hide_index=True, use_container_width=True)

# ============ 3.1 ยืนยันคำสั่งซื้อ ============
with t3:
    st.markdown("**Process 3.1** — ผู้สนใจส่ง *คำสั่งซื้อ* (ยืนยันจากใบเสนอราคา)")
    if me is None:
        st.warning("เลือกตัวตนของคุณด้านบนก่อน")
    else:
        pend = run_query("""SELECT s.Sale_ID, s.Quotation_No, s.Total_Amount
                            FROM SALE s WHERE s.Lead_ID=? AND s.Sale_Status='ออกใบเสนอราคาแล้ว'
                            ORDER BY s.Quotation_Date DESC""", (me.Lead_ID,))
        if pend.empty:
            st.info("ไม่มีใบเสนอราคาที่รอการยืนยัน")
        for r in pend.itertuples():
            det = run_query("""SELECT p.Product_Name AS สินค้า, d.Quantity AS จำนวน,
                                      d.Subtotal AS รวม
                               FROM SALE_DETAIL d JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                               WHERE d.Sale_ID=?""", (r.Sale_ID,))
            with st.expander(f"{r.Quotation_No} · ฿{r.Total_Amount:,.2f}", expanded=True):
                with st.container(border=True):
                    st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                    st.dataframe(det, hide_index=True, use_container_width=True)
                    if st.button("✅ ยืนยันสั่งซื้อตามใบเสนอราคานี้", key=f"ord_{r.Sale_ID}",
                                 type="primary"):
                        execute("""UPDATE SALE SET Sale_Status='รอตรวจสอบคำสั่งซื้อ',
                                   Order_Confirmed_At=? WHERE Sale_ID=?""", (NOW, r.Sale_ID))
                        st.cache_data.clear()
                        st.success(f"ส่งคำสั่งซื้อ {r.Sale_ID} แล้ว — รอทีมขายตรวจสอบ")
                        st.rerun()

# ============ 3.2 อัปโหลดสลิป ============
with t4:
    st.markdown("**Process 3.2** — ผู้สนใจส่ง *หลักฐานการชำระเงิน* (สลิป)")
    if me is None:
        st.warning("เลือกตัวตนของคุณด้านบนก่อน")
    else:
        wait = run_query("""SELECT Sale_ID, Quotation_No, Total_Amount, Payment_Slip
                            FROM SALE
                            WHERE Lead_ID=? AND Sale_Status IN
                                  ('รอตรวจสอบคำสั่งซื้อ','รอการตรวจสอบชำระเงิน')
                            ORDER BY Quotation_Date DESC""", (me.Lead_ID,))
        if wait.empty:
            st.info("ไม่มีรายการที่รอชำระเงิน")
        for r in wait.itertuples():
            with st.expander(f"{r.Quotation_No} · ฿{r.Total_Amount:,.2f}"
                             + (" · ✅ ส่งสลิปแล้ว" if r.Payment_Slip else ""),
                             expanded=not r.Payment_Slip):
                with st.container(border=True):
                    st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                    up = st.file_uploader("แนบสลิปโอนเงิน (รูปภาพ/PDF)",
                                          type=["png", "jpg", "jpeg", "pdf"],
                                          key=f"slip_{r.Sale_ID}")
                    if up and st.button("📤 ส่งสลิป", key=f"sendslip_{r.Sale_ID}",
                                        type="primary"):
                        fname = save_upload(up, prefix=f"slip_{r.Sale_ID}")
                        execute("UPDATE SALE SET Payment_Slip=? WHERE Sale_ID=?",
                                (fname, r.Sale_ID))
                        st.cache_data.clear()
                        st.success("ส่งสลิปแล้ว — รอทีมขายตรวจสอบและออกใบเสร็จ")
                        st.rerun()

# ============ 3.3 (รับ) + 4.1 + 4.3 ============
with t5:
    if me is None:
        st.warning("เลือกตัวตนของคุณด้านบนก่อน")
    elif pd.isna(me.Customer_ID):
        st.warning("คุณยังไม่เป็นลูกค้าทางการ (ยังไม่มีการปิดการขาย) — "
                   "ทำ flow ③④ ให้ครบแล้วให้ทีมขายออกใบเสร็จก่อน")
    else:
        cid = me.Customer_ID
        st.markdown("**Process 3.3** — ใบเสร็จรับเงินที่ได้รับ")
        rec = run_query("""SELECT s.Sale_ID, s.Invoice_No, s.Confirmed_At, s.Total_Amount
                           FROM SALE s WHERE s.Lead_ID=? AND s.Sale_Status='ปิดการขายสำเร็จ'
                           ORDER BY s.Confirmed_At DESC""", (me.Lead_ID,))
        for r in rec.itertuples():
            items = run_query("""SELECT p.Product_Name, d.Quantity, d.Unit_Price, d.Subtotal
                                 FROM SALE_DETAIL d JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                                 WHERE d.Sale_ID=?""", (r.Sale_ID,))
            rows = "".join(
                f"<tr><td>{x.Product_Name}</td><td style='text-align:right'>{x.Quantity}</td>"
                f"<td style='text-align:right'>{x.Unit_Price:,.2f}</td>"
                f"<td style='text-align:right'>{x.Subtotal:,.2f}</td></tr>"
                for x in items.itertuples())
            html = f"""<h2>ใบเสร็จรับเงิน / RECEIPT</h2>
<p>เลขที่: {r.Invoice_No}<br>วันที่: {r.Confirmed_At}<br>ลูกค้า: {me.Full_Name} ({cid})</p>
<table border=1 cellpadding=6 style='border-collapse:collapse'>
<tr><th>รายการ</th><th>จำนวน</th><th>ราคา/หน่วย</th><th>รวม</th></tr>{rows}
<tr><th colspan=3 style='text-align:right'>ยอดสุทธิ</th>
<th style='text-align:right'>{r.Total_Amount:,.2f}</th></tr></table>"""
            with st.expander(f"ใบเสร็จ {r.Invoice_No} · ฿{r.Total_Amount:,.2f}"):
                with st.container(border=True):
                    st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                    st.markdown(html, unsafe_allow_html=True)
                    st.download_button("⬇️ ดาวน์โหลดใบเสร็จ (HTML)", html,
                                       file_name=f"receipt_{r.Invoice_No}.html",
                                       mime="text/html", key=f"rc_{r.Sale_ID}")

        st.divider()
        st.markdown("**Process 4.1** — แจ้งปัญหา")
        ps = run_query("SELECT Product_ID, Product_Name FROM PRODUCT")
        with st.form("portal_ticket", clear_on_submit=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            cat = st.selectbox("ประเภทปัญหา", CATS)
            prod = st.selectbox("สินค้าที่เกี่ยวข้อง", ["— ไม่ระบุ —"] +
                                (ps.Product_ID + " — " + ps.Product_Name).tolist())
            title = st.text_input("หัวข้อปัญหา *")
            detail = st.text_area("รายละเอียด", height=90)
            if st.form_submit_button("🎫 ส่งเรื่องแจ้งปัญหา", type="primary",
                                     use_container_width=True):
                if not title.strip():
                    st.error("กรุณากรอกหัวข้อปัญหา")
                else:
                    tid = next_id("TICKET", "Ticket_ID", "TK", 4)
                    execute("INSERT INTO TICKET VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (tid, cid,
                             None if prod.startswith("—") else prod.split(" — ")[0],
                             cat, title.strip(), "รอดำเนินการ", None, NOW, None, None, None))
                    if detail.strip():
                        mid = next_id("TICKET_MESSAGE", "Message_ID", "MSG", 5)
                        execute("""INSERT INTO TICKET_MESSAGE (Message_ID,Ticket_ID,
                                   Sender_Type,Sender_Name,Message_Text,Sent_At)
                                   VALUES (?,?,?,?,?,?)""",
                                (mid, tid, "Customer", me.Full_Name, detail.strip(), NOW))
                    st.cache_data.clear()
                    st.success(f"✅ ส่งเรื่องแล้ว — เลขที่เคส {tid}")

        st.divider()
        st.markdown("**Process 4.3** — ติดตามสถานะ & ให้คะแนนบริการ + "
                    "ประวัติการสั่งซื้อและรับบริการ")
        tks = run_query("""SELECT Ticket_ID, Problem_Title, Ticket_Status,
                                  Service_Rating, Closed_At
                           FROM TICKET WHERE Customer_ID=? ORDER BY Created_At DESC""", (cid,))
        for r in tks.itertuples():
            box = st.container(border=True)
            box.markdown(f"**{r.Ticket_ID}** · {r.Problem_Title} — `{r.Ticket_Status}`")
            if r.Ticket_Status == "ปิดเคสสำเร็จ" and pd.isna(r.Service_Rating):
                with box.form(f"rate_{r.Ticket_ID}"):
                    score = st.slider("ให้คะแนนบริการ (1–5)", 1, 5, 5)
                    fb = st.text_input("ความเห็นเพิ่มเติม")
                    if st.form_submit_button("⭐ ส่งคะแนน", type="primary"):
                        execute("""UPDATE TICKET SET Service_Rating=?, Service_Feedback=?
                                   WHERE Ticket_ID=?""", (score, fb or None, r.Ticket_ID))
                        st.cache_data.clear()
                        st.success("ขอบคุณสำหรับคะแนน")
                        st.rerun()
            elif pd.notna(r.Service_Rating):
                box.caption(f"คุณให้ {int(r.Service_Rating)} ดาว")

        hist = run_query("""SELECT 'ซื้อ' AS ประเภท, s.Confirmed_At AS วันที่,
                                   s.Invoice_No AS อ้างอิง, s.Total_Amount AS ยอด
                            FROM SALE s WHERE s.Lead_ID=? AND s.Sale_Status='ปิดการขายสำเร็จ'
                            UNION ALL
                            SELECT 'แจ้งปัญหา', t.Created_At, t.Ticket_ID, NULL
                            FROM TICKET t WHERE t.Customer_ID=?
                            ORDER BY วันที่ DESC""", (me.Lead_ID, cid))
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.dataframe(hist, hide_index=True, use_container_width=True)
        st.download_button("⬇️ ดาวน์โหลดประวัติ (CSV)",
                           hist.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"history_{cid}.csv", mime="text/csv")
