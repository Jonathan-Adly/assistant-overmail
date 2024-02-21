#!/bin/bash

# Exit script if any command fails
set -e

# Collect static files
#echo "Collecting static files..."
#python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Start Gunicorn with Django
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2