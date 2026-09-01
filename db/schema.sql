-- ============================================================
-- Smart CRM Database Schema (SQLite 3)
-- อ้างอิง Data Dictionary D1–D5
-- ============================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS TICKET_MESSAGE;
DROP TABLE IF EXISTS TICKET;
DROP TABLE IF EXISTS CUSTOMER;
DROP TABLE IF EXISTS SALE_DETAIL;
DROP TABLE IF EXISTS SALE;
DROP TABLE IF EXISTS LEAD_ACTIVITY;
DROP TABLE IF EXISTS LEAD;
DROP TABLE IF EXISTS PRODUCT;
DROP TABLE IF EXISTS CAMPAIGN;

-- ---------- D5: CAMPAIGN ----------
CREATE TABLE CAMPAIGN (
    Campaign_ID       TEXT(10)  PRIMARY KEY,
    Campaign_Name     TEXT(150) NOT NULL,
    Promotion_Details TEXT,
    Discount_Rate     REAL      NOT NULL DEFAULT 0
                                CHECK (Discount_Rate BETWEEN 0 AND 100),
    Budget_Cost       REAL      NOT NULL DEFAULT 0 CHECK (Budget_Cost >= 0),
    Start_Date        TEXT      NOT NULL,          -- 'YYYY-MM-DD'
    End_Date          TEXT      NOT NULL,
    Campaign_Status   TEXT(20)  NOT NULL DEFAULT 'เปิดใช้งานอยู่'
                                CHECK (Campaign_Status IN ('เปิดใช้งานอยู่','หมดอายุ')),
    CHECK (End_Date >= Start_Date)
);

-- ---------- D2: PRODUCT ----------
CREATE TABLE PRODUCT (
    Product_ID       TEXT(10)  PRIMARY KEY,
    Product_Name     TEXT(150) NOT NULL,
    Product_Category TEXT(50),
    Unit_Price       REAL      NOT NULL CHECK (Unit_Price >= 0),
    Description      TEXT
);

