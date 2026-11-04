FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY docs ./docs

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -e . --no-deps || true

EXPOSE 8080
CMD ["python", "-m", "app.main"]
