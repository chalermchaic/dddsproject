import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import auth
from analytics import campaign_roi as roi
from analytics import churn_health as ch
from analytics import lead_scoring as ls
from analytics import rfm_segmentation as rfm
from db.connection import cached_query

auth.guard("admin", "marketing", "sales", "support")
auth.breadcrumb("แดชบอร์ดวิเคราะห์")
st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูล")
st.caption("ผลลัพธ์งาน Data Science 4 งาน + รายงาน (Process 5.0)")

t1, t2, t3, t4, t5 = st.tabs([
    "1️⃣ Lead Scoring", "2️⃣ RFM Segmentation",
    "3️⃣ Customer Health & Churn", "4️⃣ Campaign ROI (5.1)",
    "5️⃣ รายงานสรุปยอดขาย (5.2)"])


# ================= งานที่ 1 =================
@st.cache_resource(show_spinner="กำลังเทรนโมเดล...")
def train_model(algo):
    return ls.train(algo)


with t1:
    st.subheader("จำแนกโอกาสปิดการขายของผู้สนใจ")
    algo = st.radio("เลือกอัลกอริทึม",
                    ["rf", "logreg"], horizontal=True,
                    format_func=lambda a: "Random Forest" if a == "rf"
                    else "Logistic Regression")
    r = train_model(algo)

    cols = st.columns(5)
    for col, (name, val) in zip(cols, r.metrics.items()):
        col.metric(name, f"{val:.3f}")
    st.caption(f"ชุดเทรน {r.train_size} แถว · ชุดทดสอบ {r.test_size} แถว · "
               f"5-Fold CV AUC = {r.cv_auc[0]} ± {r.cv_auc[1]}")

    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### ROC Curve")
            fig = go.Figure()
            fig.add_scatter(x=r.roc["fpr"], y=r.roc["tpr"], mode="lines",
                            name=f"AUC = {r.roc['auc']}", line=dict(color="#2E7D32", width=3))
            fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random",
                            line=dict(dash="dash", color="gray"))
            fig.update_layout(height=380, xaxis_title="False Positive Rate",
                              yaxis_title="True Positive Rate",
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    with b:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### ปัจจัยที่มีอิทธิพลสูงสุด")
            top = r.importance.head(8).sort_values("importance")
            fig = px.bar(top, x="importance", y="feature_th", orientation="h",
                         color="importance", color_continuous_scale="Greens")
            fig.update_layout(height=380, yaxis_title="", xaxis_title="ค่าความสำคัญ",
                              showlegend=False,
                              plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

    c, d = st.columns(2)
    with c:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### Confusion Matrix")
            fig = px.imshow(r.confusion, text_auto=True, color_continuous_scale="Greens",
                            x=["ทำนาย: ไม่สนใจ", "ทำนาย: ปิดได้"],
                            y=["จริง: ไม่สนใจ", "จริง: ปิดได้"])
            fig.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    with d:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### Classification Report")
            st.code(r.report)

    scored = ls.score_open_leads(r.model)
    if not scored.empty:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### 🔥 ผู้สนใจที่ควรติดตามก่อน")
            st.table(scored.head(20)[["Lead_ID", "Full_Name", "Source_Channel",
                                      "Activity_Count", "Score_Pct", "Priority"]]
                     .style.hide(axis="index"))

# ================= งานที่ 2 =================
with t2:
    st.subheader("แบ่งกลุ่มลูกค้าด้วย RFM + K-Means")
    df = rfm.build_rfm()
    if df.empty:
        st.warning("ยังไม่มีข้อมูลลูกค้าที่ซื้อสำเร็จ")
    else:
        k = st.slider("จำนวนกลุ่ม (k) สำหรับ K-Means", 2, 8, 4)
        df, sil = rfm.add_kmeans(df, k)

        m = st.columns(4)
        m[0].metric("ลูกค้าทั้งหมด", len(df))
        m[1].metric("รายได้รวม", f"฿{df.Monetary.sum():,.0f}")
        m[2].metric("Recency เฉลี่ย", f"{df.Recency_Days.mean():.0f} วัน")
        m[3].metric("Silhouette Score", sil)

        a, b = st.columns([2, 1])
        with a:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                fig = px.scatter_3d(df, x="Recency_Days", y="Frequency", z="Monetary",
                                    color="Segment", hover_name="Customer_ID",
                                    color_discrete_map=rfm.SEGMENT_COLOR, opacity=.8)
                fig.update_layout(height=480, margin=dict(t=20),
                                  plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
        with b:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                cnt = df.Segment.value_counts().reset_index()
                cnt.columns = ["Segment", "N"]
                fig = px.pie(cnt, names="Segment", values="N", hole=.5,
                             color="Segment", color_discrete_map=rfm.SEGMENT_COLOR)
                fig.update_layout(height=480, legend=dict(orientation="h", y=-.1),
                                  plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

        s = rfm.segment_summary(df)
        s["กลยุทธ์"] = s.Segment.map(rfm.ACTION)
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### สรุปรายกลุ่มและกลยุทธ์ที่แนะนำ")
            st.table(s.style.hide(axis="index").format({
                "Avg_Monetary": "฿{:,.0f}", "Total_Revenue": "฿{:,.0f}",
                "Revenue_Share_%": "{:.1f}%"}))

        with st.expander("📐 Elbow & Silhouette — เลือกค่า k ที่เหมาะสม"):
            e = rfm.elbow_data(df)
            f1, f2 = st.columns(2)
            with f1:
                with st.container(border=True):
                    st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                    st.plotly_chart(px.line(e, x="k", y="inertia", markers=True,
                                            title="Elbow Method").update_layout(
                                                plot_bgcolor="white", paper_bgcolor="white"),
                                    use_container_width=True)
            with f2:
                with st.container(border=True):
                    st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                    st.plotly_chart(px.line(e, x="k", y="silhouette", markers=True,
                                            title="Silhouette Score").update_layout(
                                                plot_bgcolor="white", paper_bgcolor="white"),
                                    use_container_width=True)

# ================= งานที่ 3 =================
with t3:
    st.subheader("คะแนนสุขภาพลูกค้า และความเสี่ยงเลิกใช้บริการ")
    h = ch.build_health()
    if h.empty:
        st.warning("ยังไม่มีข้อมูลเพียงพอ")
    else:
        v = ch.validate_with_model(h)
        m = st.columns(4)
        m[0].metric("ลูกค้าที่ประเมิน", len(h))
        m[1].metric("Health Score เฉลี่ย", f"{h.Health_Score.mean():.1f}")
        m[2].metric("🔴 เสี่ยงสูง", int((h.Risk_Level == "🔴 เสี่ยงสูง").sum()))
        m[3].metric("อัตรา Churn", f"{v.get('Churn_Rate_%', 0)}%")

        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                fig = px.histogram(h, x="Health_Score", nbins=25, color="Risk_Level",
                                   color_discrete_map={"🔴 เสี่ยงสูง": "#EF5350",
                                                       "🟡 เฝ้าระวัง": "#FFA726",
                                                       "🟢 แข็งแรง": "#66BB6A"})
                fig.update_layout(height=360, title="การกระจายของคะแนนสุขภาพ",
                                  plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
        with b:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                fig = px.scatter(h, x="Recency_Days", y="Health_Score",
                                 size="Monetary", color="Risk_Level",
                                 hover_name="Company_Name",
                                 color_discrete_map={"🔴 เสี่ยงสูง": "#EF5350",
                                                     "🟡 เฝ้าระวัง": "#FFA726",
                                                     "🟢 แข็งแรง": "#66BB6A"})
                fig.update_layout(height=360, title="Recency กับคะแนนสุขภาพ",
                                  plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### สรุปตามระดับความเสี่ยง")
            st.table(ch.risk_summary(h).style.hide(axis="index"))

        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### 🚨 20 ลูกค้าที่ควรติดตามด่วนที่สุด")
            st.table(h.head(20)[["Customer_ID", "Company_Name", "Recency_Days",
                                 "Frequency", "Monetary", "Ticket_Count",
                                 "Health_Score", "Risk_Level"]]
                     .style.hide(axis="index"))

        with st.expander("🔬 ตรวจสอบความถูกต้องของ Health Score ด้วยโมเดล"):
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.json(v)
                st.caption("AUC ของ Health Score เทียบกับ Logistic Regression — "
                           "ถ้าใกล้เคียงกัน แปลว่าสูตรถ่วงน้ำหนักที่ออกแบบไว้ใช้งานได้จริง")

# ================= งานที่ 4 =================
with t4:
    st.subheader("ประเมินผลตอบแทนของแคมเปญการตลาด")
    cdf = roi.campaign_overview()
    if cdf.empty:
        st.warning("ยังไม่มีข้อมูลแคมเปญ")
    else:
        m = st.columns(4)
        m[0].metric("งบประมาณรวม", f"฿{cdf.Budget_Cost.sum():,.0f}")
        m[1].metric("รายได้รวม", f"฿{cdf.Revenue.sum():,.0f}")
        overall = (cdf.Revenue.sum() - cdf.Budget_Cost.sum()) / cdf.Budget_Cost.sum() * 100
        m[2].metric("ROI รวม", f"{overall:.1f}%")
        m[3].metric("แคมเปญที่คุ้มค่า", int((cdf["ROI_%"] > 100).sum()))

        a, b = st.columns(2)
        with a:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                fig = px.bar(cdf.sort_values("ROI_%"), x="ROI_%", y="Campaign_Name",
                             orientation="h", color="ROI_%",
                             color_continuous_scale="RdYlGn", title="ROI รายแคมเปญ (%)")
                fig.update_layout(height=380, yaxis_title="",
                                  plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
        with b:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                fig = px.scatter(cdf, x="Cost_Per_Lead", y="Conversion_Rate",
                                 size="Revenue", color="Campaign_Name",
                                 hover_name="Campaign_Name",
                                 title="ต้นทุนต่อผู้สนใจ กับ อัตราแปลง")
                fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### ตารางสรุปผลแคมเปญ")
            st.table(cdf[["Campaign_Name", "Budget_Cost", "Total_Leads",
                          "Converted_Leads", "Conversion_Rate", "Cost_Per_Lead",
                          "CAC", "Revenue", "ROAS", "ROI_%", "Verdict"]]
                     .style.hide(axis="index").format({
                         "Budget_Cost": "฿{:,.0f}", "Revenue": "฿{:,.0f}",
                         "Conversion_Rate": "{:.1f}%"}))

        c, d = st.columns(2)
        with c:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.markdown("#### 🔻 กรวยการขาย (Funnel)")
                f = roi.funnel()
                fig = go.Figure(go.Funnel(y=f.Stage, x=f.N,
                                          textinfo="value+percent initial",
                                          marker_color="#2E7D32"))
                fig.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white")
                st.plotly_chart(fig, use_container_width=True)
        with d:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.markdown("#### 📡 ผลงานรายช่องทาง")
                ch_df = roi.channel_performance()
                st.table(ch_df.style.hide(axis="index"))
                sig = roi.channel_significance()
                st.info(f"**Chi-square = {sig['chi2']}, p = {sig['p_value']}** — "
                        f"{sig['conclusion']}")

        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### 📈 แนวโน้มรายได้แยกตามแคมเปญ")
            mt = roi.monthly_trend()
            st.plotly_chart(px.line(mt, x="Month", y="Revenue", color="Campaign_Name",
                                    markers=True).update_layout(
                                        plot_bgcolor="white", paper_bgcolor="white"),
                            use_container_width=True)

        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.markdown("#### 🏆 สินค้าทำรายได้สูงสุด")
            st.table(roi.top_products(10).style.hide(axis="index"))

# ================= งานที่ 5.2 — รายงานสรุปยอดขาย =================
with t5:
    st.subheader("รายงานสรุปยอดขาย → ฝ่ายขาย")
    period = st.radio("ช่วงเวลา", ["ทั้งหมด", "12 เดือนล่าสุด", "ปีนี้"], horizontal=True)
    where = "s.Sale_Status='ปิดการขายสำเร็จ' AND s.Confirmed_At IS NOT NULL"
    if period == "12 เดือนล่าสุด":
        where += " AND s.Confirmed_At >= date('now','-12 months')"
    elif period == "ปีนี้":
        where += " AND strftime('%Y', s.Confirmed_At) = strftime('%Y','now')"

    kpi = cached_query(f"""SELECT COUNT(*) bills, COALESCE(SUM(s.Total_Amount),0) rev,
                                  COALESCE(AVG(s.Total_Amount),0) avg
                           FROM SALE s WHERE {where}""").iloc[0]
    m = st.columns(3)
    m[0].metric("จำนวนบิล", f"{int(kpi.bills):,}")
    m[1].metric("ยอดขายรวม", f"฿{kpi.rev:,.0f}")
    m[2].metric("ยอดเฉลี่ย/บิล", f"฿{kpi.avg:,.0f}")

    by_emp = cached_query(f"""SELECT e.Employee_Name AS พนักงานขาย,
                                     COUNT(*) AS บิล, SUM(s.Total_Amount) AS ยอดขาย
                              FROM SALE s JOIN EMPLOYEE e ON e.Employee_ID=s.Employee_ID
                              WHERE {where}
                              GROUP BY e.Employee_ID ORDER BY ยอดขาย DESC""")
    a, b = st.columns([3, 2])
    with a:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.plotly_chart(px.bar(by_emp, x="ยอดขาย", y="พนักงานขาย", orientation="h",
                                   color="ยอดขาย", color_continuous_scale="Greens",
                                   title="ยอดขายรายพนักงาน").update_layout(
                                       plot_bgcolor="white", paper_bgcolor="white"),
                            use_container_width=True)
    by_month = cached_query(f"""SELECT strftime('%Y-%m', s.Confirmed_At) AS เดือน,
                                       SUM(s.Total_Amount) AS ยอดขาย
                                FROM SALE s WHERE {where}
                                GROUP BY เดือน ORDER BY เดือน""")
    with b:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            st.plotly_chart(px.area(by_month, x="เดือน", y="ยอดขาย").update_layout(
                plot_bgcolor="white", paper_bgcolor="white"), use_container_width=True)

    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.markdown("#### ตารางสรุปรายพนักงาน")
        st.table(by_emp.style.hide(axis="index").format({"ยอดขาย": "฿{:,.0f}"}))
    st.download_button("⬇️ ดาวน์โหลดรายงาน (CSV)",
                       by_emp.to_csv(index=False).encode("utf-8-sig"),
                       file_name="sales_summary.csv", mime="text/csv")