-- ---------- D1: LEAD ----------
CREATE TABLE LEAD (
    Lead_ID         TEXT(10)  PRIMARY KEY,
    Full_Name       TEXT(100) NOT NULL,
    Telephone       TEXT(20),
    Email           TEXT(100),
    Source_Channel  TEXT(50)  CHECK (Source_Channel IN ('Facebook','Line','Google','Direct')),
    Campaign_ID     TEXT(10),
    Followup_Status TEXT(20)  NOT NULL DEFAULT 'รอการติดต่อ'
                              CHECK (Followup_Status IN
                                    ('รอการติดต่อ','อยู่ระหว่างเสนอขาย','ปิดการขายสำเร็จ','ไม่สนใจ')),
    Created_At      TEXT      NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (Campaign_ID) REFERENCES CAMPAIGN(Campaign_ID)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- ---------- D1: LEAD_ACTIVITY ----------
CREATE TABLE LEAD_ACTIVITY (
    Activity_ID      TEXT(10)  PRIMARY KEY,
    Lead_ID          TEXT(10)  NOT NULL,
    Activity_Type    TEXT(50)  NOT NULL
                               CHECK (Activity_Type IN ('โทรศัพท์','อีเมล','ส่งไลน์','นัดพบ')),
    Activity_Date    TEXT      NOT NULL,
    Sales_Staff      TEXT(100),
    Notes            TEXT,
    Next_Action_Date TEXT,
    FOREIGN KEY (Lead_ID) REFERENCES LEAD(Lead_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ---------- D2: SALE ----------
CREATE TABLE SALE (
    Sale_ID        TEXT(10) PRIMARY KEY,
    Lead_ID        TEXT(10) NOT NULL,
    Quotation_No   TEXT(20) UNIQUE NOT NULL,
    Quotation_Date TEXT     NOT NULL,
    Total_Amount   REAL     NOT NULL DEFAULT 0 CHECK (Total_Amount >= 0),
    Sale_Status    TEXT(20) NOT NULL DEFAULT 'ออกใบเสนอราคาแล้ว'
                            CHECK (Sale_Status IN
                                  ('ออกใบเสนอราคาแล้ว','รอการตรวจสอบชำระเงิน','ปิดการขายสำเร็จ')),
    Invoice_No     TEXT(20) UNIQUE,
    Payment_Ref    TEXT(100),
    Confirmed_At   TEXT,
    FOREIGN KEY (Lead_ID) REFERENCES LEAD(Lead_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    -- กฎธุรกิจ: ปิดการขายสำเร็จต้องมีวันยืนยัน
    CHECK (Sale_Status <> 'ปิดการขายสำเร็จ' OR Confirmed_At IS NOT NULL)
);

-- ---------- D2: SALE_DETAIL (Composite PK) ----------
CREATE TABLE SALE_DETAIL (
    Sale_ID    TEXT(10) NOT NULL,
    Product_ID TEXT(10) NOT NULL,
    Quantity   INTEGER  NOT NULL CHECK (Quantity > 0),
    Unit_Price REAL     NOT NULL CHECK (Unit_Price >= 0),
    Subtotal   REAL     NOT NULL CHECK (Subtotal >= 0),
    PRIMARY KEY (Sale_ID, Product_ID),
    FOREIGN KEY (Sale_ID)    REFERENCES SALE(Sale_ID)       ON DELETE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES PRODUCT(Product_ID)  ON DELETE RESTRICT
);

-- ---------- D3: CUSTOMER ----------
CREATE TABLE CUSTOMER (
    Customer_ID      TEXT(10)  PRIMARY KEY,
    Lead_ID          TEXT(10)  UNIQUE NOT NULL,   -- 1:1 กับ LEAD ที่ปิดการขายแล้ว
    Company_Name     TEXT(150),
    Tax_ID           TEXT(20),
    Billing_Address  TEXT,
    Shipping_Address TEXT,
    Customer_Type    TEXT(20) NOT NULL DEFAULT 'ทั่วไป'
                              CHECK (Customer_Type IN ('ทั่วไป','องค์กร / VIP')),
    Membership_Date  TEXT     NOT NULL,
    FOREIGN KEY (Lead_ID) REFERENCES LEAD(Lead_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------- D4: TICKET ----------
CREATE TABLE TICKET (
    Ticket_ID        TEXT(10)  PRIMARY KEY,
    Customer_ID      TEXT(10)  NOT NULL,
    Product_ID       TEXT(10),
    Problem_Category TEXT(50)  CHECK (Problem_Category IN ('ระบบขัดข้อง','สินค้าชำรุด','ขอข้อมูลเพิ่ม')),
    Problem_Title    TEXT(150) NOT NULL,
    Ticket_Status    TEXT(20)  NOT NULL DEFAULT 'รอดำเนินการ'
                               CHECK (Ticket_Status IN ('รอดำเนินการ','กำลังแก้ไข','ปิดเคสสำเร็จ')),
    Assigned_Staff   TEXT(100),
    Created_At       TEXT      NOT NULL DEFAULT (datetime('now','localtime')),
    Closed_At        TEXT,
    FOREIGN KEY (Customer_ID) REFERENCES CUSTOMER(Customer_ID) ON DELETE CASCADE,
    FOREIGN KEY (Product_ID)  REFERENCES PRODUCT(Product_ID)   ON DELETE SET NULL,
    CHECK (Ticket_Status <> 'ปิดเคสสำเร็จ' OR Closed_At IS NOT NULL)
);

-- ---------- D4: TICKET_MESSAGE ----------
CREATE TABLE TICKET_MESSAGE (
    Message_ID   TEXT(10)  PRIMARY KEY,
    Ticket_ID    TEXT(10)  NOT NULL,
    Sender_Type  TEXT(20)  NOT NULL CHECK (Sender_Type IN ('Customer','Support_Staff')),
    Sender_Name  TEXT(100),
    Message_Text TEXT      NOT NULL,
    Sent_At      TEXT      NOT NULL DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (Ticket_ID) REFERENCES TICKET(Ticket_ID) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES (รองรับ Query ของงาน Data Science ทั้ง 4)
-- ============================================================
CREATE INDEX idx_lead_campaign   ON LEAD(Campaign_ID);
CREATE INDEX idx_lead_status     ON LEAD(Followup_Status);
CREATE INDEX idx_lead_source     ON LEAD(Source_Channel);
CREATE INDEX idx_act_lead        ON LEAD_ACTIVITY(Lead_ID, Activity_Date);
CREATE INDEX idx_sale_lead       ON SALE(Lead_ID);
CREATE INDEX idx_sale_confirmed  ON SALE(Confirmed_At);
CREATE INDEX idx_cust_lead       ON CUSTOMER(Lead_ID);
CREATE INDEX idx_ticket_cust     ON TICKET(Customer_ID, Created_At);
CREATE INDEX idx_msg_ticket      ON TICKET_MESSAGE(Ticket_ID);

-- ============================================================
-- VIEWS สำเร็จรูปสำหรับ Analytics Layer
-- ============================================================
-- V1: ฟีเจอร์สำหรับ Lead Scoring (งานที่ 1)
CREATE VIEW V_LEAD_FEATURES AS
SELECT  l.Lead_ID,
        l.Source_Channel,
        COALESCE(c.Discount_Rate, 0)                       AS Discount_Rate,
        COUNT(a.Activity_ID)                               AS Activity_Count,
        COUNT(DISTINCT a.Activity_Type)                    AS Distinct_Channel_Used,
        MIN(julianday(a.Activity_Date) - julianday(l.Created_At)) AS First_Response_Days,
        MAX(julianday(a.Activity_Date) - julianday(l.Created_At)) AS Engagement_Span_Days,
        CASE WHEN l.Followup_Status = 'ปิดการขายสำเร็จ' THEN 1 ELSE 0 END AS Target_Converted
FROM LEAD l
LEFT JOIN CAMPAIGN      c ON c.Campaign_ID = l.Campaign_ID
LEFT JOIN LEAD_ACTIVITY a ON a.Lead_ID     = l.Lead_ID
WHERE l.Followup_Status IN ('ปิดการขายสำเร็จ','ไม่สนใจ')   -- เฉพาะ label ที่ชัดเจน
GROUP BY l.Lead_ID;

-- V2: RFM ดิบ (งานที่ 2)
CREATE VIEW V_CUSTOMER_RFM AS
SELECT  cu.Customer_ID,
        cu.Customer_Type,
        CAST(julianday('now') - julianday(MAX(s.Confirmed_At)) AS INTEGER) AS Recency_Days,
        COUNT(s.Sale_ID)      AS Frequency,
        SUM(s.Total_Amount)   AS Monetary
FROM CUSTOMER cu
JOIN SALE s ON s.Lead_ID = cu.Lead_ID AND s.Sale_Status = 'ปิดการขายสำเร็จ'
GROUP BY cu.Customer_ID;

-- V3: ตัวชี้วัดสุขภาพลูกค้า (งานที่ 3)
CREATE VIEW V_SERVICE_HEALTH AS
SELECT  cu.Customer_ID,
        COUNT(DISTINCT t.Ticket_ID) AS Ticket_Count,
        SUM(CASE WHEN t.Problem_Category IN ('ระบบขัดข้อง','สินค้าชำรุด') THEN 1 ELSE 0 END) AS Critical_Tickets,
        AVG(julianday(t.Closed_At) - julianday(t.Created_At)) AS Avg_Resolution_Days,
        COUNT(m.Message_ID) AS Total_Messages
FROM CUSTOMER cu
LEFT JOIN TICKET t         ON t.Customer_ID = cu.Customer_ID
LEFT JOIN TICKET_MESSAGE m ON m.Ticket_ID   = t.Ticket_ID
GROUP BY cu.Customer_ID;

-- V4: ผลตอบแทนแคมเปญ (งานที่ 4)
CREATE VIEW V_CAMPAIGN_ROI AS
SELECT  c.Campaign_ID,
        c.Campaign_Name,
        c.Budget_Cost,
        COUNT(DISTINCT l.Lead_ID)  AS Total_Leads,
        COUNT(DISTINCT s.Lead_ID)  AS Converted_Leads,
        ROUND(100.0 * COUNT(DISTINCT s.Lead_ID) / NULLIF(COUNT(DISTINCT l.Lead_ID),0), 2) AS Conversion_Rate,
        ROUND(c.Budget_Cost / NULLIF(COUNT(DISTINCT l.Lead_ID),0), 2)  AS Cost_Per_Lead,
        COALESCE(SUM(s.Total_Amount),0) AS Revenue,
        ROUND((COALESCE(SUM(s.Total_Amount),0) - c.Budget_Cost) / NULLIF(c.Budget_Cost,0), 4) AS ROI
FROM CAMPAIGN c
LEFT JOIN LEAD l ON l.Campaign_ID = c.Campaign_ID
LEFT JOIN SALE s ON s.Lead_ID = l.Lead_ID AND s.Sale_Status = 'ปิดการขายสำเร็จ'
GROUP BY c.Campaign_ID;