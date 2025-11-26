from django.contrib import admin
from django.urls import path
from misterK import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('agregados', views.agregados, name='agregados'),
    path('login/', views.custom_login_view, name='login'),
    path('menu', views.menu, name='menu'),
    path('ubicacion', views.ubicacion, name='ubicacion'),
    path('categoria/<int:id>/', views.categoria, name='categoria'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('obtener_agregados/', views.obtener_agregados, name='obtener_agregados'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.carrito, name='carrito'),
    path('administracion/', views.administracion, name='administracion'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('registrar_usuario/', views.registrar_usuario, name='registrar_usuario'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('estado_pedido/', views.estado_pedido, name='estado_pedido'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)