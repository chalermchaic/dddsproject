from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

import auth
from analytics import lead_scoring as ls
from db.connection import cached_query, execute, next_id, run_query

emp = auth.guard("admin", "sales")
st.title("📞 ติดตามผู้สนใจ")
st.caption(f"ผู้ใช้งาน: {emp['name']} ({emp['username']})")

STATUSES = ["รอการติดต่อ", "อยู่ระหว่างเสนอขาย", "ปิดการขายสำเร็จ", "ไม่สนใจ"]


@st.cache_resource(show_spinner="กำลังเทรนโมเดลจัดลำดับความสำคัญ...")
def get_model():
    return ls.train("rf")


tab1, tab2, tab3 = st.tabs(["🔥 คิวงานจัดลำดับด้วย AI", "🔍 ค้นหา & บันทึกกิจกรรม",
                            "📈 ภาพรวมการติดตาม"])

# ---------------- แท็บ 1: Priority Queue ----------------
with tab1:
    st.caption("จัดลำดับผู้สนใจที่ยังไม่ปิด ตามความน่าจะเป็นที่จะปิดการขายได้")
    try:
        res = get_model()
        scored = ls.score_open_leads(res.model)
        if scored.empty:
            st.info("ไม่มีผู้สนใจที่เปิดค้างอยู่")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("รอติดตามทั้งหมด", len(scored))
            c2.metric("🔥 Hot", int((scored.Priority == "🔥 Hot").sum()))
            c3.metric("🌤 Warm", int((scored.Priority == "🌤 Warm").sum()))
            c4.metric("ROC-AUC ของโมเดล", res.metrics["ROC-AUC"])

            pick = st.multiselect("กรองระดับความสำคัญ",
                                  ["🔥 Hot", "🌤 Warm", "❄️ Cold"],
                                  default=["🔥 Hot", "🌤 Warm"])
            view = scored[scored.Priority.isin(pick)] if pick else scored
            st.dataframe(
                view[["Lead_ID", "Full_Name", "Source_Channel", "Activity_Count",
                      "Followup_Status", "Score_Pct", "Priority"]]
                .rename(columns={"Lead_ID": "รหัส", "Full_Name": "ชื่อ",
                                 "Source_Channel": "ช่องทาง",
                                 "Activity_Count": "ติดตามแล้ว (ครั้ง)",
                                 "Followup_Status": "สถานะ",
                                 "Score_Pct": "โอกาสปิด %", "Priority": "ระดับ"}),
                use_container_width=True, hide_index=True, height=430,
                column_config={"โอกาสปิด %": st.column_config.ProgressColumn(
                    format="%.1f%%", min_value=0, max_value=100)})
            st.download_button("⬇️ ดาวน์โหลดคิวงาน (CSV)",
                               view.to_csv(index=False).encode("utf-8-sig"),
                               "priority_leads.csv", "text/csv")
    except Exception as e:
        st.error(f"เทรนโมเดลไม่สำเร็จ: {e}")

