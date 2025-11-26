#!/usr/bin/env bash
# Start script para Render

set -o errexit  # Exit on error

# Aplicar migraciones de misterK primero
python manage.py migrate misterK

# Marcar como fake las migraciones problemáticas de auth si es necesario
python manage.py migrate auth 0002 --fake || true
python manage.py migrate auth 0003 --fake || true

# Aplicar todas las demás migraciones
python manage.py migrate || true

# Aplicar migraciones de contenttypes, sessions, admin
python manage.py migrate contenttypes || true
python manage.py migrate sessions || true
python manage.py migrate admin || true

# Iniciar servidor
gunicorn mainApp.wsgi:application
