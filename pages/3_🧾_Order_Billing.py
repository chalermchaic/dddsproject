from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from db.connection import cached_query, execute, next_id, run_query

st.set_page_config(page_title="Order & Billing", page_icon="🧾", layout="wide")
st.title("🧾 ใบเสนอราคาและการชำระเงิน")

tab1, tab2, tab3 = st.tabs(["📝 ออกใบเสนอราคา", "💳 ยืนยันการชำระเงิน", "📚 ประวัติการขาย"])

# ---------------- แท็บ 1: ออกใบเสนอราคา ----------------
with tab1:
    leads = run_query("""
        SELECT l.Lead_ID, l.Full_Name, COALESCE(c.Discount_Rate,0) AS Disc,
               COALESCE(c.Campaign_Name,'ไม่ระบุ') AS Camp
        FROM LEAD l LEFT JOIN CAMPAIGN c ON c.Campaign_ID=l.Campaign_ID
        WHERE l.Followup_Status IN ('อยู่ระหว่างเสนอขาย','รอการติดต่อ','ปิดการขายสำเร็จ')
        ORDER BY l.Created_At DESC LIMIT 300""")
    products = run_query("SELECT * FROM PRODUCT ORDER BY Product_Category, Product_Name")

    if leads.empty:
        st.warning("ไม่มีผู้สนใจให้เลือก")
        st.stop()

    sel = st.selectbox("เลือกผู้สนใจ", leads.Lead_ID + " — " + leads.Full_Name)
    row = leads[leads.Lead_ID == sel.split(" — ")[0]].iloc[0]
    st.caption(f"แคมเปญ: **{row.Camp}** · ส่วนลดอัตโนมัติ **{row.Disc:.0f}%**")

    st.markdown("#### เลือกสินค้า/บริการ")
    chosen = st.multiselect(
        "รายการสินค้า",
        options=products.Product_ID.tolist(),
        format_func=lambda pid: (
            f"{pid} · {products.set_index('Product_ID').loc[pid,'Product_Name']} "
            f"(฿{products.set_index('Product_ID').loc[pid,'Unit_Price']:,.0f})"))

    items, total = [], 0.0
    if chosen:
        pmap = products.set_index("Product_ID")
        for pid in chosen:
            c1, c2, c3 = st.columns([3, 1, 2])
            c1.write(f"**{pmap.loc[pid,'Product_Name']}**")
            qty = c2.number_input("จำนวน", 1, 99, 1, key=f"q_{pid}")
            unit = round(float(pmap.loc[pid, "Unit_Price"]) * (1 - row.Disc / 100), 2)
            sub = round(unit * qty, 2)
            c3.write(f"฿{unit:,.2f} × {qty} = **฿{sub:,.2f}**")
            items.append((pid, qty, unit, sub))
            total += sub

        st.success(f"### ยอดรวมสุทธิ: ฿{total:,.2f}")
        qdate = st.date_input("วันที่ออกใบเสนอราคา", value=date.today())

        if st.button("🧾 ออกใบเสนอราคา", type="primary", use_container_width=True):
            sid = next_id("SALE", "Sale_ID", "SL", 4)
            no = sid[2:]
            execute("""INSERT INTO SALE VALUES (?,?,?,?,?,?,?,?,?)""",
                    (sid, row.Lead_ID, f"QT-{qdate.year}-{no}", str(qdate),
                     round(total, 2), "ออกใบเสนอราคาแล้ว", None, None, None))
            execute_rows = [(sid, pid, q, u, s) for pid, q, u, s in items]
            for r in execute_rows:
                execute("INSERT INTO SALE_DETAIL VALUES (?,?,?,?,?)", r)
            execute("UPDATE LEAD SET Followup_Status='อยู่ระหว่างเสนอขาย' "
                    "WHERE Lead_ID=? AND Followup_Status='รอการติดต่อ'", (row.Lead_ID,))
            st.cache_data.clear()
            st.success(f"✅ ออกใบเสนอราคา {sid} (QT-{qdate.year}-{no}) เรียบร้อย")

