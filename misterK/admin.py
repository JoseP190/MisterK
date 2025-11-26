from django.contrib import admin
from misterK.models import Productos,Categorias,Agregados,Usuario,Pedido

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre','precio','descripcion','categoria','oferta','porcentajeOferta']
admin.site.register(Productos,ProductoAdmin)

class CategoriasAdmin(admin.ModelAdmin):
    list_display = ['nombre_categoria']
admin.site.register(Categorias,CategoriasAdmin)

class AgregadosAdmin(admin.ModelAdmin):
    list_display = ['nombre','precio']
admin.site.register(Agregados,AgregadosAdmin)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'rut', 'fecha_registro']
    search_fields = ['nombre_completo', 'rut']
    readonly_fields = ['fecha_registro']
admin.site.register(Usuario, UsuarioAdmin)

class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'forma_pago', 'total', 'fecha_pedido']
    list_filter = ['estado', 'forma_pago', 'fecha_pedido']
    search_fields = ['usuario__nombre_completo', 'usuario__rut']
    readonly_fields = ['fecha_pedido', 'fecha_actualizacion']
    date_hierarchy = 'fecha_pedido'
admin.site.register(Pedido, PedidoAdmin)