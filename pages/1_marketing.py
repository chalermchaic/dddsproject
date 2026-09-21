import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import auth
from db.connection import cached_query, execute, next_id, run_query

emp = auth.guard("admin", "marketing")
auth.breadcrumb("งานการตลาด")
st.title("📢 งานการตลาด")
st.caption(f"ผู้ใช้งาน: {emp['name']} ({emp['username']})")

tab1, tab2, tab3 = st.tabs(["📋 แคมเปญทั้งหมด", "➕ สร้างแคมเปญ", "🙋 บันทึกผู้สนใจใหม่"])

# ---------------- แท็บ 1: รายการแคมเปญ ----------------
with tab1:
    raw_df = cached_query("""
        SELECT c.Campaign_ID, c.Campaign_Name AS ชื่อแคมเปญ,
               c.Budget_Cost AS งบประมาณ, c.Discount_Rate AS ส่วนลด,
               c.Start_Date AS เริ่ม, c.End_Date AS สิ้นสุด,
               c.Campaign_Status AS สถานะ,
               COALESCE(e.Employee_Name, 'ไม่ระบุ') AS ผู้รับผิดชอบ,
               c.Employee_ID,
               COUNT(l.Lead_ID) AS ผู้สนใจ,
               COALESCE(SUM(CASE WHEN l.Followup_Status='ปิดการขายสำเร็จ' THEN 1 ELSE 0 END), 0) AS ปิดได้
        FROM CAMPAIGN c
        LEFT JOIN EMPLOYEE e ON e.Employee_ID = c.Employee_ID
        LEFT JOIN LEAD l ON l.Campaign_ID = c.Campaign_ID
        GROUP BY c.Campaign_ID ORDER BY c.Start_Date DESC
    """)
    raw_df["ปิดได้"] = raw_df["ปิดได้"].fillna(0).astype(int)
    raw_df["ผู้สนใจ"] = raw_df["ผู้สนใจ"].fillna(0).astype(int)
    raw_df["งบประมาณ"] = raw_df["งบประมาณ"].fillna(0.0).astype(float)
    raw_df["อัตราแปลง %"] = np.where(
        raw_df["ผู้สนใจ"] > 0,
        (100.0 * raw_df["ปิดได้"] / raw_df["ผู้สนใจ"]).round(1),
        0.0,
    )
    raw_df["อัตราแปลง %"] = raw_df["อัตราแปลง %"].fillna(0.0).astype(float)
    raw_df["ต้นทุน/ผู้สนใจ"] = np.where(
        raw_df["ผู้สนใจ"] > 0,
        (raw_df["งบประมาณ"] / raw_df["ผู้สนใจ"]).round(0),
        np.nan,
    )

    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        my_opt_label = f"เฉพาะแคมเปญของฉัน ({emp['name']})"
        v_filter = st.radio("มุมมองข้อมูลแคมเปญ", ["แคมเปญทั้งหมด", my_opt_label], horizontal=True)

    if v_filter == my_opt_label:
        df = raw_df[raw_df["Employee_ID"] == emp["employee_id"]].copy()
    else:
        df = raw_df.copy()

    m1, m2, m3 = st.columns(3)
    m1.metric("แคมเปญในมุมมอง", len(df))
    m2.metric("กำลังดำเนินการ", int((df["สถานะ"] == "เปิดใช้งานอยู่").sum()) if not df.empty else 0)
    m3.metric("งบประมาณรวม", f"฿{df['งบประมาณ'].sum():,.0f}" if not df.empty else "฿0")

    display_cols = [c for c in df.columns if c != "Employee_ID"]
    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.dataframe(
            df[display_cols], use_container_width=True, hide_index=True,
            column_config={
                "งบประมาณ": st.column_config.NumberColumn(format="฿%.0f"),
                "ต้นทุน/ผู้สนใจ": st.column_config.NumberColumn(format="฿%.0f"),
                "อัตราแปลง %": st.column_config.ProgressColumn(
                    format="%.1f%%", min_value=0, max_value=100),
            })

    if not df.empty:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.subheader("เปรียบเทียบงบประมาณกับจำนวนผู้สนใจ")
            fig = px.scatter(df, x="งบประมาณ", y="ผู้สนใจ", size="ปิดได้",
                             color="อัตราแปลง %", hover_name="ชื่อแคมเปญ",
                             color_continuous_scale="Greens", size_max=45)
            fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ยังไม่มีแคมเปญที่คุณเป็นผู้รับผิดชอบ")

