FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    TZ=Asia/Bangkok \
    CRM_DB_PATH=/app/db/crm.db \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# ฟอนต์ไทย (สำหรับ matplotlib/wordcloud) + sqlite CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
        sqlite3 fonts-thai-tlwg curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x docker/entrypoint.sh

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# entrypoint จะ seed db/crm.db ให้ถ้ายังไม่มี แล้วจึงเปิด Streamlit
ENTRYPOINT ["/app/docker/entrypoint.sh"]
