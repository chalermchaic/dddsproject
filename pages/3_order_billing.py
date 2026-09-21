from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import auth
from db.connection import cached_query, execute, next_id, run_query

emp = auth.guard("admin", "sales")
auth.breadcrumb("ใบเสนอราคา/ชำระเงิน")
st.title("🧾 คำสั่งซื้อและการชำระเงิน")
st.caption(f"ผู้ใช้งาน: {emp['name']} ({emp['username']}) · Process 3.0")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 ออกใบเสนอราคา (2.3)", "📥 รับ & ตรวจคำสั่งซื้อ (3.1)",
    "💳 ตรวจสอบการชำระเงิน (3.2)", "🧾 ออกใบเสร็จ + บันทึกลูกค้า (3.3)",
    "📚 ประวัติการขาย"])


def _items(sid):
    return run_query("""SELECT p.Product_Name AS สินค้า, d.Quantity AS จำนวน,
                               d.Unit_Price AS ราคาต่อหน่วย, d.Subtotal AS รวม
                        FROM SALE_DETAIL d JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                        WHERE d.Sale_ID=?""", (sid,))


# ---------------- 2.3 ออกใบเสนอราคา ----------------
with tab1:
    leads = run_query("""
        SELECT l.Lead_ID, l.Full_Name, COALESCE(c.Discount_Rate,0) AS Disc,
               COALESCE(c.Campaign_Name,'ไม่ระบุ') AS Camp
        FROM LEAD l LEFT JOIN CAMPAIGN c ON c.Campaign_ID=l.Campaign_ID
        WHERE l.Followup_Status IN ('อยู่ระหว่างเสนอขาย','รอการติดต่อ')
        ORDER BY l.Created_At DESC LIMIT 300""")
    products = run_query("SELECT * FROM PRODUCT ORDER BY Product_Category, Product_Name")

    if leads.empty:
        st.warning("ไม่มีผู้สนใจให้เลือก")
    else:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            sel = st.selectbox("เลือกผู้สนใจ", leads.Lead_ID + " — " + leads.Full_Name)
            row = leads[leads.Lead_ID == sel.split(" — ")[0]].iloc[0]
            st.caption(f"แคมเปญ: **{row.Camp}** · ส่วนลดอัตโนมัติ **{row.Disc:.0f}%**")

            pmap = products.set_index("Product_ID")
            chosen = st.multiselect(
                "รายการสินค้า", options=products.Product_ID.tolist(),
                format_func=lambda pid: f"{pid} · {pmap.loc[pid,'Product_Name']} "
                                        f"(฿{pmap.loc[pid,'Unit_Price']:,.0f})")
            items, total = [], 0.0
            for pid in chosen:
                c1, c2, c3 = st.columns([3, 1, 2])
                c1.write(f"**{pmap.loc[pid,'Product_Name']}**")
                qty = c2.number_input("จำนวน", 1, 99, 1, key=f"q_{pid}")
                unit = round(float(pmap.loc[pid, "Unit_Price"]) * (1 - row.Disc / 100), 2)
                sub = round(unit * qty, 2)
                c3.write(f"฿{unit:,.2f} × {qty} = **฿{sub:,.2f}**")
                items.append((pid, qty, unit, sub))
                total += sub

            if chosen:
                st.success(f"### ยอดรวมสุทธิ: ฿{total:,.2f}")
                qdate = st.date_input("วันที่ออกใบเสนอราคา", value=date.today())
                if st.button("🧾 ออกใบเสนอราคา", type="primary", use_container_width=True):
                    sid = next_id("SALE", "Sale_ID", "SL", 4)
                    no = sid[2:]
                    execute("INSERT INTO SALE VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (sid, row.Lead_ID, emp["employee_id"], f"QT-{qdate.year}-{no}",
                             str(qdate), round(total, 2), "ออกใบเสนอราคาแล้ว",
                             None, None, None, None, None))
                    for pid, q, u, s in items:
                        execute("INSERT INTO SALE_DETAIL VALUES (?,?,?,?,?)", (sid, pid, q, u, s))
                    execute("UPDATE LEAD SET Followup_Status='อยู่ระหว่างเสนอขาย' "
                            "WHERE Lead_ID=? AND Followup_Status='รอการติดต่อ'", (row.Lead_ID,))
                    st.cache_data.clear()
                    st.success(f"✅ ออกใบเสนอราคา {sid} (QT-{qdate.year}-{no}) เรียบร้อย")


