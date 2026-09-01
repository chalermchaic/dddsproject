# พจนานุกรมข้อมูล (Data Dictionary) — Entity Relationship Diagram

**โครงการ:** ระบบบริหารจัดการความสัมพันธ์ลูกค้า (CRM System)
**อ้างอิงจาก:** ER Diagram (`er.drawio` / `er.drawio.pdf`) — 10 Entities แบบ Normalized (3NF)

---

### 1. `CAMPAIGN` (ข้อมูลแคมเปญการตลาด - D5)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Campaign_ID`** | VARCHAR(10) | **PK** | NO | รหัสแคมเปญ (เช่น `M000000001`) |
| `Campaign_Name` | VARCHAR(150) | - | NO | ชื่อโครงการแคมเปญโปรโมชัน |
| `Promotion_Details`| TEXT | - | YES | เงื่อนไขและรายละเอียดสิทธิพิเศษ |
| `Discount_Rate` | DECIMAL(5,2) | - | YES | อัตราส่วนลด (%) |
| `Budget_Cost` | DECIMAL(10,2)| - | YES | งบประมาณที่ใช้ลงทุนในแคมเปญ |
| `Start_Date` | DATE | - | NO | วันที่เริ่มต้นโปรโมชัน |
| `End_Date` | DATE | - | NO | วันที่สิ้นสุดโปรโมชัน |
| `Campaign_Status` | VARCHAR(20) | - | NO | สถานะ (เช่น 'Active', 'Expired') |
| `Employee_ID` | VARCHAR(10) | **FK** | NO | พนักงานฝ่ายการตลาดผู้สร้างแคมเปญ (`EMPLOYEE.Employee_ID`) |

---

### 2. `LEAD` (ข้อมูลผู้สนใจหลัก - D1 Master)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Lead_ID`** | VARCHAR(10) | **PK** | NO | รหัสผู้สนใจ (เช่น `L000000001`) |
| `Full_Name` | VARCHAR(100) | - | NO | ชื่อ-นามสกุลของผู้สนใจ (Composite: First_Name + Last_Name) |
| `Telephone` | VARCHAR(20) | - | NO | เบอร์โทรศัพท์ติดต่อ |
| `Email` | VARCHAR(100) | - | YES | อีเมลสำหรับส่งโปรโมชัน/เอกสาร |
| `Source_Channel` | VARCHAR(50) | - | YES | ช่องทางที่มา (เช่น 'Facebook', 'Line', 'Direct') |
| `Campaign_ID` | VARCHAR(10) | **FK** | YES | อ้างอิงแคมเปญต้นทาง (`CAMPAIGN.Campaign_ID`) |
| `Followup_Status` | VARCHAR(20) | - | NO | สถานะ (เช่น 'รอการติดต่อ', 'อยู่ระหว่างเสนอขาย', 'ปิดการขาย') |
| `Created_At` | TIMESTAMP | - | NO | วันเวลาที่ลงทะเบียนเข้าสู่ระบบ |

---

### 3. `LEAD_ACTIVITY` (บันทึกประวัติการติดต่อผู้สนใจ - D1 Activity) — *Weak Entity*
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Activity_ID`** | VARCHAR(10) | **PK** | NO | รหัสบันทึกกิจกรรม (เช่น `A000000001`) |
| `Lead_ID` | VARCHAR(10) | **FK** | NO | อ้างอิงผู้สนใจที่ติดต่อ (`LEAD.Lead_ID`) |
| `Activity_Type` | VARCHAR(50) | - | NO | ช่องทางการติดต่อ (เช่น 'โทรศัพท์', 'อีเมล', 'Line', 'นัดพบ') |
| `Activity_Date` | DATETIME | - | NO | วันเวลาที่ติดต่อประสานงาน |
| `Employee_ID` | VARCHAR(10) | **FK** | NO | พนักงานขายผู้รับผิดชอบการติดต่อรอบนี้ (`EMPLOYEE.Employee_ID`) |
| `Notes` | TEXT | - | YES | บันทึกสรุปผลการพูดคุยเจรจา |
| `Next_Action_Date`| DATE | - | YES | วันที่นัดหมายติดต่อรอบถัดไป |

---

### 4. `CUSTOMER` (ข้อมูลโปรไฟล์ลูกค้าทางการ - D3)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Customer_ID`** | VARCHAR(10) | **PK** | NO | รหัสลูกค้าทางการ (เช่น `C000000001`) |
| `Lead_ID` | VARCHAR(10) | **FK (Unique)**| NO | เชื่อมโยงรหัสผู้สนใจเดิม (`LEAD.Lead_ID`) |
| `Company_Name` | VARCHAR(150) | - | YES | ชื่อบริษัท/หน่วยงาน (กรณีลูกค้านิติบุคคล) |
| `Tax_ID` | VARCHAR(20) | - | YES | เลขประจำตัวผู้เสียภาษี |
| `Billing_Address` | TEXT | - | YES | ที่อยู่ออกใบเสร็จ/ใบกำกับภาษี |
| `Shipping_Address` | TEXT | - | YES | ที่อยู่จัดส่งสินค้า |
| `Customer_Type` | VARCHAR(20) | - | NO | ประเภทลูกค้า (เช่น 'บุคคลทั่วไป', 'องค์กร / VIP') |
| `Membership_Date` | DATE | - | NO | วันที่ขึ้นทะเบียนเป็นลูกค้าทางการ |

