"""
Database connection helper — Smart CRM (SQLite)
รองรับทั้งการเรียกจาก Streamlit (มี cache) และเรียกจากสคริปต์ธรรมดา
"""
import os
import sqlite3
from contextlib import contextmanager

import pandas as pd

DB_PATH = os.getenv("CRM_DB_PATH", os.path.join("db", "crm.db"))
UPLOAD_DIR = os.getenv("CRM_UPLOAD_DIR", "uploads")


def save_upload(uploaded_file, prefix: str = "file") -> str:
    """เก็บไฟล์ที่ผู้ใช้อัปโหลด (เช่น สลิปโอนเงิน) ลง uploads/ แล้วคืนชื่อไฟล์"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(getattr(uploaded_file, "name", ""))[1] or ".bin"
    fname = f"{prefix}{ext}"
    with open(os.path.join(UPLOAD_DIR, fname), "wb") as fh:
        fh.write(uploaded_file.getbuffer())
    return fname


@contextmanager
def get_conn(readonly: bool = False):
    """เปิด connection พร้อมเปิด FK และปิดให้อัตโนมัติ"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"ไม่พบฐานข้อมูลที่ {DB_PATH} — รัน `python db/seed_data.py` ก่อน"
        )
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    try:
        yield con
        if not readonly:
            con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def run_query(sql: str, params: tuple | dict = ()) -> pd.DataFrame:
    """SELECT → DataFrame"""
    with get_conn(readonly=True) as con:
        return pd.read_sql_query(sql, con, params=params)


def execute(sql: str, params: tuple | dict = ()) -> int:
    """INSERT / UPDATE / DELETE → จำนวนแถวที่กระทบ"""
    with get_conn() as con:
        cur = con.execute(sql, params)
        return cur.rowcount


def execute_many(sql: str, rows: list[tuple]) -> int:
    with get_conn() as con:
        cur = con.executemany(sql, rows)
        return cur.rowcount


def next_id(table: str, col: str, prefix: str, width: int = 4) -> str:
    """สร้าง Running ID ถัดไป เช่น LD0601"""
    df = run_query(f"SELECT MAX({col}) AS mx FROM {table}")
    mx = df.iloc[0]["mx"]
    n = int(str(mx)[len(prefix):]) + 1 if mx else 1
    return f"{prefix}{n:0{width}d}"


def table_counts() -> pd.DataFrame:
    """สรุปจำนวนเรคคอร์ดทุกตาราง (ใช้บนหน้า Dashboard)"""
    tables = ["EMPLOYEE", "CAMPAIGN", "PRODUCT", "LEAD", "LEAD_ACTIVITY", "SALE",
              "SALE_DETAIL", "CUSTOMER", "TICKET", "TICKET_MESSAGE"]
    sql = " UNION ALL ".join(
        [f"SELECT '{t}' AS table_name, COUNT(*) AS n FROM {t}" for t in tables]
    )
    return run_query(sql)


# ---------- Streamlit cache wrapper (ใช้เมื่อรันในแอปเท่านั้น) ----------
try:
    import streamlit as st

    @st.cache_data(ttl=300, show_spinner=False)
    def cached_query(sql: str, params: tuple = ()) -> pd.DataFrame:
        return run_query(sql, params)

except ModuleNotFoundError:      # รันนอก Streamlit
    def cached_query(sql: str, params: tuple = ()) -> pd.DataFrame:
        return run_query(sql, params)