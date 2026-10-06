# Agent Sentinel API + dashboard. Used by docker-compose.yml; see README "Run it with Docker".
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install ".[auth,postgres]"

# The API reads the dashboard and policies relative to the working directory.
COPY dashboard ./dashboard
COPY policies ./policies

RUN useradd --system --uid 10001 sentinel
USER sentinel

EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=3s --retries=20 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"
# 0.0.0.0 is needed inside the container; compose publishes the port on 127.0.0.1 only.
CMD ["sentinel", "serve", "--host", "0.0.0.0", "--port", "8000"]