---

### 5. `PRODUCT` (ข้อมูลสินค้าและบริการ - Master Data)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Product_ID`** | VARCHAR(10) | **PK** | NO | รหัสสินค้า (เช่น `P000000001`) |
| `Product_Name` | VARCHAR(150) | - | NO | ชื่อสินค้า/บริการ |
| `Product_Category`| VARCHAR(50) | - | YES | หมวดหมู่สินค้า |
| `Unit_Price` | DECIMAL(10,2)| - | NO | ราคาขายมาตรฐานต่อหน่วย |
| `Description` | TEXT | - | YES | คำอธิบายรายละเอียดสินค้า |

---

### 6. `SALE` (ข้อมูลหัวบิลยอดขายและธุรกรรม - D2 Header)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Sale_ID`** | VARCHAR(10) | **PK** | NO | รหัสการขาย/ธุรกรรม (เช่น `S000000001`) |
| `Lead_ID` | VARCHAR(10) | **FK** | NO | รหัสผู้สนใจ/ผู้ซื้อ (`LEAD.Lead_ID`) |
| `Employee_ID` | VARCHAR(10) | **FK** | NO | พนักงานขายผู้รับผิดชอบ/ปิดการขาย (`EMPLOYEE.Employee_ID`) |
| `Quotation_No` | VARCHAR(20) | - | NO | หมายเลขใบเสนอราคา |
| `Quotation_Date` | DATE | - | NO | วันที่ออกใบเสนอราคา |
| `Total_Amount` | DECIMAL(10,2)| - | NO | ยอดเงินสุทธิรวมของบิล (เก็บค่าจริง ณ วันที่ออกเอกสาร — ไม่ใช่ค่าคำนวณสด) |
| `Sale_Status` | VARCHAR(20) | - | NO | สถานะ (เช่น 'เสนอราคาแล้ว', 'รอชำระเงิน', 'ปิดการขายสำเร็จ') |
| `Invoice_No` | VARCHAR(20) | - | YES | หมายเลขใบแจ้งหนี้ / ใบเสร็จรับเงิน |
| `Payment_Ref` | VARCHAR(100) | - | YES | หลักฐานอ้างอิงการโอนเงิน (สลิป) |
| `Confirmed_At` | TIMESTAMP | - | YES | วันเวลาที่ยืนยันการรับเงิน |

---

### 7. `SALE_DETAIL` (รายละเอียดรายการสินค้าในบิล - D2 Items Detail) — *Weak Entity*
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Sale_ID`** | VARCHAR(10) | **PK, FK** | NO | อ้างอิงหัวบิลการขาย (`SALE.Sale_ID`) |
| **`Product_ID`** | VARCHAR(10) | **PK, FK** | NO | อ้างอิงสินค้าที่ซื้อ (`PRODUCT.Product_ID`) |
| `Quantity` | INT | - | NO | จำนวนชิ้นที่สั่งซื้อ |
| `Unit_Price` | DECIMAL(10,2)| - | NO | ราคาขายต่อหน่วย ณ วันที่ซื้อ |
| `Subtotal` | DECIMAL(10,2)| - | NO | ราคารวมของรายการ — *Derived* (`Quantity × Unit_Price`) |

---

### 8. `TICKET` (ข้อมูลหัวข้อปัญหาและบริการหลังการขาย - D4 Header)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Ticket_ID`** | VARCHAR(10) | **PK** | NO | รหัสแจ้งปัญหาบริการ (เช่น `T000000001`) |
| `Customer_ID` | VARCHAR(10) | **FK** | NO | รหัสลูกค้าผู้แจ้งเคส (`CUSTOMER.Customer_ID`) |
| `Product_ID` | VARCHAR(10) | **FK** | YES | รหัสสินค้าที่มีปัญหา (`PRODUCT.Product_ID`) |
| `Problem_Category` | VARCHAR(50) | - | NO | หมวดหมู่ปัญหา (เช่น 'ระบบขัดข้อง', 'สินค้าชำรุด') |
| `Problem_Title` | VARCHAR(150) | - | NO | หัวข้อเรื่องที่แจ้ง |
| `Ticket_Status` | VARCHAR(20) | - | NO | สถานะ (เช่น 'รอดำเนินการ', 'กำลังแก้ไข', 'ปิดเคสสำเร็จ') |
| `Employee_ID` | VARCHAR(10) | **FK** | YES | พนักงาน/ช่างเทคนิคที่รับผิดชอบเคส (`EMPLOYEE.Employee_ID`) — NULL = ยังไม่มอบหมาย |
| `Created_At` | TIMESTAMP | - | NO | วันเวลาที่ลูกค้าแจ้งเรื่องเข้ามา |
| `Closed_At` | DATETIME | - | YES | วันเวลาที่ปิดเคสการให้บริการ |

