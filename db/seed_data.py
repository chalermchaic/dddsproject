"""
Seed Data Generator — Smart CRM (SQLite)
รัน: python db/seed_data.py
ใช้เฉพาะ standard library + sqlite3 (ไม่ต้องลง Faker)
"""
import sqlite3, random, os
from datetime import datetime, timedelta

random.seed(42)                       # reproducible
DB_PATH     = "db/crm.db"
SCHEMA_PATH = "db/schema.sql"
TODAY       = datetime(2026, 9, 1)
N_LEADS     = 600

# ---------- คลังคำสำหรับสร้างชื่อไทย ----------
FIRST = ["สมชาย","สมหญิง","ปรีชา","อารีย์","วิชัย","กมล","ณัฐพล","สุดารัตน์",
         "ธนกร","พิมพ์ใจ","ศิริพร","อนุชา","เจนจิรา","ภาณุวัฒน์","รัตนา","ชลธิชา"]
LAST  = ["ใจดี","รักเรียน","ศรีสุข","วงศ์สว่าง","มั่นคง","ทองดี","แสงทอง",
         "พูนทรัพย์","บุญมาก","เกษมสุข","อินทรีย์","จันทร์เพ็ญ"]
STAFF = ["ณัฐวุฒิ ขายเก่ง","ปิยะดา ปิดดีล","ธีรภัทร ตามงาน","อรพรรณ ดูแลลูกค้า"]
SUPPORT = ["ศุภชัย ซัพพอร์ต","มณีรัตน์ ช่วยเหลือ","กิตติพงษ์ เทคนิค"]
COMPANY = ["บจก.{} เทรดดิ้ง","หจก.{} ซัพพลาย","บมจ.{} อินดัสทรี","ร้าน{} การค้า"]

# ---------- EMPLOYEE (master data + บัญชีเข้าใช้งานตาม role) ----------
# (Employee_ID, Employee_Name, Position, Department, Username, Role)
EMPLOYEES = [
    ("EMP001", "ธนวัฒน์ บริหารดี",  "ผู้ดูแลระบบ",              "ฝ่ายบริหาร",        "admin1",     "admin"),
    ("EMP002", "ชนิกานต์ การตลาด",  "นักการตลาด",              "ฝ่ายการตลาด",       "marketing1", "marketing"),
    ("EMP003", "ปวริศา วางแผน",     "นักการตลาด",              "ฝ่ายการตลาด",       "marketing2", "marketing"),
    ("EMP004", STAFF[0],            "พนักงานขาย",              "ฝ่ายขาย",           "sale1",      "sales"),
    ("EMP005", STAFF[1],            "พนักงานขาย",              "ฝ่ายขาย",           "sale2",      "sales"),
    ("EMP006", STAFF[2],            "พนักงานขาย",              "ฝ่ายขาย",           "sale3",      "sales"),
    ("EMP007", STAFF[3],            "หัวหน้าทีมขาย",           "ฝ่ายขาย",           "sale4",      "sales"),
    ("EMP008", SUPPORT[0],          "เจ้าหน้าที่บริการลูกค้า",  "ฝ่ายบริการลูกค้า",  "cs1",        "support"),
    ("EMP009", SUPPORT[1],          "เจ้าหน้าที่บริการลูกค้า",  "ฝ่ายบริการลูกค้า",  "cs2",        "support"),
    ("EMP010", SUPPORT[2],          "ช่างเทคนิค",              "ฝ่ายบริการลูกค้า",  "cs3",        "support"),
]
SALES_IDS   = [e[0] for e in EMPLOYEES if e[5] == "sales"]
MKT_IDS     = [e[0] for e in EMPLOYEES if e[5] in ("marketing", "admin")]
SUPPORT_IDS = [e[0] for e in EMPLOYEES if e[5] == "support"]
EMP_NAME    = {e[0]: e[1] for e in EMPLOYEES}

def dt(d): return d.strftime("%Y-%m-%d %H:%M:%S")
def dd(d): return d.strftime("%Y-%m-%d")

# ---------- สร้าง DB ----------
os.makedirs("db", exist_ok=True)
if os.path.exists(DB_PATH): os.remove(DB_PATH)
con = sqlite3.connect(DB_PATH)
con.execute("PRAGMA foreign_keys = ON")
con.executescript(open(SCHEMA_PATH, encoding="utf-8").read())
cur = con.cursor()

# ============ 0) EMPLOYEE (master + auth) ============
cur.executemany("INSERT INTO EMPLOYEE VALUES (?,?,?,?,?,?)", EMPLOYEES)