# ---------------- แท็บ 2: ยืนยันชำระเงิน ----------------
with tab2:
    pend = run_query("""
        SELECT s.Sale_ID, s.Quotation_No, s.Quotation_Date, s.Total_Amount,
               s.Sale_Status, l.Lead_ID, l.Full_Name
        FROM SALE s JOIN LEAD l ON l.Lead_ID=s.Lead_ID
        WHERE s.Sale_Status <> 'ปิดการขายสำเร็จ'
        ORDER BY s.Quotation_Date DESC""")

    c1, c2 = st.columns(2)
    c1.metric("ใบเสนอราคาค้างอยู่", len(pend))
    c2.metric("มูลค่ารวมที่รอปิด", f"฿{pend.Total_Amount.sum():,.0f}" if len(pend) else "฿0")

    if pend.empty:
        st.info("ไม่มีรายการค้างชำระ")
    else:
        st.dataframe(pend.rename(columns={
            "Sale_ID": "รหัส", "Quotation_No": "เลขที่ใบเสนอราคา",
            "Quotation_Date": "วันที่", "Total_Amount": "ยอดรวม",
            "Sale_Status": "สถานะ", "Full_Name": "ลูกค้า"}),
            use_container_width=True, hide_index=True, height=250,
            column_config={"ยอดรวม": st.column_config.NumberColumn(format="฿%.2f")})

        pick = st.selectbox("เลือกรายการเพื่อยืนยัน",
                            pend.Sale_ID + " — " + pend.Full_Name +
                            " (฿" + pend.Total_Amount.map("{:,.0f}".format) + ")")
        sid = pick.split(" — ")[0]
        srow = pend[pend.Sale_ID == sid].iloc[0]

        det = run_query("""SELECT p.Product_Name AS สินค้า, d.Quantity AS จำนวน,
                                  d.Unit_Price AS 'ราคา/หน่วย', d.Subtotal AS รวม
                           FROM SALE_DETAIL d JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                           WHERE d.Sale_ID=?""", (sid,))
        st.dataframe(det, use_container_width=True, hide_index=True)

        with st.form("pay"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("เลขอ้างอิงการชำระเงิน *", placeholder="TRF123456")
            cdate = c2.date_input("วันที่ยืนยัน", value=date.today())
            mk_cust = st.checkbox("สร้างเป็นลูกค้าในระบบ (ถ้ายังไม่มี)", value=True)
            ctype = st.radio("ประเภทลูกค้า", ["ทั่วไป", "องค์กร / VIP"], horizontal=True)
            company = st.text_input("ชื่อบริษัท", value=f"บจก.{srow.Full_Name.split()[0]} เทรดดิ้ง")
            addr = st.text_area("ที่อยู่จัดส่ง/วางบิล", height=70)

            if st.form_submit_button("✅ ยืนยันการชำระเงิน", type="primary",
                                     use_container_width=True):
                if not ref.strip():
                    st.error("กรุณากรอกเลขอ้างอิงการชำระเงิน")
                else:
                    execute("""UPDATE SALE SET Sale_Status='ปิดการขายสำเร็จ',
                               Invoice_No=?, Payment_Ref=?, Confirmed_At=?
                               WHERE Sale_ID=?""",
                            (f"INV-{cdate.year}-{sid[2:]}", ref.strip(),
                             f"{cdate} 12:00:00", sid))
                    execute("UPDATE LEAD SET Followup_Status='ปิดการขายสำเร็จ' "
                            "WHERE Lead_ID=?", (srow.Lead_ID,))
                    exists = run_query("SELECT 1 FROM CUSTOMER WHERE Lead_ID=?",
                                       (srow.Lead_ID,))
                    if mk_cust and exists.empty:
                        cid = next_id("CUSTOMER", "Customer_ID", "CU", 4)
                        execute("INSERT INTO CUSTOMER VALUES (?,?,?,?,?,?,?,?)",
                                (cid, srow.Lead_ID, company, None, addr, addr,
                                 ctype, str(cdate)))
                        st.info(f"สร้างลูกค้าใหม่: {cid}")
                    st.cache_data.clear()
                    st.success(f"✅ ปิดการขาย {sid} เรียบร้อย")

# ---------------- แท็บ 3: ประวัติ ----------------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ยอดขายรายเดือน")
        d = cached_query("""SELECT strftime('%Y-%m',Confirmed_At) AS เดือน,
                                   COUNT(*) AS ออเดอร์, SUM(Total_Amount) AS ยอดขาย
                            FROM SALE WHERE Sale_Status='ปิดการขายสำเร็จ'
                            GROUP BY เดือน ORDER BY เดือน""")
        st.plotly_chart(px.bar(d, x="เดือน", y="ยอดขาย",
                               color_discrete_sequence=["#2E7D32"]),
                        use_container_width=True)
    with c2:
        st.subheader("สินค้าขายดี (ตามรายได้)")
        d = cached_query("""SELECT p.Product_Name AS สินค้า,
                                   SUM(d.Quantity) AS จำนวน, SUM(d.Subtotal) AS รายได้
                            FROM SALE_DETAIL d
                            JOIN SALE s ON s.Sale_ID=d.Sale_ID
                                       AND s.Sale_Status='ปิดการขายสำเร็จ'
                            JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                            GROUP BY p.Product_ID ORDER BY รายได้ DESC""")
        st.plotly_chart(px.bar(d.head(8), x="รายได้", y="สินค้า", orientation="h",
                               color="รายได้", color_continuous_scale="Greens"),
                        use_container_width=True)

    st.subheader("รายการขายทั้งหมด")
    st.dataframe(cached_query("""
        SELECT s.Sale_ID AS รหัส, s.Invoice_No AS เลขที่ใบแจ้งหนี้,
               l.Full_Name AS ลูกค้า, s.Total_Amount AS ยอดรวม,
               s.Sale_Status AS สถานะ, s.Confirmed_At AS ยืนยันเมื่อ
        FROM SALE s JOIN LEAD l ON l.Lead_ID=s.Lead_ID
        ORDER BY s.Quotation_Date DESC LIMIT 300"""),
        use_container_width=True, hide_index=True, height=350,
        column_config={"ยอดรวม": st.column_config.NumberColumn(format="฿%.2f")})