# ---------------- 3.1 รับ & ตรวจคำสั่งซื้อ ----------------
with tab2:
    st.caption("ผู้สนใจยืนยันคำสั่งซื้อผ่าน Portal แล้วสถานะจะมาที่ "
               "**'รอตรวจสอบคำสั่งซื้อ'** ให้ทีมขายตรวจความถูกต้อง")
    q = run_query("""SELECT s.Sale_ID, s.Quotation_No, s.Total_Amount, s.Sale_Status,
                            s.Order_Confirmed_At, l.Full_Name
                     FROM SALE s JOIN LEAD l ON l.Lead_ID=s.Lead_ID
                     WHERE s.Sale_Status IN ('ออกใบเสนอราคาแล้ว','รอตรวจสอบคำสั่งซื้อ')
                     ORDER BY s.Quotation_Date DESC""")
    if q.empty:
        st.info("ไม่มีใบเสนอราคา/คำสั่งซื้อที่รอตรวจ")
    for r in q.itertuples():
        confirmed = r.Sale_Status == "รอตรวจสอบคำสั่งซื้อ"
        head = (f"{r.Quotation_No} · {r.Full_Name} · ฿{r.Total_Amount:,.2f}"
                + (" · 📥 ลูกค้ายืนยันแล้ว" if confirmed else " · ⏳ ยังไม่ยืนยัน"))
        with st.expander(head, expanded=confirmed):
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.dataframe(_items(r.Sale_ID), hide_index=True, use_container_width=True)
                c1, c2 = st.columns(2)
                if not confirmed and c1.button("บันทึกคำสั่งซื้อแทนลูกค้า",
                                               key=f"mkord_{r.Sale_ID}"):
                    execute("""UPDATE SALE SET Sale_Status='รอตรวจสอบคำสั่งซื้อ',
                               Order_Confirmed_At=datetime('now','localtime')
                               WHERE Sale_ID=?""", (r.Sale_ID,))
                    st.cache_data.clear(); st.rerun()
                if confirmed and c1.button("✅ ตรวจแล้วถูกต้อง — ส่งต่อขั้นชำระเงิน",
                                           key=f"okord_{r.Sale_ID}", type="primary"):
                    execute("UPDATE SALE SET Sale_Status='รอการตรวจสอบชำระเงิน' WHERE Sale_ID=?",
                            (r.Sale_ID,))
                    st.cache_data.clear()
                    st.success(f"คำสั่งซื้อ {r.Sale_ID} ผ่านการตรวจ")
                    st.rerun()


# ---------------- 3.2 ตรวจสอบการชำระเงิน ----------------
with tab3:
    st.caption("ตรวจสลิปที่ลูกค้าอัปโหลด แล้วบันทึกการรับเงิน")
    pend = run_query("""SELECT s.Sale_ID, s.Quotation_No, s.Total_Amount, s.Payment_Slip,
                               s.Lead_ID, l.Full_Name
                        FROM SALE s JOIN LEAD l ON l.Lead_ID=s.Lead_ID
                        WHERE s.Sale_Status='รอการตรวจสอบชำระเงิน' AND s.Confirmed_At IS NULL
                        ORDER BY s.Quotation_Date DESC""")
    if pend.empty:
        st.info("ไม่มีรายการรอตรวจชำระเงิน")
    for r in pend.itertuples():
        with st.expander(f"{r.Quotation_No} · {r.Full_Name} · ฿{r.Total_Amount:,.2f}",
                         expanded=True):
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.dataframe(_items(r.Sale_ID), hide_index=True, use_container_width=True)
                if r.Payment_Slip:
                    st.success(f"📎 สลิปที่ได้รับ: `{r.Payment_Slip}`")
                    try:
                        st.image(f"uploads/{r.Payment_Slip}", width=280)
                    except Exception:
                        pass
                else:
                    st.warning("ยังไม่ได้รับสลิปจากลูกค้า")
                with st.form(f"pay_{r.Sale_ID}"):
                    ref = st.text_input("เลขอ้างอิงการโอน *", placeholder="TRF123456")
                    cdate = st.date_input("วันที่ได้รับเงิน", value=date.today())
                    if st.form_submit_button("💰 ยืนยันรับเงิน", type="primary"):
                        if not ref.strip():
                            st.error("กรุณากรอกเลขอ้างอิง")
                        else:
                            execute("""UPDATE SALE SET Payment_Ref=?, Invoice_No=?, Confirmed_At=?
                                       WHERE Sale_ID=?""",
                                    (ref.strip(), f"INV-{cdate.year}-{r.Sale_ID[2:]}",
                                     f"{cdate} 12:00:00", r.Sale_ID))
                            st.cache_data.clear()
                            st.success("บันทึกการรับเงินแล้ว — ไปออกใบเสร็จที่แท็บถัดไป")
                            st.rerun()


