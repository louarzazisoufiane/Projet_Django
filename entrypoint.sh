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
password = "$DJANGO_SUPERUSER_PASSWORD"
user = U.objects.filter(email=email).first()
if user is None:
    U.objects.create_superuser(email=email, password=password,
                               first_name="Admin", last_name="Principal")
    print("Superutilisateur créé:", email)
else:
    user.is_staff = True
    user.is_superuser = True
    if hasattr(user, "role"):
        user.role = "ADMIN"
    user.set_password(password)
    user.save()
    print("Superutilisateur mis à jour:", email)
PYTHON
else
    echo "DJANGO_SUPERUSER_EMAIL/PASSWORD non définis; aucun superutilisateur créé."
fi

exec "$@"
