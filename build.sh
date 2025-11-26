#!/usr/bin/env bash
# Build script para Render

set -o errexit  # Exit on error

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio de archivos estáticos si no existe
mkdir -p staticfiles

# Recopilar archivos estáticos
python manage.py collectstatic --noinput --clear