# ============ 1) CAMPAIGN (D5) ============
campaigns = [
    ("CMP001","Summer Sale 2025","ลดราคาสินค้ากลุ่มซอฟต์แวร์",15.0,120000,"2025-03-01","2025-05-31","หมดอายุ"),
    ("CMP002","Mid-Year Business Expo","ออกบูธงานแสดงสินค้า B2B",10.0,250000,"2025-06-01","2025-07-31","หมดอายุ"),
    ("CMP003","Digital Ads Q3","โฆษณา Facebook/Google Ads",5.0, 80000,"2025-08-01","2025-10-31","หมดอายุ"),
    ("CMP004","New Year Promotion 2026","แพ็กเกจพิเศษต้อนรับปีใหม่",20.0,180000,"2025-12-01","2026-02-28","หมดอายุ"),
    ("CMP005","Enterprise Solution Day","สัมมนาลูกค้าองค์กร",12.0,300000,"2026-03-01","2026-06-30","หมดอายุ"),
    ("CMP006","Back-to-Business H2","แคมเปญกระตุ้นยอดครึ่งปีหลัง", 8.0,150000,"2026-07-01","2026-12-31","เปิดใช้งานอยู่"),
]
# แคมเปญสร้างโดยฝ่ายการตลาด (วนแบบ deterministic ไม่รบกวน RNG ของส่วนอื่น)
campaigns = [c + (MKT_IDS[idx % len(MKT_IDS)],) for idx, c in enumerate(campaigns)]
cur.executemany("INSERT INTO CAMPAIGN VALUES (?,?,?,?,?,?,?,?,?)", campaigns)

# ============ 2) PRODUCT (D2) ============
products = [
    ("PRD001","ระบบ CRM Cloud (License 1 ปี)","Software",   45000,"ระบบบริหารลูกค้าบนคลาวด์"),
    ("PRD002","ระบบ POS หน้าร้าน","Software",              28000,"ระบบขายหน้าร้านพร้อมสต็อก"),
    ("PRD003","แพ็กเกจ Data Analytics Dashboard","Service", 65000,"ออกแบบแดชบอร์ดวิเคราะห์ข้อมูล"),
    ("PRD004","เครื่องอ่านบาร์โค้ด Pro","Hardware",          4500,"เครื่องสแกนบาร์โค้ดไร้สาย"),
    ("PRD005","เซิร์ฟเวอร์สำรองข้อมูล NAS","Hardware",      38000,"อุปกรณ์จัดเก็บข้อมูลองค์กร"),
    ("PRD006","บริการฝึกอบรมพนักงาน (2 วัน)","Service",     18000,"อบรมการใช้งานระบบ"),
    ("PRD007","ค่าบำรุงรักษารายปี (MA)","Service",          22000,"ดูแลระบบและอัปเดต"),
    ("PRD008","โมดูลเชื่อมต่อ LINE OA","Software",          15000,"เชื่อมระบบกับ LINE Official"),
]
cur.executemany("INSERT INTO PRODUCT VALUES (?,?,?,?,?)", products)

# ---------- น้ำหนักเชิงสถิติ (ให้โมเดลเรียนรู้ได้) ----------
CH_W = {"Facebook":0.35,"Line":0.25,"Google":0.25,"Direct":0.15}   # สัดส่วนช่องทาง
CH_Q = {"Direct":0.30,"Google":0.15,"Line":0.05,"Facebook":-0.05}  # คุณภาพ lead

leads, acts, sales, sdetails, customers = [], [], [], [], []
a_no = s_no = c_no = 1