# ---------------- 3.3 ออกใบเสร็จ + บันทึกลูกค้า ----------------
with tab4:
    ready = run_query("""SELECT s.Sale_ID, s.Quotation_No, s.Invoice_No, s.Total_Amount,
                                s.Confirmed_At, s.Lead_ID, l.Full_Name,
                                (SELECT Customer_ID FROM CUSTOMER WHERE Lead_ID=s.Lead_ID) AS Cust
                         FROM SALE s JOIN LEAD l ON l.Lead_ID=s.Lead_ID
                         WHERE s.Sale_Status='รอการตรวจสอบชำระเงิน'
                               AND s.Confirmed_At IS NOT NULL
                         ORDER BY s.Confirmed_At DESC""")
    if ready.empty:
        st.info("ไม่มีรายการรอออกใบเสร็จ")
    for r in ready.itertuples():
        with st.expander(f"{r.Invoice_No} · {r.Full_Name} · ฿{r.Total_Amount:,.2f}",
                         expanded=True):
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                items = _items(r.Sale_ID)
                st.dataframe(items, hide_index=True, use_container_width=True)
                need_cust = pd.isna(r.Cust)
                with st.form(f"rc_{r.Sale_ID}"):
                    mk = st.checkbox("สร้างเป็นลูกค้าในระบบ", value=bool(need_cust),
                                     disabled=not need_cust)
                    ctype = st.radio("ประเภทลูกค้า", ["ทั่วไป", "องค์กร / VIP"], horizontal=True)
                    company = st.text_input("ชื่อบริษัท",
                                            value=f"บจก.{r.Full_Name.split()[0]} เทรดดิ้ง")
                    addr = st.text_area("ที่อยู่วางบิล/จัดส่ง", height=60)
                    if st.form_submit_button("🧾 ออกใบเสร็จ & ปิดการขาย", type="primary"):
                        execute("UPDATE SALE SET Sale_Status='ปิดการขายสำเร็จ' WHERE Sale_ID=?",
                                (r.Sale_ID,))
                        execute("UPDATE LEAD SET Followup_Status='ปิดการขายสำเร็จ' WHERE Lead_ID=?",
                                (r.Lead_ID,))
                        if mk and need_cust:
                            cid = next_id("CUSTOMER", "Customer_ID", "CU", 4)
                            execute("INSERT INTO CUSTOMER VALUES (?,?,?,?,?,?,?,?)",
                                    (cid, r.Lead_ID, company, None, addr, addr, ctype,
                                     str(date.today())))
                            st.info(f"สร้างลูกค้าใหม่: {cid}")
                        st.cache_data.clear()
                        st.success(f"✅ ปิดการขาย {r.Sale_ID} เรียบร้อย")
                rows = "".join(
                    f"<tr><td>{pn}</td><td align=right>{qy}</td>"
                    f"<td align=right>{up:,.2f}</td><td align=right>{sb:,.2f}</td></tr>"
                    for pn, qy, up, sb in items.itertuples(index=False, name=None))
                html = (f"<h2>ใบเสร็จรับเงิน</h2><p>เลขที่ {r.Invoice_No} · {r.Confirmed_At}"
                        f"<br>ลูกค้า: {r.Full_Name}</p>"
                        f"<table border=1 cellpadding=6 style='border-collapse:collapse'>"
                        f"<tr><th>รายการ</th><th>จำนวน</th><th>ราคา/หน่วย</th><th>รวม</th></tr>"
                        f"{rows}<tr><th colspan=3 align=right>ยอดสุทธิ</th>"
                        f"<th align=right>{r.Total_Amount:,.2f}</th></tr></table>")
                st.download_button("⬇️ ดาวน์โหลดใบเสร็จ (HTML)", html,
                                   file_name=f"receipt_{r.Invoice_No}.html",
                                   mime="text/html", key=f"dl_{r.Sale_ID}")


