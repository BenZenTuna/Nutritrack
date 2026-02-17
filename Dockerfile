FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV NUTRITRACK_DB_PATH=/app/data/nutritrack.db
ENV NUTRITRACK_HOST=0.0.0.0
ENV NUTRITRACK_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/profile')" || exit 1

CMD ["python3", "app.py"]
