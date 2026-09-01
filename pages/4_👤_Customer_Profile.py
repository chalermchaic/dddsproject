import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.rfm_segmentation import SEGMENT_COLOR, build_rfm
from db.connection import cached_query, run_query

st.set_page_config(page_title="Customer Profile", page_icon="👤", layout="wide")
st.title("👤 ข้อมูลลูกค้า")

cust = cached_query("""
    SELECT cu.Customer_ID, cu.Company_Name, cu.Customer_Type, cu.Membership_Date,
           cu.Billing_Address, cu.Tax_ID, l.Full_Name, l.Telephone, l.Email,
           l.Source_Channel
    FROM CUSTOMER cu JOIN LEAD l ON l.Lead_ID=cu.Lead_ID
    ORDER BY cu.Membership_Date DESC""")

if cust.empty:
    st.warning("ยังไม่มีลูกค้าในระบบ")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("ลูกค้าทั้งหมด", len(cust))
c2.metric("องค์กร / VIP", int((cust.Customer_Type == "องค์กร / VIP").sum()))
c3.metric("ทั่วไป", int((cust.Customer_Type == "ทั่วไป").sum()))

tab1, tab2 = st.tabs(["🔎 โปรไฟล์รายบุคคล", "📋 รายชื่อลูกค้าทั้งหมด"])

with tab1:
    sel = st.selectbox("เลือกลูกค้า",
                       cust.Customer_ID + " — " + cust.Company_Name.fillna("") +
                       " (" + cust.Full_Name + ")")
    cid = sel.split(" — ")[0]
    row = cust[cust.Customer_ID == cid].iloc[0]

    a, b = st.columns([1, 2])
    with a:
        st.markdown(f"""
        #### 🏢 {row.Company_Name or '—'}
        - **ผู้ติดต่อ:** {row.Full_Name}
        - **โทร:** {row.Telephone or '—'}
        - **อีเมล:** {row.Email or '—'}
        - **ประเภท:** {row.Customer_Type}
        - **เลขผู้เสียภาษี:** {row.Tax_ID or '—'}
        - **ช่องทางที่มา:** {row.Source_Channel}
        - **เป็นลูกค้าตั้งแต่:** {row.Membership_Date}
        """)
        st.caption(f"📍 {row.Billing_Address or '—'}")

    with b:
        rfm = build_rfm()
        me = rfm[rfm.Customer_ID == cid]
        if me.empty:
            st.info("ยังไม่มีคำสั่งซื้อที่ยืนยันแล้ว")
        else:
            r = me.iloc[0]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ซื้อล่าสุด (วัน)", int(r.Recency_Days))
            m2.metric("จำนวนครั้งที่ซื้อ", int(r.Frequency))
            m3.metric("มูลค่ารวม", f"฿{r.Monetary:,.0f}")
            m4.metric("กลุ่ม RFM", r.Segment)

            fig = go.Figure(go.Scatterpolar(
                r=[r.R_Score, r.F_Score, r.M_Score],
                theta=["Recency", "Frequency", "Monetary"],
                fill="toself", line_color=SEGMENT_COLOR.get(r.Segment, "#2E7D32")))
            fig.update_layout(height=280, margin=dict(t=30, b=10),
                              polar=dict(radialaxis=dict(range=[0, 5])),
                              showlegend=False, title="คะแนน RFM (1–5)")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 🛒 ประวัติการซื้อ")
        st.dataframe(run_query("""
            SELECT s.Invoice_No AS ใบแจ้งหนี้, s.Confirmed_At AS วันที่,
                   s.Total_Amount AS ยอด
            FROM SALE s JOIN CUSTOMER cu ON cu.Lead_ID=s.Lead_ID
            WHERE cu.Customer_ID=? AND s.Sale_Status='ปิดการขายสำเร็จ'
            ORDER BY s.Confirmed_At DESC""", (cid,)),
            use_container_width=True, hide_index=True,
            column_config={"ยอด": st.column_config.NumberColumn(format="฿%.2f")})
    with d2:
        st.markdown("#### 🎫 ประวัติแจ้งปัญหา")
        st.dataframe(run_query("""
            SELECT Ticket_ID AS รหัส, Problem_Category AS ประเภท,
                   Problem_Title AS หัวข้อ, Ticket_Status AS สถานะ,
                   Created_At AS แจ้งเมื่อ
            FROM TICKET WHERE Customer_ID=? ORDER BY Created_At DESC""", (cid,)),
            use_container_width=True, hide_index=True)

with tab2:
    kw = st.text_input("🔍 ค้นหาชื่อบริษัท / ผู้ติดต่อ")
    view = cust
    if kw:
        m = (cust.Company_Name.fillna("").str.contains(kw) |
             cust.Full_Name.str.contains(kw))
        view = cust[m]
    st.dataframe(view.rename(columns={
        "Customer_ID": "รหัส", "Company_Name": "บริษัท", "Full_Name": "ผู้ติดต่อ",
        "Customer_Type": "ประเภท", "Telephone": "โทร",
        "Membership_Date": "เป็นลูกค้าตั้งแต่"}),
        use_container_width=True, hide_index=True, height=430)
    st.download_button("⬇️ ดาวน์โหลดรายชื่อ (CSV)",
                       view.to_csv(index=False).encode("utf-8-sig"),
                       "customers.csv", "text/csv")