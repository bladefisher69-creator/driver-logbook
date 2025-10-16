#!/bin/sh
set -e

# Activate venv if present (containers usually don't need venv)
# Run migrations then start Daphne ASGI server

echo "Running migrations..."
python manage.py makemigrations --noinput || true
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput || true

# Start Daphne (ASGI) on port 8000
echo "Starting Daphne..."
# Allow overriding the port via PORT env var (Render provides $PORT)
PORT=${PORT:-8000}
exec daphne -b 0.0.0.0 -p "$PORT" config.asgi:application