# ---------------- แท็บ 2: สร้างแคมเปญ ----------------
with tab2:
    with st.form("form_campaign", clear_on_submit=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        name = c1.text_input("ชื่อแคมเปญ *", placeholder="เช่น Year-End Mega Sale")
        status = c2.selectbox("สถานะ", ["เปิดใช้งานอยู่", "หมดอายุ"])
        detail = st.text_area("รายละเอียดโปรโมชัน", height=90)
        c3, c4, c5, c6 = st.columns(4)
        disc = c3.number_input("ส่วนลด (%)", 0.0, 100.0, 10.0, 0.5)
        budget = c4.number_input("งบประมาณ (บาท)", 0.0, step=10000.0, value=100000.0)
        sdate = c5.date_input("วันเริ่มต้น")
        edate = c6.date_input("วันสิ้นสุด")

        if st.form_submit_button("💾 บันทึกแคมเปญ", type="primary",
                                 use_container_width=True):
            if not name.strip():
                st.error("กรุณากรอกชื่อแคมเปญ")
            elif edate < sdate:
                st.error("วันสิ้นสุดต้องไม่ก่อนวันเริ่มต้น")
            else:
                cid = next_id("CAMPAIGN", "Campaign_ID", "CMP", 3)
                execute("INSERT INTO CAMPAIGN VALUES (?,?,?,?,?,?,?,?,?)",
                        (cid, name.strip(), detail, disc, budget,
                         str(sdate), str(edate), status, emp["employee_id"]))
                st.cache_data.clear()
                st.success(f"✅ สร้างแคมเปญ {cid} เรียบร้อย")

# ---------------- แท็บ 3: บันทึกผู้สนใจ ----------------
with tab3:
    camps = run_query(
        "SELECT Campaign_ID, Campaign_Name FROM CAMPAIGN ORDER BY Start_Date DESC")
    opts = {f"{r.Campaign_ID} — {r.Campaign_Name}": r.Campaign_ID
            for r in camps.itertuples()}

    with st.form("form_lead", clear_on_submit=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        full = c1.text_input("ชื่อ-นามสกุล *")
        tel = c2.text_input("เบอร์โทรศัพท์", max_chars=20)
        c3, c4 = st.columns(2)
        email = c3.text_input("อีเมล")
        channel = c4.selectbox("ช่องทางที่มา", ["Facebook", "Line", "Google", "Direct"])
        camp = st.selectbox("แคมเปญที่เกี่ยวข้อง", ["— ไม่ระบุ —"] + list(opts))

        if st.form_submit_button("💾 บันทึกผู้สนใจ", type="primary",
                                 use_container_width=True):
            if not full.strip():
                st.error("กรุณากรอกชื่อ-นามสกุล")
            else:
                lid = next_id("LEAD", "Lead_ID", "LD", 4)
                execute("""INSERT INTO LEAD
                           (Lead_ID, Full_Name, Telephone, Email, Source_Channel,
                            Campaign_ID, Followup_Status)
                           VALUES (?,?,?,?,?,?, 'รอการติดต่อ')""",
                        (lid, full.strip(), tel, email, channel,
                         opts.get(camp)))
                st.cache_data.clear()
                st.success(f"✅ บันทึกผู้สนใจ {lid} แล้ว — ส่งต่อให้ทีมขายติดตามได้เลย")

    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.subheader("ผู้สนใจล่าสุด 15 รายการ")
        st.dataframe(
            run_query("""SELECT Lead_ID AS รหัส, Full_Name AS ชื่อ, Telephone AS โทร,
                                Source_Channel AS ช่องทาง, Followup_Status AS สถานะ,
                                Created_At AS บันทึกเมื่อ
                         FROM LEAD ORDER BY Created_At DESC LIMIT 15"""),
            use_container_width=True, hide_index=True)