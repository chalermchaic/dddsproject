"""ภาพรวมระบบ — KPI + กราฟสรุป (หน้าแรกหลังเข้าสู่ระบบ)"""
import plotly.express as px
import streamlit as st

import auth
from db.connection import cached_query, table_counts

emp = auth.guard()

st.markdown("""
<style>
  .block-container {padding-top: 2rem;}
  div[data-testid="stMetricValue"] {font-size: 1.6rem;}
  .stTabs [data-baseweb="tab"] {font-size: 1rem;}
</style>
""", unsafe_allow_html=True)

st.title("📈 Smart CRM Analytics")
st.caption(f"สวัสดี {emp['name']} · {auth.ROLE_TH.get(emp['role'], emp['role'])} "
           "— ระบบบริหารความสัมพันธ์ลูกค้า พร้อมวิเคราะห์ข้อมูลด้วย Machine Learning")

# ================= KPI แถวบน =================
KPI_SQL = """
SELECT
 (SELECT COUNT(*) FROM LEAD)                                              AS leads,
 (SELECT COUNT(*) FROM LEAD WHERE Followup_Status='ปิดการขายสำเร็จ')       AS won,
 (SELECT COUNT(*) FROM LEAD
   WHERE Followup_Status IN ('รอการติดต่อ','อยู่ระหว่างเสนอขาย'))          AS open_leads,
 (SELECT COUNT(*) FROM CUSTOMER)                                          AS customers,
 (SELECT COALESCE(SUM(Total_Amount),0) FROM SALE
   WHERE Sale_Status='ปิดการขายสำเร็จ')                                    AS revenue,
 (SELECT COUNT(*) FROM TICKET WHERE Ticket_Status<>'ปิดเคสสำเร็จ')         AS open_tickets
"""
k = cached_query(KPI_SQL).iloc[0]
conv = 100 * k["won"] / k["leads"] if k["leads"] else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("👥 ผู้สนใจทั้งหมด", f"{k['leads']:,}", f"เปิดอยู่ {k['open_leads']:,} ราย")
c2.metric("🎯 อัตราปิดการขาย", f"{conv:.1f}%", f"สำเร็จ {k['won']:,} ราย")
c3.metric("🧑‍💼 ลูกค้าปัจจุบัน", f"{k['customers']:,}")
c4.metric("💰 รายได้รวม", f"฿{k['revenue']:,.0f}")
c5.metric("🎫 เคสค้าง", f"{k['open_tickets']:,}",
          delta="ต้องดำเนินการ" if k["open_tickets"] else "เคลียร์หมด",
          delta_color="inverse" if k["open_tickets"] else "normal")

st.divider()

# ================= กราฟภาพรวม =================
left, right = st.columns([3, 2])

with left:
    st.subheader("📅 แนวโน้มรายได้รายเดือน")
    trend = cached_query("""
        SELECT strftime('%Y-%m', Confirmed_At) AS Month,
               COUNT(*) AS Orders, SUM(Total_Amount) AS Revenue
        FROM SALE
        WHERE Sale_Status='ปิดการขายสำเร็จ' AND Confirmed_At IS NOT NULL
        GROUP BY Month ORDER BY Month
    """)
    if trend.empty:
        st.info("ยังไม่มีข้อมูลการขาย")
    else:
        fig = px.area(trend, x="Month", y="Revenue", markers=True,
                      labels={"Month": "เดือน", "Revenue": "รายได้ (บาท)"})
        fig.update_traces(line_color="#2E7D32", fillcolor="rgba(46,125,50,.15)")
        fig.update_layout(height=340, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("🔀 สถานะผู้สนใจ")
    status = cached_query("""
        SELECT Followup_Status AS Status, COUNT(*) AS N
        FROM LEAD GROUP BY Followup_Status
    """)
    fig = px.pie(status, names="Status", values="N", hole=.55,
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=340, margin=dict(t=10, b=10),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)

# ================= ช่องทาง + ตารางข้อมูล =================
a, b = st.columns(2)

with a:
    st.subheader("📡 ผลงานรายช่องทาง")
    ch = cached_query("""
        SELECT Source_Channel AS ช่องทาง, COUNT(*) AS ผู้สนใจ,
               SUM(CASE WHEN Followup_Status='ปิดการขายสำเร็จ' THEN 1 ELSE 0 END) AS ปิดได้
        FROM LEAD GROUP BY Source_Channel ORDER BY ผู้สนใจ DESC
    """)
    ch["อัตราแปลง %"] = (100 * ch["ปิดได้"] / ch["ผู้สนใจ"]).round(1)
    fig = px.bar(ch, x="ช่องทาง", y=["ผู้สนใจ", "ปิดได้"], barmode="group",
                 color_discrete_sequence=["#90CAF9", "#2E7D32"])
    fig.update_layout(height=300, margin=dict(t=10, b=10), yaxis_title="จำนวน")
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("🗄️ ปริมาณข้อมูลในระบบ")
    st.dataframe(table_counts().rename(columns={"table_name": "ตาราง", "n": "จำนวนแถว"}),
                 use_container_width=True, hide_index=True, height=300)

with st.sidebar:
    if st.button("🔄 ล้างแคชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.success("ล้างแคชแล้ว")
        st.rerun()
    st.caption("ฐานข้อมูล: SQLite · `db/crm.db`")
