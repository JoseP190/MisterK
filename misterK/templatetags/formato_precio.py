from django import template

register = template.Library()

@register.filter(name='formato_precio')
def formato_precio(value):
    """
    Formatea un número como precio chileno: sin decimales, con puntos como separadores de miles
    Ejemplo: 10400 -> "10.400", 29000 -> "29.000"
    """
    try:
        # Convertir a entero para eliminar decimales
        numero = int(float(value))
        # Formatear con puntos como separadores de miles
        return f"{numero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value

