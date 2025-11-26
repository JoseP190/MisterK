from django.db import models
from django.core.exceptions import ValidationError
import re

# Create your models here.

def validar_rut(rut):
    """
    Valida el formato de RUT chileno (ej: 12345678-9)
    Solo valida el formato, no el dígito verificador
    """
    # Limpiar el RUT (quitar puntos y convertir a mayúsculas)
    rut_limpio = rut.replace('.', '').replace('-', '').upper()
    
    # Validar que tenga el formato correcto: números seguidos de un dígito verificador (0-9 o K)
    # Mínimo 7 dígitos en el cuerpo (RUT chileno mínimo) y máximo 9 dígitos
    if not re.match(r'^[0-9]{7,9}[0-9K]$', rut_limpio):
        raise ValidationError('El RUT debe tener el formato correcto (ej: 12345678-9). Debe tener entre 7 y 9 dígitos seguidos de un guión y un dígito verificador (0-9 o K)')
    
    return rut_limpio
class Categorias(models.Model):
    nombre_categoria = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre_categoria

class Productos(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.IntegerField()
    descripcion = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    oferta = models.BooleanField(default=False) 
    porcentajeOferta = models.IntegerField()  
    imagen = models.ImageField(upload_to='productos/',null=True,blank=True)
    # agregadosRelacionados = models.CharField(max_length=50) debe ser una lista
    
    def precio_con_descuento(self):
        if self.oferta:
            return int(round(self.precio * (1 - self.porcentajeOferta / 100)))
        return self.precio

    def __str__(self):
        return self.nombre


class Agregados(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.IntegerField()
    # productosRelacionado = models.CharField(max_length=50) debe ser una lista
    

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre_completo = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.rut}"
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Confirmado', 'Confirmado'),
        ('Entregado', 'Entregado'),
    ]
    
    FORMA_PAGO_CHOICES = [
        ('Transferencia', 'Transferencia'),
        ('Efectivo', 'Efectivo'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    productos = models.JSONField()  # Almacena los productos del carrito como JSON
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    total = models.IntegerField()
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.nombre_completo} - {self.estado}"
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']


