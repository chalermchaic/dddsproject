.PHONY: install seed run docker check test zip clean

install:
	pip install -r requirements.txt

seed:
	python db/seed_data.py

run:
	streamlit run app.py

docker:
	docker compose up --build

check:
	python bootstrap.py --check

test:
	python -m analytics.lead_scoring
	python -m analytics.rfm_segmentation
	python -m analytics.churn_health
	python -m analytics.campaign_roi

zip:
	python bootstrap.py

clean:
	rm -rf __pycache__ */__pycache__ db/crm.db db/crm.db-wal db/crm.db-shm
