FROM python:3.14-slim

ARG VALIDATOR_COMMIT=5955c71bbba9ceb7bde39f19730c925a0ce1e9c7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DATA_DIR=/app/data

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-app.txt ./
RUN pip install --no-cache-dir -r requirements-app.txt \
    && pip install --no-cache-dir "ttml-validator @ git+https://github.com/bbc/ttml-validator.git@${VALIDATOR_COMMIT}"

COPY app ./app
COPY templates ./templates
COPY knowledge ./knowledge
COPY schemas ./schemas

RUN mkdir -p /app/data && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