# ---------------- ประวัติ ----------------
with tab5:
    my_sales_label = f"เฉพาะยอดขายของฉัน ({emp['name']})"
    view_sales_mode = st.radio("มุมมองข้อมูลการขาย", ["รายการขายทั้งหมด", my_sales_label], horizontal=True)
    is_my_sales = (view_sales_mode == my_sales_label)

    where_filter = "s.Sale_Status='ปิดการขายสำเร็จ'"
    if is_my_sales:
        where_filter += f" AND s.Employee_ID='{emp['employee_id']}'"

    my_summary = run_query(f"""
        SELECT COUNT(*) AS total_bills,
               COALESCE(SUM(Total_Amount), 0) AS total_revenue
        FROM SALE s WHERE {where_filter}
    """).iloc[0]

    sm1, sm2 = st.columns(2)
    sm1.metric("จำนวนบิลที่ปิดสำเร็จ", f"{int(my_summary.total_bills):,} บิล")
    sm2.metric("ยอดขายสุทธิ", f"฿{my_summary.total_revenue:,.2f}")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.subheader("ยอดขายรายเดือน")
            d = cached_query(f"""SELECT strftime('%Y-%m',Confirmed_At) AS เดือน,
                                        SUM(Total_Amount) AS ยอดขาย
                                 FROM SALE s WHERE {where_filter}
                                 GROUP BY เดือน ORDER BY เดือน""")
            if not d.empty:
                st.plotly_chart(px.bar(d, x="เดือน", y="ยอดขาย",
                                       color_discrete_sequence=["#2E7D32"]).update_layout(
                                           plot_bgcolor="white", paper_bgcolor="white"),
                                use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลยอดขายในมุมมองนี้")
    with c2:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.subheader("สินค้าขายดี (ตามรายได้)")
            d = cached_query(f"""SELECT p.Product_Name AS สินค้า, SUM(d.Subtotal) AS รายได้
                                 FROM SALE_DETAIL d
                                 JOIN SALE s ON s.Sale_ID=d.Sale_ID AND {where_filter}
                                 JOIN PRODUCT p ON p.Product_ID=d.Product_ID
                                 GROUP BY p.Product_ID ORDER BY รายได้ DESC""")
            if not d.empty:
                st.plotly_chart(px.bar(d.head(8), x="รายได้", y="สินค้า", orientation="h",
                                       color="รายได้", color_continuous_scale="Greens")
                                .update_layout(plot_bgcolor="white", paper_bgcolor="white"),
                                use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลสินค้าที่ขาย")

    q_sales = f"""
        SELECT s.Sale_ID AS รหัส, s.Invoice_No AS เลขที่ใบแจ้งหนี้,
               l.Full_Name AS ลูกค้า, e.Employee_Name AS พนักงานขาย,
               s.Total_Amount AS ยอดรวม, s.Sale_Status AS สถานะ, s.Confirmed_At AS ยืนยันเมื่อ
        FROM SALE s 
        JOIN LEAD l ON l.Lead_ID=s.Lead_ID
        JOIN EMPLOYEE e ON e.Employee_ID=s.Employee_ID
        {"WHERE s.Employee_ID='" + emp["employee_id"] + "'" if is_my_sales else ""}
        ORDER BY s.Quotation_Date DESC LIMIT 300
    """
    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.subheader("ตารางรายการขาย")
        st.dataframe(run_query(q_sales),
            use_container_width=True, hide_index=True, height=350,
            column_config={"ยอดรวม": st.column_config.NumberColumn(format="฿%.2f")})
