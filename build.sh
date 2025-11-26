#!/usr/bin/env bash
# Build script para Render

set -o errexit  # Exit on error

# Instalar dependencias
pip install -r requirements.txt

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

