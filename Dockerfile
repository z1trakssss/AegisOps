# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md ./
COPY app ./app
RUN python -m pip install --prefix=/install .

FROM python:3.12-slim AS runtime

ENV PATH="/home/aegis/.local/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 aegis \
    && useradd --uid 10001 --gid aegis --create-home --shell /usr/sbin/nologin aegis

COPY --from=builder /install /usr/local
USER 10001:10001
WORKDIR /home/aegis

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]

CMD ["uvicorn", "orders_api.main:app", "--host=0.0.0.0", "--port=8080", "--no-access-log"]

