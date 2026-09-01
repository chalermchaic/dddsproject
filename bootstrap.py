#!/usr/bin/env python3
"""
Smart CRM Analytics — Project Verifier & Packager
------------------------------------------------
ตอนนี้ไฟล์โปรเจกต์ทั้งหมดอยู่ใน repo แล้ว สคริปต์นี้จึงเหลือแค่ 2 หน้าที่:

    python bootstrap.py            # ตรวจโครงสร้าง + แพ็กเป็น .zip สำหรับส่งงาน
    python bootstrap.py --check    # ตรวจโครงสร้างอย่างเดียว (คืน exit code)
    python bootstrap.py --no-zip   # เหมือน --check

ผลตรวจ: ไฟล์สำคัญครบไหม และ import โมดูลหลักผ่านไหม
"""
from __future__ import annotations

import argparse
import importlib
import sys
import zipfile
from datetime import datetime
from pathlib import Path

PROJECT = "smart-crm-analytics"
ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    "db/schema.sql",
    "db/seed_data.py",
    "db/connection.py",
    "db/__init__.py",
    "analytics/__init__.py",
    "analytics/lead_scoring.py",
    "analytics/rfm_segmentation.py",
    "analytics/churn_health.py",
    "analytics/campaign_roi.py",
    "pages/1_📢_Marketing.py",
    "pages/2_📞_Sales_Followup.py",
    "pages/3_🧾_Order_Billing.py",
    "pages/4_👤_Customer_Profile.py",
    "pages/5_🎫_Support_Ticket.py",
    "pages/6_📊_Analytics_Dashboard.py",
    ".streamlit/config.toml",
]

# โมดูลที่ต้อง import ได้ (ไม่ต้องมี DB — แค่ syntax/deps ครบ)
IMPORT_CHECKS = [
    "db.connection",
    "analytics.lead_scoring",
    "analytics.rfm_segmentation",
    "analytics.churn_health",
    "analytics.campaign_roi",
]

# สิ่งที่ไม่แพ็กลง zip
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", ".idea", ".vscode", ".claude"}
EXCLUDE_SUFFIX = {".zip", ".pyc", ".pyo"}
EXCLUDE_NAMES = {"crm.db", "crm.db-wal", "crm.db-shm"}


def check_files() -> list[str]:
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).exists()]
    for f in REQUIRED_FILES:
        mark = "✅" if (ROOT / f).exists() else "❌"
        print(f"  {mark} {f}")
    return missing


def check_imports() -> list[str]:
    sys.path.insert(0, str(ROOT))
    failed = []
    for mod in IMPORT_CHECKS:
        try:
            importlib.import_module(mod)
            print(f"  ✅ import {mod}")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"{mod}: {exc}")
            print(f"  ❌ import {mod} — {exc}")
    return failed


def run_check() -> bool:
    print("── ตรวจไฟล์ที่จำเป็น ─────────────────────────────")
    missing = check_files()
    print("\n── ตรวจการ import โมดูลหลัก ─────────────────────")
    failed = check_imports()

    print()
    if missing:
        print(f"❌ ไฟล์ขาด {len(missing)} รายการ: {', '.join(missing)}")
    if failed:
        print(f"❌ import ไม่ผ่าน {len(failed)} โมดูล")
    if not missing and not failed:
        print("✅ ผ่านทั้งหมด — โปรเจกต์พร้อมรัน (อย่าลืม `python db/seed_data.py` ก่อนครั้งแรก)")
        return True
    return False


def make_zip() -> Path:
    stamp = datetime.now().strftime("%Y%m%d")
    out = ROOT / f"{PROJECT}_{stamp}.zip"
    if out.exists():
        out.unlink()

    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT)
            if set(rel.parts) & EXCLUDE_DIRS:
                continue
            if path.suffix in EXCLUDE_SUFFIX or path.name in EXCLUDE_NAMES:
                continue
            if rel.name.startswith("response") and rel.suffix == ".md":
                continue
            if rel.name.startswith(f"{PROJECT}_") and rel.suffix == ".zip":
                continue
            z.write(path, Path(PROJECT) / rel)
            count += 1
    print(f"📦 สร้าง {out.name} ({count} ไฟล์)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="ตรวจโครงสร้าง + แพ็ก zip โปรเจกต์ Smart CRM")
    ap.add_argument("--check", action="store_true", help="ตรวจอย่างเดียว ไม่แพ็ก zip")
    ap.add_argument("--no-zip", action="store_true", help="เหมือน --check")
    args = ap.parse_args()

    ok = run_check()
    if not ok:
        return 1

    if not (args.check or args.no_zip):
        make_zip()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
