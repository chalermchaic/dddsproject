from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

import auth
from db.connection import cached_query, execute, next_id, run_query

emp = auth.guard("admin", "support")
auth.breadcrumb("รับแจ้งปัญหา")
st.title("🎫 ระบบรับแจ้งปัญหา")
st.caption(f"ผู้ใช้งาน: {emp['name']} ({emp['username']})")

CATS = ["ระบบขัดข้อง", "สินค้าชำรุด", "ขอข้อมูลเพิ่ม"]
STATUSES = ["รอดำเนินการ", "กำลังแก้ไข", "ปิดเคสสำเร็จ"]

# ทีมบริการลูกค้า (สำหรับมอบหมายเคส)  ชื่อ -> Employee_ID
_sup = run_query("SELECT Employee_ID, Employee_Name FROM EMPLOYEE "
                 "WHERE Role='support' ORDER BY Employee_Name")
SUPPORT_OPTS = {r.Employee_Name: r.Employee_ID for r in _sup.itertuples()}
SUPPORT_NAMES = list(SUPPORT_OPTS)

k = cached_query("""
    SELECT COUNT(*) AS total,
           SUM(Ticket_Status='รอดำเนินการ') AS waiting,
           SUM(Ticket_Status='กำลังแก้ไข')  AS working,
           SUM(Ticket_Status='ปิดเคสสำเร็จ') AS closed,
           ROUND(AVG(julianday(Closed_At)-julianday(Created_At)),2) AS avg_days
    FROM TICKET""").iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("เคสทั้งหมด", f"{k.total:,}")
c2.metric("รอดำเนินการ", f"{k.waiting:,}")
c3.metric("กำลังแก้ไข", f"{k.working:,}")
c4.metric("ปิดสำเร็จ", f"{k.closed:,}")
c5.metric("เวลาแก้เฉลี่ย", f"{k.avg_days:.1f} วัน" if k.avg_days else "—")

tab1, tab2, tab3 = st.tabs(["📥 คิวเคส & สนทนา", "➕ เปิดเคสใหม่", "📊 สถิติงานบริการ"])

