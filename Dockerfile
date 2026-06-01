# ── E-Shop Django — production image ────────────────────────────────────────────
FROM python:3.12-slim

# Python runtime tuning
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies (PostgreSQL client libs + build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Project source
COPY . .

# Collect static files at build time (uses a throwaway secret).
RUN SECRET_KEY=build-time DJANGO_SETTINGS_MODULE=ecommerce.settings \
    python manage.py collectstatic --noinput

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "ecommerce.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