for i in range(1, N_LEADS+1):
    lid = f"LD{i:04d}"
    cmp_id = random.choice(campaigns)[0]
    cmp_row = next(c for c in campaigns if c[0]==cmp_id)
    disc = cmp_row[3]
    lead_owner = random.choice(SALES_IDS)        # พนักงานขายเจ้าของ lead รายนี้
    ch = random.choices(list(CH_W), weights=list(CH_W.values()))[0]
    created = TODAY - timedelta(days=random.randint(20, 540), hours=random.randint(0,23))

    # จำนวนการติดตาม: lead คุณภาพดีมักถูกติดตามมากกว่า
    n_act = max(0, int(random.gauss(3 + CH_Q[ch]*6, 1.6)))
    n_act = min(n_act, 8)

    # ---- ความน่าจะเป็นในการปิดการขาย (สร้าง signal ให้ ML) ----
    p = 0.05 + 0.09*n_act + CH_Q[ch] + 0.010*disc
    p = max(0.02, min(0.92, p))
    converted = random.random() < p

    if n_act == 0:
        status = "รอการติดต่อ"
    elif converted:
        status = "ปิดการขายสำเร็จ"
    else:
        status = random.choices(["ไม่สนใจ","อยู่ระหว่างเสนอขาย"], weights=[0.75,0.25])[0]

    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    leads.append((lid, name, f"08{random.randint(10000000,99999999)}",
                  f"lead{i:04d}@example.com", ch, cmp_id, status, dt(created)))

    # ---- LEAD_ACTIVITY ----
    last = created
    for k in range(n_act):
        gap = random.randint(1,10) if converted else random.randint(3,25)
        last = last + timedelta(days=gap, hours=random.randint(1,8))
        if last > TODAY: break
        acts.append((f"ACT{a_no:05d}", lid,
                     random.choices(["โทรศัพท์","ส่งไลน์","อีเมล","นัดพบ"],
                                    weights=[0.4,0.3,0.2,0.1])[0],
                     dt(last), lead_owner,
                     random.choice(["ลูกค้าสนใจ ขอใบเสนอราคา","ยังไม่ตัดสินใจ ขอเวลาพิจารณา",
                                    "นัดสาธิตระบบสัปดาห์หน้า","ติดต่อไม่ได้ ฝากข้อความ",
                                    "สอบถามรายละเอียดแพ็กเกจเพิ่มเติม"]),
                     dd(last + timedelta(days=random.randint(3,14)))))
        a_no += 1

    # ---- SALE + SALE_DETAIL + CUSTOMER ----
    if converted:
        n_orders = random.choices([1,2,3,4,5], weights=[0.42,0.26,0.16,0.10,0.06])[0]
        first_buy = last + timedelta(days=random.randint(1,7))
        for o in range(n_orders):
            if first_buy > TODAY: break
            sid = f"SL{s_no:04d}"
            items = random.sample(products, random.randint(1,3))
            total = 0
            for prd in items:
                qty  = random.randint(1,4)
                unit = round(prd[3] * (1 - disc/100), 2)
                sub  = round(unit*qty, 2)
                total += sub
                sdetails.append((sid, prd[0], qty, unit, sub))
            sales.append((sid, lid, lead_owner, f"QT-{first_buy.year}-{s_no:04d}", dd(first_buy),
                          round(total,2), "ปิดการขายสำเร็จ",
                          dt(first_buy - timedelta(days=1)),            # Order_Confirmed_At
                          f"slip_{sid}.jpg",                            # Payment_Slip
                          f"INV-{first_buy.year}-{s_no:04d}",
                          f"TRF{random.randint(100000,999999)}",
                          dt(first_buy + timedelta(days=random.randint(1,5)))))
            s_no += 1
            first_buy += timedelta(days=random.randint(30, 200))

        cid = f"CU{c_no:04d}"; c_no += 1
        ctype = "องค์กร / VIP" if n_orders >= 3 else "ทั่วไป"
        addr = f"{random.randint(1,999)}/{random.randint(1,99)} ถนนสุขุมวิท เขตวัฒนา กรุงเทพฯ 10110"
        customers.append((cid, lid, random.choice(COMPANY).format(name.split()[0]),
                          str(random.randint(1000000000000,9999999999999)),
                          addr, addr, ctype, dd(last + timedelta(days=1))))
    else:
        # lead ที่ไม่ปิด บางส่วนเคยได้ใบเสนอราคา — ค้างอยู่ในขั้นใดขั้นหนึ่งของ Process 3.0
        if status == "อยู่ระหว่างเสนอขาย" and random.random() < 0.6:
            sid = f"SL{s_no:04d}"
            prd = random.choice(products); qty = random.randint(1,2)
            unit = round(prd[3]*(1-disc/100),2); sub = round(unit*qty,2)
            sdetails.append((sid, prd[0], qty, unit, sub))
            sstatus = random.choice(["ออกใบเสนอราคาแล้ว", "รอตรวจสอบคำสั่งซื้อ",
                                     "รอการตรวจสอบชำระเงิน"])
            order_conf = (None if sstatus == "ออกใบเสนอราคาแล้ว"
                          else dt(last + timedelta(days=random.randint(1,4))))
            slip = (f"slip_{sid}.jpg"
                    if sstatus == "รอการตรวจสอบชำระเงิน" and random.random() < 0.7 else None)
            sales.append((sid, lid, lead_owner, f"QT-{last.year}-{s_no:04d}", dd(last), sub,
                          sstatus, order_conf, slip, None, None, None))
            s_no += 1

cur.executemany("INSERT INTO LEAD          VALUES (?,?,?,?,?,?,?,?)", leads)
cur.executemany("INSERT INTO LEAD_ACTIVITY VALUES (?,?,?,?,?,?,?)",  acts)
cur.executemany("INSERT INTO SALE          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", sales)
cur.executemany("INSERT INTO SALE_DETAIL   VALUES (?,?,?,?,?)",      sdetails)
cur.executemany("INSERT INTO CUSTOMER      VALUES (?,?,?,?,?,?,?,?)", customers)