# ---------------- แท็บ 1 ----------------
with tab1:
    f1, f2 = st.columns(2)
    fs = f1.multiselect("สถานะ", STATUSES, default=["รอดำเนินการ", "กำลังแก้ไข"])
    fc = f2.multiselect("ประเภทปัญหา", CATS, default=CATS)

    q = """SELECT t.Ticket_ID, t.Problem_Category, t.Problem_Title, t.Ticket_Status,
                  e.Employee_Name AS Assigned_Staff, t.Created_At,
                  cu.Company_Name, l.Full_Name
           FROM TICKET t
           JOIN CUSTOMER cu     ON cu.Customer_ID=t.Customer_ID
           JOIN LEAD l          ON l.Lead_ID=cu.Lead_ID
           LEFT JOIN EMPLOYEE e ON e.Employee_ID=t.Employee_ID
           WHERE 1=1"""
    p = []
    if fs:
        q += f" AND t.Ticket_Status IN ({','.join('?'*len(fs))})"; p += fs
    if fc:
        q += f" AND t.Problem_Category IN ({','.join('?'*len(fc))})"; p += fc
    q += " ORDER BY t.Created_At DESC LIMIT 200"

    tks = run_query(q, tuple(p))
    st.caption(f"พบ {len(tks)} เคส")
    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.dataframe(tks.rename(columns={
            "Ticket_ID": "รหัส", "Problem_Category": "ประเภท", "Problem_Title": "หัวข้อ",
            "Ticket_Status": "สถานะ", "Assigned_Staff": "ผู้รับผิดชอบ",
            "Created_At": "แจ้งเมื่อ", "Company_Name": "ลูกค้า"}),
            use_container_width=True, hide_index=True, height=250)

    if not tks.empty:
        st.divider()
        sel = st.selectbox("เลือกเคสเพื่อดูบทสนทนา",
                           tks.Ticket_ID + " — " + tks.Problem_Title)
        tid = sel.split(" — ")[0]
        trow = tks[tks.Ticket_ID == tid].iloc[0]

        left, right = st.columns([2, 1])
        with left:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.markdown(f"#### 💬 {trow.Problem_Title}")
                msgs = run_query("""SELECT Sender_Type, Sender_Name, Message_Text, Sent_At
                                    FROM TICKET_MESSAGE WHERE Ticket_ID=?
                                    ORDER BY Sent_At""", (tid,))
                for m in msgs.itertuples():
                    who = "user" if m.Sender_Type == "Customer" else "assistant"
                    with st.chat_message(who):
                        st.markdown(f"**{m.Sender_Name}** · _{m.Sent_At[:16]}_")
                        st.write(m.Message_Text)

                new_msg = st.chat_input("พิมพ์ข้อความตอบกลับลูกค้า...")
                if new_msg:
                    mid = next_id("TICKET_MESSAGE", "Message_ID", "MSG", 5)
                    execute("""INSERT INTO TICKET_MESSAGE
                               (Message_ID,Ticket_ID,Sender_Type,Sender_Name,
                                Message_Text,Sent_At) VALUES (?,?,?,?,?,?)""",
                            (mid, tid, "Support_Staff", emp["name"],
                             new_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    st.cache_data.clear()
                    st.rerun()

        with right:
            with st.container(border=True):
                st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
                st.markdown("#### ⚙️ จัดการเคส (Process 4.2)")
                with st.form("upd"):
                    ns = st.selectbox("สถานะ", STATUSES, index=STATUSES.index(trow.Ticket_Status))
                    _cur = trow.Assigned_Staff if trow.Assigned_Staff in SUPPORT_NAMES else None
                    staff_name = st.selectbox(
                        "ผู้รับผิดชอบ", SUPPORT_NAMES,
                        index=SUPPORT_NAMES.index(_cur) if _cur else 0)
                    cdate = st.date_input("วันที่ปิดเคส", value=date.today())
                    resolution = st.text_area("สรุปผลการแก้ไข (แจ้งลูกค้าเมื่อปิดเคส)",
                                              height=70)
                    if st.form_submit_button("💾 อัปเดต", type="primary",
                                             use_container_width=True):
                        closed = f"{cdate} 17:00:00" if ns == "ปิดเคสสำเร็จ" else None
                        execute("""UPDATE TICKET SET Ticket_Status=?, Employee_ID=?,
                                   Closed_At=? WHERE Ticket_ID=?""",
                                (ns, SUPPORT_OPTS[staff_name], closed, tid))
                        if ns == "ปิดเคสสำเร็จ" and resolution.strip():
                            mid = next_id("TICKET_MESSAGE", "Message_ID", "MSG", 5)
                            execute("""INSERT INTO TICKET_MESSAGE (Message_ID,Ticket_ID,
                                       Sender_Type,Sender_Name,Message_Text,Sent_At)
                                       VALUES (?,?,?,?,?,?)""",
                                    (mid, tid, "Support_Staff", emp["name"],
                                     f"[สรุปผล] {resolution.strip()}",
                                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        st.cache_data.clear()
                        st.success("อัปเดตเคสแล้ว")
                        st.rerun()

                # ---- Process 4.3: ประเมินผลบริการ (ปกติลูกค้าให้ผ่าน Portal) ----
                if trow.Ticket_Status == "ปิดเคสสำเร็จ":
                    cur_rating = run_query(
                        "SELECT Service_Rating, Service_Feedback FROM TICKET WHERE Ticket_ID=?",
                        (tid,)).iloc[0]
                    st.markdown("#### ⭐ ประเมินผลบริการ (Process 4.3)")
                    if pd.notna(cur_rating.Service_Rating):
                        st.info(f"ลูกค้าให้ {int(cur_rating.Service_Rating)} ดาว — "
                                f"{cur_rating.Service_Feedback or '(ไม่มีความเห็น)'}")
                    else:
                        with st.form("rate"):
                            sc = st.slider("คะแนน (แทนลูกค้า)", 1, 5, 5)
                            fb = st.text_input("ความเห็น")
                            if st.form_submit_button("บันทึกคะแนน"):
                                execute("""UPDATE TICKET SET Service_Rating=?, Service_Feedback=?
                                           WHERE Ticket_ID=?""", (sc, fb or None, tid))
                                st.cache_data.clear()
                                st.rerun()

# ---------------- แท็บ 2 ----------------
with tab2:
    cs = run_query("""SELECT cu.Customer_ID, cu.Company_Name, l.Full_Name
                      FROM CUSTOMER cu JOIN LEAD l ON l.Lead_ID=cu.Lead_ID
                      ORDER BY cu.Customer_ID""")
    ps = run_query("SELECT Product_ID, Product_Name FROM PRODUCT")
    with st.form("new_ticket", clear_on_submit=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        cust = st.selectbox("ลูกค้า *", cs.Customer_ID + " — " +
                            cs.Company_Name.fillna("") + " (" + cs.Full_Name + ")")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("ประเภทปัญหา", CATS)
        prod = c2.selectbox("สินค้าที่เกี่ยวข้อง", ["— ไม่ระบุ —"] +
                            (ps.Product_ID + " — " + ps.Product_Name).tolist())
        title = st.text_input("หัวข้อปัญหา *")
        detail = st.text_area("รายละเอียดจากลูกค้า", height=100)
        assignee = st.selectbox("มอบหมายให้", ["— ยังไม่มอบหมาย —"] + SUPPORT_NAMES)

        if st.form_submit_button("🎫 เปิดเคส", type="primary", use_container_width=True):
            if not title.strip():
                st.error("กรุณากรอกหัวข้อปัญหา")
            else:
                tid = next_id("TICKET", "Ticket_ID", "TK", 4)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                emp_id = SUPPORT_OPTS.get(assignee)   # None ถ้ายังไม่มอบหมาย
                execute("INSERT INTO TICKET VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (tid, cust.split(" — ")[0],
                         None if prod.startswith("—") else prod.split(" — ")[0],
                         cat, title.strip(), "รอดำเนินการ", emp_id, now, None, None, None))
                if detail.strip():
                    mid = next_id("TICKET_MESSAGE", "Message_ID", "MSG", 5)
                    execute("""INSERT INTO TICKET_MESSAGE
                               (Message_ID,Ticket_ID,Sender_Type,Sender_Name,
                                Message_Text,Sent_At) VALUES (?,?,?,?,?,?)""",
                            (mid, tid, "Customer", "ลูกค้า", detail.strip(), now))
                st.cache_data.clear()
                st.success(f"✅ เปิดเคส {tid} เรียบร้อย")

# ---------------- แท็บ 3 ----------------
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            d = cached_query("""SELECT Problem_Category AS ประเภท, COUNT(*) AS จำนวน
                                FROM TICKET GROUP BY Problem_Category""")
            st.plotly_chart(px.pie(d, names="ประเภท", values="จำนวน", hole=.5,
                                   title="สัดส่วนประเภทปัญหา").update_layout(
                                       plot_bgcolor="white", paper_bgcolor="white"),
                            use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
            d = cached_query("""SELECT e.Employee_Name AS พนักงาน, COUNT(*) AS เคสทั้งหมด,
                                       SUM(t.Ticket_Status='ปิดเคสสำเร็จ') AS ปิดสำเร็จ,
                                       ROUND(AVG(julianday(t.Closed_At)-julianday(t.Created_At)),2)
                                            AS 'เวลาเฉลี่ย (วัน)',
                                       ROUND(AVG(t.Service_Rating),2) AS 'คะแนนเฉลี่ย'
                                FROM TICKET t
                                JOIN EMPLOYEE e ON e.Employee_ID = t.Employee_ID
                                GROUP BY e.Employee_ID""")
            st.markdown("#### ผลงานทีมซัพพอร์ต")
            st.dataframe(d, use_container_width=True, hide_index=True)
            avg = cached_query("SELECT ROUND(AVG(Service_Rating),2) r, COUNT(Service_Rating) n "
                               "FROM TICKET").iloc[0]
            st.metric("⭐ คะแนนบริการเฉลี่ย (Process 4.3)",
                      f"{avg.r or 0}/5", f"จาก {int(avg.n)} รีวิว")

    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.subheader("แนวโน้มจำนวนเคสรายเดือน")
        d = cached_query("""SELECT strftime('%Y-%m',Created_At) AS เดือน,
                                   Problem_Category AS ประเภท, COUNT(*) AS จำนวน
                            FROM TICKET GROUP BY เดือน, ประเภท ORDER BY เดือน""")
        st.plotly_chart(px.line(d, x="เดือน", y="จำนวน", color="ประเภท", markers=True)
                        .update_layout(plot_bgcolor="white", paper_bgcolor="white"),
                        use_container_width=True)

    with st.container(border=True):
        st.markdown('<span class="card-shadow-marker"></span>', unsafe_allow_html=True)
        st.subheader("การกระจายของระยะเวลาแก้ปัญหา")
        d = cached_query("""SELECT Problem_Category AS ประเภท,
                                   julianday(Closed_At)-julianday(Created_At) AS วัน
                            FROM TICKET WHERE Closed_At IS NOT NULL""")
        st.plotly_chart(px.box(d, x="ประเภท", y="วัน", color="ประเภท", points="outliers")
                        .update_layout(plot_bgcolor="white", paper_bgcolor="white"),
                    use_container_width=True)