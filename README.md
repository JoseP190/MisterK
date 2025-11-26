# Mister K - Proyecto Django

Sistema de gestión de menú y pedidos para restaurante de hamburguesas.

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Instala las dependencias del proyecto:
```bash
pip install -r requirements.txt
```

## Ejecutar el Servidor

1. Inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```

2. Abre tu navegador y visita:
```
http://127.0.0.1:8000
```

## Funcionalidades Principales

- 🍔 Catálogo de productos con categorías
- 🛒 Carrito de compras con agregados personalizables
- 📦 Sistema de ofertas y descuentos
- 🔐 Panel de administración para gestionar productos y agregados
- 📄 Paginación (12 productos por página)

## Estructura del Proyecto

```
MisterK-Django/
├── manage.py          # Utilidad de Django
├── mainApp/           # Configuración del proyecto
├── misterK/           # Aplicación principal
├── templates/         # Plantillas HTML
├── static/            # Archivos estáticos (CSS, imágenes)
├── media/             # Archivos subidos (imágenes de productos)
└── db.sqlite3         # Base de datos
```

## Notas

- El servidor de desarrollo se ejecuta en `http://127.0.0.1:8000` por defecto
- Para detener el servidor, presiona `Ctrl+C` en la terminal
- La base de datos SQLite se crea automáticamente al ejecutar las migraciones

