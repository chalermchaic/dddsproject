.PHONY: install install-dev seed run docker check test e2e evidence analytics zip clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt
	python -m playwright install chromium

seed:
	python db/seed_data.py

run:
	streamlit run app.py

docker:
	docker compose up --build

check:
	python bootstrap.py --check

analytics:
	python -m analytics.lead_scoring
	python -m analytics.rfm_segmentation
	python -m analytics.churn_health
	python -m analytics.campaign_roi

test:               ## ชั้น 1 + 2 (เร็ว, ไม่ใช้ browser)
	python db/seed_data.py
	pytest -q

e2e:                ## ชั้น 3 — Playwright
	pytest tests/e2e -q --browser chromium

evidence:           ## ถ่ายภาพหลักฐาน UI จริงครบ 14 กิจกรรม + ประกอบ docs/evidence/README.md
	python tests/e2e/capture_manual_evidence.py
	python tests/e2e/build_report.py

zip:
	python bootstrap.py

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache uploads \
	       db/crm.db db/crm.db-wal db/crm.db-shm
