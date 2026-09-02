"""fixtures ร่วม — จัดการ seed ฐานข้อมูลจำลองก่อนเทสต์"""
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
os.environ.setdefault("PYTHONUTF8", "1")


def seed() -> None:
    """สร้าง db/crm.db ใหม่จากศูนย์ (deterministic, seed=42)"""
    subprocess.run([sys.executable, "db/seed_data.py"], cwd=ROOT, check=True,
                   capture_output=True)


USERS = {
    "admin":     dict(employee_id="EMP001", username="admin1",
                      name="ธนวัฒน์ บริหารดี", role="admin",
                      department="ฝ่ายบริหาร", position="ผู้ดูแลระบบ"),
    "marketing": dict(employee_id="EMP002", username="marketing1",
                      name="ชนิกานต์ การตลาด", role="marketing",
                      department="ฝ่ายการตลาด", position="นักการตลาด"),
    "sales":     dict(employee_id="EMP004", username="sale1",
                      name="ณัฐวุฒิ ขายเก่ง", role="sales",
                      department="ฝ่ายขาย", position="พนักงานขาย"),
    "support":   dict(employee_id="EMP008", username="cs1",
                      name="ศุภชัย ซัพพอร์ต", role="support",
                      department="ฝ่ายบริการลูกค้า", position="เจ้าหน้าที่บริการลูกค้า"),
    "guest":     dict(employee_id=None, username="guest", name="ผู้เยี่ยมชม",
                      role="guest", department="-", position="-"),
}


@pytest.fixture(scope="session", autouse=True)
def _seed_once():
    seed()


@pytest.fixture
def fresh_db():
    """re-seed ก่อนเทสต์ที่แก้ข้อมูล"""
    seed()
    yield


@pytest.fixture
def db():
    import sqlite3

    def _q(sql, *args):
        con = sqlite3.connect(os.path.join(ROOT, "db", "crm.db"))
        try:
            return con.execute(sql, args).fetchall()
        finally:
            con.close()
    return _q
