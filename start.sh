#!/usr/bin/env bash
# Start script para Render

set +o errexit  # No salir en error para manejar migraciones problemáticas

# Aplicar migraciones de misterK primero
python manage.py migrate misterK

# Marcar como fake la migración problemática de auth antes de aplicar
python manage.py migrate auth 0003_alter_user_email_max_length --fake 2>/dev/null || true

# Aplicar todas las demás migraciones
python manage.py migrate --run-syncdb 2>/dev/null || python manage.py migrate

# Iniciar servidor
gunicorn mainApp.wsgi:application