# ---------------- แท็บ 2: ค้นหา + บันทึกกิจกรรม ----------------
with tab2:
    c1, c2 = st.columns([2, 1])
    kw = c1.text_input("🔍 ค้นหาชื่อ / เบอร์โทร / รหัส")
    fs = c2.multiselect("สถานะ", STATUSES, default=["รอการติดต่อ", "อยู่ระหว่างเสนอขาย"])

    q = """SELECT l.Lead_ID, l.Full_Name, l.Telephone, l.Email, l.Source_Channel,
                  l.Followup_Status, c.Campaign_Name,
                  COUNT(a.Activity_ID) AS Acts, MAX(a.Activity_Date) AS Last_Act
           FROM LEAD l
           LEFT JOIN CAMPAIGN c      ON c.Campaign_ID = l.Campaign_ID
           LEFT JOIN LEAD_ACTIVITY a ON a.Lead_ID = l.Lead_ID
           WHERE 1=1 """
    p = []
    if kw:
        q += " AND (l.Full_Name LIKE ? OR l.Telephone LIKE ? OR l.Lead_ID LIKE ?)"
        p += [f"%{kw}%"] * 3
    if fs:
        q += f" AND l.Followup_Status IN ({','.join('?' * len(fs))})"
        p += fs
    q += " GROUP BY l.Lead_ID ORDER BY l.Created_At DESC LIMIT 200"

    leads = run_query(q, tuple(p))
    st.caption(f"พบ {len(leads)} รายการ")
    st.dataframe(leads.rename(columns={
        "Lead_ID": "รหัส", "Full_Name": "ชื่อ", "Telephone": "โทร",
        "Source_Channel": "ช่องทาง", "Followup_Status": "สถานะ",
        "Campaign_Name": "แคมเปญ", "Acts": "ติดตาม", "Last_Act": "ล่าสุด"}),
        use_container_width=True, hide_index=True, height=260)

    st.divider()
    if leads.empty:
        st.info("ไม่พบผู้สนใจตามเงื่อนไข")
    else:
        sel = st.selectbox("เลือกผู้สนใจเพื่อบันทึกกิจกรรม",
                           leads.Lead_ID + " — " + leads.Full_Name)
        lid = sel.split(" — ")[0]

        left, right = st.columns([1, 1])
        with left:
            st.markdown("#### ➕ บันทึกกิจกรรมใหม่")
            with st.form("act", clear_on_submit=True):
                atype = st.selectbox("ประเภท", ["โทรศัพท์", "อีเมล", "ส่งไลน์", "นัดพบ"])
                st.caption(f"บันทึกโดย: {emp['name']} ({emp['username']})")
                adate = st.date_input("วันที่ติดต่อ", value=date.today())
                notes = st.text_area("บันทึกผลการติดต่อ", height=80)
                nxt = st.date_input("นัดติดตามครั้งถัดไป",
                                    value=date.today() + timedelta(days=7))
                new_st = st.selectbox("อัปเดตสถานะผู้สนใจ", STATUSES, index=1)

                if st.form_submit_button("💾 บันทึก", type="primary",
                                         use_container_width=True):
                    aid = next_id("LEAD_ACTIVITY", "Activity_ID", "ACT", 5)
                    execute("INSERT INTO LEAD_ACTIVITY VALUES (?,?,?,?,?,?,?)",
                            (aid, lid, atype, f"{adate} 10:00:00",
                             emp["employee_id"], notes, str(nxt)))
                    execute("UPDATE LEAD SET Followup_Status=? WHERE Lead_ID=?",
                            (new_st, lid))
                    st.cache_data.clear()
                    st.success(f"บันทึก {aid} และอัปเดตสถานะเป็น “{new_st}” แล้ว")

        with right:
            st.markdown("#### 🕓 ไทม์ไลน์การติดตาม")
            hist = run_query("""SELECT a.Activity_Date, a.Activity_Type,
                                       e.Employee_Name AS Sales_Staff, a.Notes
                                FROM LEAD_ACTIVITY a
                                JOIN EMPLOYEE e ON e.Employee_ID = a.Employee_ID
                                WHERE a.Lead_ID=?
                                ORDER BY a.Activity_Date DESC""", (lid,))
            if hist.empty:
                st.info("ยังไม่มีประวัติการติดตาม")
            else:
                for r in hist.itertuples():
                    st.markdown(
                        f"**{r.Activity_Date[:10]} · {r.Activity_Type}** — "
                        f"{r.Sales_Staff}  \n{r.Notes or '—'}")
                    st.divider()

# ---------------- แท็บ 3: ภาพรวม ----------------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("จำนวนกิจกรรมแยกตามประเภท")
        d = cached_query("""SELECT Activity_Type AS ประเภท, COUNT(*) AS จำนวน
                            FROM LEAD_ACTIVITY GROUP BY Activity_Type""")
        st.plotly_chart(px.bar(d, x="ประเภท", y="จำนวน",
                               color_discrete_sequence=["#2E7D32"]),
                        use_container_width=True)
    with c2:
        st.subheader("ผลงานรายพนักงาน")
        d = cached_query("""
            SELECT e.Employee_Name AS พนักงาน,
                   COUNT(*) AS กิจกรรม,
                   COUNT(DISTINCT a.Lead_ID) AS ผู้สนใจที่ดูแล,
                   SUM(CASE WHEN l.Followup_Status='ปิดการขายสำเร็จ' THEN 1 ELSE 0 END) AS ปิดได้
            FROM LEAD_ACTIVITY a
            JOIN LEAD l     ON l.Lead_ID = a.Lead_ID
            JOIN EMPLOYEE e ON e.Employee_ID = a.Employee_ID
            GROUP BY e.Employee_ID ORDER BY ปิดได้ DESC""")
        st.dataframe(d, use_container_width=True, hide_index=True)

    st.subheader("ความสัมพันธ์: จำนวนครั้งที่ติดตาม กับ อัตราปิดการขาย")
    d = cached_query("""
        SELECT n AS ครั้งที่ติดตาม, COUNT(*) AS ผู้สนใจ,
               ROUND(100.0*SUM(won)/COUNT(*),1) AS 'อัตราปิด %'
        FROM (SELECT l.Lead_ID, COUNT(a.Activity_ID) AS n,
                     CASE WHEN l.Followup_Status='ปิดการขายสำเร็จ' THEN 1 ELSE 0 END AS won
              FROM LEAD l LEFT JOIN LEAD_ACTIVITY a ON a.Lead_ID=l.Lead_ID
              GROUP BY l.Lead_ID)
        GROUP BY n ORDER BY n""")
    fig = px.bar(d, x="ครั้งที่ติดตาม", y="อัตราปิด %", text="อัตราปิด %",
                 color="อัตราปิด %", color_continuous_scale="Greens")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 ข้อค้นพบ: จำนวนครั้งที่ติดตามสัมพันธ์เชิงบวกกับอัตราปิดการขายอย่างชัดเจน "
            "— ควรกำหนด SLA ให้ทีมขายติดตามอย่างน้อย 3 ครั้งต่อผู้สนใจ 1 ราย")