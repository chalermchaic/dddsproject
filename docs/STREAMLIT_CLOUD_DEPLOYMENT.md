# ☁️ คู่มือการ Deploy ระบบขึ้น Streamlit Community Cloud
### โครงงาน DDDS: ระบบบริหารจัดการความสัมพันธ์ลูกค้าอัจฉริยะ (Smart CRM & Data Science Analytics)
> **เป้าหมาย:** นำเว็บแอปพลิเคชันขึ้นสู่ระบบคลาวด์สาธารณะฟรี (Streamlit Cloud) เพื่อให้กรรมการและอาจารย์สามารถเปิดดูผ่าน URL บนมือถือ แท็บเล็ต หรือคอมพิวเตอร์เครื่องใดก็ได้ โดยไม่ต้องติดตั้งโปรแกรม

---

## 🧭 สารบัญ
1. [สิ่งที่เตรียมไว้พร้อมแล้วในโปรเจกต์ (Prerequisites)](#1-สิ่งที่เตรียมไว้พร้อมแล้วในโปรเจกต์)
2. [ขั้นตอนการ Deploy แบบ Step-by-Step (5 นาทีเสร็จ)](#2-ขั้นตอนการ-deploy-แบบ-step-by-step)
3. [การตั้งค่า Advanced Settings (ถ้าจำเป็น)](#3-การตั้งค่า-advanced-settings)
4. [ข้อควรรู้เกี่ยวกับฐานข้อมูล SQLite บน Cloud (สำคัญมาก)](#4-ข้อควรรู้เกี่ยวกับฐานข้อมูล-sqlite-บน-cloud)
5. [การอัปเดตโค้ดเมื่อมีการแก้ไข (Auto Continuous Deployment)](#5-การอัปเดตโค้ดเมื่อมีการแก้ไข)

---

## 1. สิ่งที่เตรียมไว้พร้อมแล้วในโปรเจกต์

ระบบของเราได้รับการปรับแต่งให้พร้อมสำหรับการ Deploy ขึ้น Streamlit Cloud 100% แล้ว:
* ✅ **`app.py`**: ไฟล์หลักที่เป็น Entry Point และ Navigation Router
* ✅ **`requirements.txt`**: ระบุเวอร์ชันของไลบรารีที่จำเป็นครบถ้วน (`streamlit`, `pandas`, `numpy`, `scikit-learn`, `scipy`, `plotly`)
* ✅ **`.streamlit/config.toml`**: กำหนดธีมสีและการแสดงผลของหน้าจอ
* ✅ **Auto-Seed Database Engine**: มีระบบตรวจจับใน `auth.py` หากรันบน Cloud ครั้งแรกแล้วไม่พบไฟล์ `db/crm.db` ระบบจะทำการ Execute `db/seed_data.py` สร้างและบรรจุข้อมูลจำลอง (Seed 42) ให้อัตโนมัติทันที

---

## 2. ขั้นตอนการ Deploy แบบ Step-by-Step

### ขั้นที่ 1: Push โค้ดล่าสุดขึ้น GitHub
ตรวจสอบให้แน่ใจว่าโค้ดทั้งหมดถูก commit และ push ขึ้น GitHub เรียบร้อยแล้ว:
```powershell
git add .
git commit -m "Prepare project for Streamlit Cloud deployment with auto-seed DB"
git push origin master
```

---

### ขั้นที่ 2: สมัคร / เข้าสู่ระบบ Streamlit Community Cloud
1. เปิดเบราว์เซอร์ไปที่: **[share.streamlit.io](https://share.streamlit.io)**
2. คลิกปุ่ม **"Continue with GitHub"** (ล็อกอินด้วยบัญชี GitHub เดียวกับที่เก็บโค้ด)
3. อนุญาต (Authorize) ให้ Streamlit เข้าถึง Repository ใน GitHub

---

### ขั้นที่ 3: สร้าง App ใหม่ (Create App)
1. เมื่อเข้าสู่หน้า Workspace ให้มองหาปุ่มสีฟ้าที่มุมบนขวา: คลิก **"Create app"** (หรือ **"New app"**)
2. ระบบจะถามว่าจะสร้างแบบไหน ให้เลือก:
   * **"Yep, I have an existing app"**

---

### ขั้นที่ 4: กรอกข้อมูลการเชื่อมต่อ Repository
กรอกแบบฟอร์ม 3 ช่องหลัก ดังนี้:

| ช่องข้อมูล | ค่าที่ต้องกรอก / เลือก | คำอธิบาย |
|---|---|---|
| **Repository** | `ชื่อผู้ใช้ของคุณ/ddds-project` | เลือก Repo ที่เก็บโค้ดนี้ |
| **Branch** | `master` (หรือ `main`) | สาขาหลักที่ต้องการ Deploy |
| **Main file path** | `app.py` | ไฟล์จุดเริ่มต้นของระบบ |
| **App URL** *(ไม่บังคับ)* | `ddds-smart-crm` *(ตัวอย่าง)* | ตั้งชื่อ Subdomain ให้จำง่าย เช่น `ddds-smart-crm.streamlit.app` |

---

### ขั้นที่ 5: กดปุ่ม "Deploy!"
1. คลิกปุ่มสีฟ้า **"Deploy!"**
2. หน้าจอจะแสดงหน้าต่าง Terminal การติดตั้ง (Oven Cooking):
   * กำลัง Clone repository
   * กำลังติดตั้ง Dependencies จาก `requirements.txt`
   * กำลังรัน `streamlit run app.py`
   * ระบบสร้างฐานข้อมูลจำลองให้อัตโนมัติ
3. ใช้เวลาประมาณ **1 – 2 นาที** หน้าเว็บ Smart CRM จะปรากฏขึ้นมาพร้อมใช้งานทันที! 🎉

---

## 3. การตั้งค่า Advanced Settings (ถ้าจำเป็น)

ก่อนกดปุ่ม Deploy (หรือในเมนู App Settings):
* คลิก **"Advanced settings"**
* **Python Version:** แนะนำเลือกเป็น **`3.11`** (ให้ตรงกับสภาพแวดล้อมที่ใช้พัฒนา)

---

## 4. ข้อควรรู้เกี่ยวกับฐานข้อมูล SQLite บน Cloud (สำคัญมาก)

### 💡 ธรรมชาติของ Streamlit Cloud Storage (Ephemeral Container)
* **ไฟล์ฐานข้อมูล SQLite (`db/crm.db`)** บน Streamlit Cloud จะถูกเก็บในเครื่อง Virtual Container ชั่วคราว
* **เมื่อไม่มีคนใช้งานนานๆ หรือแอป Sleep ไป:**
  * เมื่อมีคนเข้ามาเปิดใหม่ คอนเทนเนอร์จะตื่นขึ้นมา และระบบ Auto-seed ของเราจะทำการรีเซ็ตข้อมูลเริ่มต้น (Seed 42) ให้ใหม่โดยอัตโนมัติ
  * **ข้อดีมหาศาล:** ทำให้ข้อมูลตัวอย่างสำหรับการ Demo ไม่เคยพัง และพร้อมสำหรับการพรีเซนต์ของคณะกรรมการหรือคนเข้ามาทดลองใช้งานเสมอ!
* **ปุ่มรีเซ็ตข้อมูลหน้าเว็บ:**
  * ปุ่ม **`🔄 รีเซ็ตฐานข้อมูล Demo`** ที่หน้า Login และ Sidebar สามารถกดบน Cloud ได้จริง ข้อมูลจะคืนค่าตั้งต้นใน 2 วินาทีเหมือนรันใน Localhost

---

## 5. การอัปเดตโค้ดเมื่อมีการแก้ไข (Auto Continuous Deployment)

Streamlit Community Cloud มีระบบ **Continuous Deployment (CI/CD)** ในตัว:
* ทุกครั้งที่คุณพิมพ์คำสั่ง:
  ```powershell
  git add .
  git commit -m "Update feature XYZ"
  git push origin master
  ```
* Streamlit Cloud จะตรวจจับการเปลี่ยนแปลงบน GitHub อัตโนมัติ และทำการ Re-deploy อัปเดตหน้าเว็บจริงให้ทันทีภายในไม่กี่วินาที โดยที่คุณไม่ต้องกดอะไรเพิ่มเลย!
