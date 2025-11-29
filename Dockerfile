FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY api_watcher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

COPY api_watcher/ ./api_watcher/

RUN mkdir -p snapshots logs

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "api_watcher.watcher"]