# ============ 3) TICKET + TICKET_MESSAGE (D4) ============
tickets, msgs = [], []
t_no = m_no = 1
TITLES = {
 "ระบบขัดข้อง": ["เข้าสู่ระบบไม่ได้","ระบบทำงานช้าผิดปกติ","ข้อมูลไม่ซิงค์"],
 "สินค้าชำรุด": ["อุปกรณ์เปิดไม่ติด","เครื่องสแกนอ่านไม่ได้","สายเชื่อมต่อชำรุด"],
 "ขอข้อมูลเพิ่ม": ["ขอคู่มือการใช้งาน","สอบถามการต่ออายุ License","ขอใบเสนอราคาโมดูลเพิ่ม"],
}
for cid, lid, *_rest, ctype, mdate in customers:
    base = 3 if ctype == "องค์กร / VIP" else 1.5
    for _ in range(max(0, int(random.gauss(base, 1.5)))):
        tid = f"TK{t_no:04d}"; t_no += 1
        cat = random.choices(list(TITLES), weights=[0.45,0.30,0.25])[0]
        created = datetime.strptime(mdate,"%Y-%m-%d") + timedelta(days=random.randint(5,400))
        if created > TODAY: continue
        st = random.choices(["ปิดเคสสำเร็จ","กำลังแก้ไข","รอดำเนินการ"], weights=[0.78,0.15,0.07])[0]
        # เคสร้ายแรงใช้เวลานานกว่า
        dur = random.uniform(0.5, 4) if cat=="ขอข้อมูลเพิ่ม" else random.uniform(1, 14)
        closed = dt(created + timedelta(days=dur)) if st=="ปิดเคสสำเร็จ" else None
        emp_id = None if st == "รอดำเนินการ" else random.choice(SUPPORT_IDS)
        support_name = EMP_NAME[emp_id] if emp_id else EMP_NAME[random.choice(SUPPORT_IDS)]
        if st == "ปิดเคสสำเร็จ" and random.random() < 0.7:
            rating = random.choices([5,4,3,2,1], weights=[0.4,0.3,0.15,0.1,0.05])[0]
            feedback = random.choice(["แก้ไขรวดเร็ว ประทับใจ","บริการดี แต่รอนานไปนิด",
                                      "เจ้าหน้าที่สุภาพมาก","ตอบกลับช้า","แก้ปัญหาได้ตรงจุด"])
        else:
            rating = feedback = None
        tickets.append((tid, cid, random.choice(products)[0], cat,
                        random.choice(TITLES[cat]), st, emp_id,
                        dt(created), closed, rating, feedback))
        # ข้อความโต้ตอบ: เคสยิ่งนาน ยิ่งมีข้อความมาก
        n_msg = max(2, int(dur*0.9) + random.randint(1,3))
        t = created
        for j in range(n_msg):
            sender = "Customer" if j % 2 == 0 else "Support_Staff"
            msgs.append((f"MSG{m_no:05d}", tid, sender,
                         "ลูกค้า" if sender=="Customer" else support_name,
                         random.choice(["พบปัญหาตามที่แจ้ง รบกวนช่วยตรวจสอบด่วน",
                                        "รับเรื่องแล้วครับ กำลังตรวจสอบให้",
                                        "ยังใช้งานไม่ได้เหมือนเดิม","แก้ไขเรียบร้อยแล้ว รบกวนทดสอบ",
                                        "ขอบคุณครับ ใช้งานได้แล้ว"]),
                         dt(t)))
            m_no += 1
            t += timedelta(hours=random.randint(2,20))

cur.executemany("INSERT INTO TICKET         VALUES (?,?,?,?,?,?,?,?,?,?,?)", tickets)
cur.executemany("INSERT INTO TICKET_MESSAGE VALUES (?,?,?,?,?,?)",      msgs)

con.commit()

# ---------- ตรวจ referential integrity ----------
fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()
assert not fk_errors, f"❌ พบ FK ผิดพลาด: {fk_errors}"

pipe = {s: sum(1 for x in sales if x[6] == s) for s in
        ("ออกใบเสนอราคาแล้ว", "รอตรวจสอบคำสั่งซื้อ", "รอการตรวจสอบชำระเงิน", "ปิดการขายสำเร็จ")}
rated = sum(1 for t in tickets if t[9] is not None)
print(f"""✅ สร้างฐานข้อมูลสำเร็จ: {DB_PATH}
   EMPLOYEE {len(EMPLOYEES)} | CAMPAIGN {len(campaigns)} | PRODUCT {len(products)} | LEAD {len(leads)}
   LEAD_ACTIVITY {len(acts)} | SALE {len(sales)} | SALE_DETAIL {len(sdetails)}
   CUSTOMER {len(customers)} | TICKET {len(tickets)} ({rated} มีคะแนน) | TICKET_MESSAGE {len(msgs)}
   SALE pipeline: {pipe}
   บัญชีเข้าใช้งาน: {', '.join(e[4] for e in EMPLOYEES)}""")
con.close()