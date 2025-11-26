#!/usr/bin/env bash
# Start script para Render

set -o errexit  # Exit on error

# Aplicar migraciones de forma segura
# Primero aplicar solo las migraciones de misterK
python manage.py migrate misterK

# Intentar aplicar las migraciones de auth, si falla usar --fake
python manage.py migrate auth || python manage.py migrate auth --fake-initial || true

# Aplicar todas las demás migraciones
python manage.py migrate

# Iniciar servidor
gunicorn mainApp.wsgi:application
