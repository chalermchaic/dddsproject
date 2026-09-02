#!/bin/sh
set -e

# seed ฐานข้อมูลอัตโนมัติถ้ายังไม่มี (เช่น first run หลัง mount volume ว่าง)
DB_PATH="${CRM_DB_PATH:-db/crm.db}"
if [ ! -f "$DB_PATH" ]; then
    echo "⏳ ไม่พบ $DB_PATH — กำลังสร้างฐานข้อมูล + ข้อมูลจำลอง..."
    python db/seed_data.py
fi

exec streamlit run app.py
