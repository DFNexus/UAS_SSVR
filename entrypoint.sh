#!/bin/bash
set -e

echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Generating database migrations..."
python manage.py makemigrations users categories courses enrollments progress

echo "Applying database migrations..."
python manage.py migrate

echo "Seeding demo data..."
python manage.py seed_demo_data

echo "Starting server..."
exec "$@"
