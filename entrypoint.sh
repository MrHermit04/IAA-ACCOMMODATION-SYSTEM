#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading initial data..."
python manage.py loaddata data.json

echo "Creating superuser if not exists..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'kizitorj04@gmail.com', 'admin2025')" | python manage.py shell

echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
