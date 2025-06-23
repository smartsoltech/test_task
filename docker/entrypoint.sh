#!/bin/bash
set -e

echo "✅ Запуск миграций..."
python manage.py migrate

echo "✅ Сборка статики..."
python manage.py collectstatic --noinput

echo "🚀 Запуск Django на 0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000
