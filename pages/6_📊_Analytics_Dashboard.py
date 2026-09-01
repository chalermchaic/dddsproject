import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics import campaign_roi as roi
from analytics import churn_health as ch
from analytics import lead_scoring as ls
from analytics import rfm_segmentation as rfm

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูล")
st.caption("ผลลัพธ์งาน Data Science ทั้ง 4 — ประมวลผลจากฐานข้อมูลจริงในระบบ")

t1, t2, t3, t4 = st.tabs([
    "1️⃣ Lead Scoring", "2️⃣ RFM Segmentation",
    "3️⃣ Customer Health & Churn", "4️⃣ Campaign ROI"])


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
        st.markdown("#### ROC Curve")
        fig = go.Figure()
        fig.add_scatter(x=r.roc["fpr"], y=r.roc["tpr"], mode="lines",
                        name=f"AUC = {r.roc['auc']}", line=dict(color="#2E7D32", width=3))
        fig.add_scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random",
                        line=dict(dash="dash", color="gray"))
        fig.update_layout(height=380, xaxis_title="False Positive Rate",
                          yaxis_title="True Positive Rate")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        st.markdown("#### ปัจจัยที่มีอิทธิพลสูงสุด")
        top = r.importance.head(8).sort_values("importance")
        fig = px.bar(top, x="importance", y="feature_th", orientation="h",
                     color="importance", color_continuous_scale="Greens")
        fig.update_layout(height=380, yaxis_title="", xaxis_title="ค่าความสำคัญ",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    c, d = st.columns(2)
    with c:
        st.markdown("#### Confusion Matrix")
        fig = px.imshow(r.confusion, text_auto=True, color_continuous_scale="Greens",
                        x=["ทำนาย: ไม่สนใจ", "ทำนาย: ปิดได้"],
                        y=["จริง: ไม่สนใจ", "จริง: ปิดได้"])
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)
    with d:
        st.markdown("#### Classification Report")
        st.code(r.report)

    st.markdown("#### 🔥 ผู้สนใจที่ควรติดตามก่อน")
    scored = ls.score_open_leads(r.model)
    if not scored.empty:
        st.dataframe(scored.head(20)[["Lead_ID", "Full_Name", "Source_Channel",
                                      "Activity_Count", "Score_Pct", "Priority"]],
                     use_container_width=True, hide_index=True)

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
            fig = px.scatter_3d(df, x="Recency_Days", y="Frequency", z="Monetary",
                                color="Segment", hover_name="Customer_ID",
                                color_discrete_map=rfm.SEGMENT_COLOR, opacity=.8)
            fig.update_layout(height=480, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)
        with b:
            cnt = df.Segment.value_counts().reset_index()
            cnt.columns = ["Segment", "N"]
            fig = px.pie(cnt, names="Segment", values="N", hole=.5,
                         color="Segment", color_discrete_map=rfm.SEGMENT_COLOR)
            fig.update_layout(height=480, legend=dict(orientation="h", y=-.1))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### สรุปรายกลุ่มและกลยุทธ์ที่แนะนำ")
        s = rfm.segment_summary(df)
        s["กลยุทธ์"] = s.Segment.map(rfm.ACTION)
        st.dataframe(s, use_container_width=True, hide_index=True,
                     column_config={
                         "Avg_Monetary": st.column_config.NumberColumn(format="฿%.0f"),
                         "Total_Revenue": st.column_config.NumberColumn(format="฿%.0f"),
                         "Revenue_Share_%": st.column_config.ProgressColumn(
                             format="%.1f%%", min_value=0, max_value=100)})

        with st.expander("📐 Elbow & Silhouette — เลือกค่า k ที่เหมาะสม"):
            e = rfm.elbow_data(df)
            f1, f2 = st.columns(2)
            f1.plotly_chart(px.line(e, x="k", y="inertia", markers=True,
                                    title="Elbow Method"), use_container_width=True)
            f2.plotly_chart(px.line(e, x="k", y="silhouette", markers=True,
                                    title="Silhouette Score"), use_container_width=True)

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
            fig = px.histogram(h, x="Health_Score", nbins=25, color="Risk_Level",
                               color_discrete_map={"🔴 เสี่ยงสูง": "#EF5350",
                                                   "🟡 เฝ้าระวัง": "#FFA726",
                                                   "🟢 แข็งแรง": "#66BB6A"})
            fig.update_layout(height=360, title="การกระจายของคะแนนสุขภาพ")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            fig = px.scatter(h, x="Recency_Days", y="Health_Score",
                             size="Monetary", color="Risk_Level",
                             hover_name="Company_Name",
                             color_discrete_map={"🔴 เสี่ยงสูง": "#EF5350",
                                                 "🟡 เฝ้าระวัง": "#FFA726",
                                                 "🟢 แข็งแรง": "#66BB6A"})
            fig.update_layout(height=360, title="Recency กับคะแนนสุขภาพ")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### สรุปตามระดับความเสี่ยง")
        st.dataframe(ch.risk_summary(h), use_container_width=True, hide_index=True)

        st.markdown("#### 🚨 20 ลูกค้าที่ควรติดตามด่วนที่สุด")
        st.dataframe(h.head(20)[["Customer_ID", "Company_Name", "Recency_Days",
                                 "Frequency", "Monetary", "Ticket_Count",
                                 "Health_Score", "Risk_Level"]],
                     use_container_width=True, hide_index=True,
                     column_config={"Health_Score": st.column_config.ProgressColumn(
                         format="%.0f", min_value=0, max_value=100)})

        with st.expander("🔬 ตรวจสอบความถูกต้องของ Health Score ด้วยโมเดล"):
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
            fig = px.bar(cdf.sort_values("ROI_%"), x="ROI_%", y="Campaign_Name",
                         orientation="h", color="ROI_%",
                         color_continuous_scale="RdYlGn", title="ROI รายแคมเปญ (%)")
            fig.update_layout(height=380, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            fig = px.scatter(cdf, x="Cost_Per_Lead", y="Conversion_Rate",
                             size="Revenue", color="Campaign_Name",
                             hover_name="Campaign_Name",
                             title="ต้นทุนต่อผู้สนใจ กับ อัตราแปลง")
            fig.update_layout(height=380)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### ตารางสรุปผลแคมเปญ")
        st.dataframe(cdf[["Campaign_Name", "Budget_Cost", "Total_Leads",
                          "Converted_Leads", "Conversion_Rate", "Cost_Per_Lead",
                          "CAC", "Revenue", "ROAS", "ROI_%", "Verdict"]],
                     use_container_width=True, hide_index=True,
                     column_config={
                         "Budget_Cost": st.column_config.NumberColumn(format="฿%.0f"),
                         "Revenue": st.column_config.NumberColumn(format="฿%.0f"),
                         "Conversion_Rate": st.column_config.ProgressColumn(
                             format="%.1f%%", min_value=0, max_value=100)})

        c, d = st.columns(2)
        with c:
            st.markdown("#### 🔻 กรวยการขาย (Funnel)")
            f = roi.funnel()
            fig = go.Figure(go.Funnel(y=f.Stage, x=f.N,
                                      textinfo="value+percent initial",
                                      marker_color="#2E7D32"))
            fig.update_layout(height=340)
            st.plotly_chart(fig, use_container_width=True)
        with d:
            st.markdown("#### 📡 ผลงานรายช่องทาง")
            ch_df = roi.channel_performance()
            st.dataframe(ch_df, use_container_width=True, hide_index=True)
            sig = roi.channel_significance()
            st.info(f"**Chi-square = {sig['chi2']}, p = {sig['p_value']}** — "
                    f"{sig['conclusion']}")

        st.markdown("#### 📈 แนวโน้มรายได้แยกตามแคมเปญ")
        mt = roi.monthly_trend()
        st.plotly_chart(px.line(mt, x="Month", y="Revenue", color="Campaign_Name",
                                markers=True), use_container_width=True)

        st.markdown("#### 🏆 สินค้าทำรายได้สูงสุด")
        st.dataframe(roi.top_products(10), use_container_width=True, hide_index=True)