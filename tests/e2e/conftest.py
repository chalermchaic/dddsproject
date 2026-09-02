"""
ชั้น 3 — Playwright e2e: บูต streamlit จริง แล้วถ่าย screenshot เป็นหลักฐาน
รัน: pytest tests/e2e --browser chromium
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
EVIDENCE = os.path.join(ROOT, "docs", "evidence")


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


@pytest.fixture(scope="session")
def app_url():
    os.makedirs(EVIDENCE, exist_ok=True)
    subprocess.run([sys.executable, "db/seed_data.py"], cwd=ROOT, check=True,
                   capture_output=True, env={**os.environ, "PYTHONUTF8": "1"})
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.port", str(port), "--server.headless", "true",
         "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        env={**os.environ, "PYTHONUTF8": "1"})
    base = f"http://localhost:{port}"
    for _ in range(60):
        try:
            if urllib.request.urlopen(base + "/_stcore/health", timeout=2).status == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        proc.terminate()
        raise RuntimeError("streamlit ไม่ขึ้นภายในเวลาที่กำหนด")
    yield base
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()


@pytest.fixture
def page(page):
    page.set_default_timeout(20000)
    return page


def shot(page, name: str) -> None:
    page.wait_for_timeout(800)
    page.screenshot(path=os.path.join(EVIDENCE, f"{name}.png"), full_page=True)


def login_as(page, base_url, username: str) -> None:
    page.goto(base_url, wait_until="networkidle")
    if username == "guest":
        page.get_by_role("button", name="เข้าเป็นผู้สนใจ / ลูกค้า (จำลอง)").click()
    else:
        page.get_by_role("button", name=f"เข้าใช้งานเป็น {username}").click()
    page.wait_for_timeout(1500)