---

### 9. `TICKET_MESSAGE` (ประวัติการถาม-ตอบและบันทึกการแก้ไขปัญหา - D4 Messages) — *Weak Entity*
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Message_ID`** | VARCHAR(10) | **PK** | NO | รหัสข้อความ (เช่น `MSG0000001`) |
| `Ticket_ID` | VARCHAR(10) | **FK** | NO | อ้างอิงเคส Ticket (`TICKET.Ticket_ID`) |
| `Sender_Type` | VARCHAR(20) | - | NO | ผู้ส่ง (Customer/Support) |
| `Sender_Name` | VARCHAR(100) | - | NO | ชื่อผู้ส่งข้อความ |
| `Message_Text` | TEXT | - | NO | ข้อความถาม-ตอบ / บันทึกการแก้ไข |
| `Sent_At` | TIMESTAMP | - | NO | วันเวลาที่ส่งข้อความ |

---

### 10. `EMPLOYEE` (ข้อมูลพนักงาน - Master Data)
| ฟิลด์ (Field Name) | ประเภทข้อมูล (Type) | Key | Nullable | คำอธิบาย (Description) |
| :--- | :--- | :---: | :---: | :--- |
| **`Employee_ID`** | VARCHAR(10) | **PK** | NO | รหัสพนักงาน (เช่น `E000000001`) |
| `Employee_Name` | VARCHAR(100) | - | NO | ชื่อ-นามสกุลพนักงาน |
| `Position` | VARCHAR(50) | - | NO | ตำแหน่งงาน (เช่น 'พนักงานขาย', 'ช่างเทคนิค', 'นักการตลาด') |
| `Department` | VARCHAR(50) | - | NO | สังกัดฝ่าย ('ฝ่ายการตลาด' / 'ฝ่ายขาย' / 'ฝ่ายบริการลูกค้า' — ตรงกับ External Entity 3 ฝ่ายใน DFD) |

---

### ความสัมพันธ์ (Relationships)

| ความสัมพันธ์ | Cardinality | คำอธิบาย |
| :--- | :---: | :--- |
| CAMPAIGN — attracts — LEAD | 1 : N | 1 แคมเปญดึงผู้สนใจได้หลายคน |
| LEAD — has_logs — LEAD_ACTIVITY | 1 : N | 1 ผู้สนใจมีประวัติการติดต่อได้หลายครั้ง |
| LEAD — converts_to — CUSTOMER | 1 : 1 (optional) | ผู้สนใจอาจเปลี่ยนเป็นลูกค้าทางการ |
| LEAD — places — SALE | 1 : N | 1 ผู้สนใจ/ลูกค้าซื้อได้หลายบิล |
| SALE — contains — SALE_DETAIL | 1 : N | 1 บิลมีได้หลายรายการสินค้า |
| PRODUCT — included_in — SALE_DETAIL | 1 : N | 1 สินค้าถูกขายได้ในหลายบิล |
| PRODUCT — relates_to — TICKET | 1 : N | 1 สินค้าถูกแจ้งปัญหาได้หลายเคส |
| CUSTOMER — reports — TICKET | 1 : N | 1 ลูกค้าแจ้งปัญหาได้หลายเคส |
| TICKET — has_messages — TICKET_MESSAGE | 1 : N | 1 เคสมีประวัติสนทนาได้หลายข้อความ |
| EMPLOYEE — creates — CAMPAIGN | 1 : N | พนักงาน 1 คนสร้างแคมเปญได้หลายรายการ |
| EMPLOYEE — sells — SALE | 1 : N | พนักงานขาย 1 คนรับผิดชอบการขายได้หลายบิล |
| EMPLOYEE — resolves — TICKET | 1 : N | พนักงาน 1 คนรับผิดชอบเคสปัญหาได้หลายเคส |
| EMPLOYEE — performs — LEAD_ACTIVITY | 1 : N | พนักงาน 1 คนบันทึกกิจกรรมติดตามผู้สนใจได้หลายครั้ง |
