#!/bin/sh
set -e

# Wait for the database to be reachable (PostgreSQL).
if [ -n "$DB_HOST" ]; then
    echo "En attente de la base de données sur $DB_HOST:$DB_PORT..."
    while ! python -c "import socket,os,sys; s=socket.socket(); s.settimeout(2); \
        sys.exit(0) if not s.connect_ex((os.environ.get('DB_HOST'), int(os.environ.get('DB_PORT', 5432)))) else sys.exit(1)" 2>/dev/null; do
        sleep 1
    done
    echo "Base de données disponible."
fi

# Apply database migrations.
python manage.py migrate --noinput

# Collect static files (safe to run again at startup).
python manage.py collectstatic --noinput

# Optionally create a superuser from environment variables.
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell <<PYTHON
from django.contrib.auth import get_user_model
U = get_user_model()
email = "$DJANGO_SUPERUSER_EMAIL"
if not U.objects.filter(email=email).exists():
    U.objects.create_superuser(email=email, password="$DJANGO_SUPERUSER_PASSWORD",
                               first_name="Admin", last_name="Principal")
    print("Superutilisateur créé:", email)
PYTHON
fi

exec "$@"
