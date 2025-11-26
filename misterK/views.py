from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.core.exceptions import ValidationError
from misterK.models import Productos, Categorias , Agregados, Usuario, Pedido
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.

def index(request):
    
    productos_en_oferta = Productos.objects.filter(oferta=True)[:6]  
    data = {
        'productos_en_oferta': productos_en_oferta,
    }
    
    return render(request, 'index.html',data)

def agregados(request):
    
    return render(request, 'agregados.html')

def menu(request):
    productos_list = Productos.objects.all().order_by('id')
    categorias = Categorias.objects.all()
    agregados = Agregados.objects.all()
    
    # Paginación: 12 productos por página
    paginator = Paginator(productos_list, 12)
    page = request.GET.get('page')
    
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        productos = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        productos = paginator.page(paginator.num_pages)
    
    data = {
        'productos' : productos,
        'categorias' : categorias,
        'agregados' : agregados
    }
    
    return render(request, 'menu.html', data)

def ubicacion(request):
    
    return render(request, 'ubicacion.html')

def login(request):
    
    return render(request, 'login.html')

def detalle_producto(request, id):
    producto = get_object_or_404(Productos, id=id)
    categorias = Categorias.objects.all()
    productos_relacionados = Productos.objects.filter(categoria=producto.categoria).exclude(id=producto.id)[:3]
    data = {
        'producto': producto,
        'categorias' : categorias,
        'productos_relacionados' : productos_relacionados 
    }
    return render(request, 'detalle_producto.html',data)

def categoria(request,id) :
    categoria = get_object_or_404(Categorias, id=id)
    categorias = Categorias.objects.all()
    productos_list = Productos.objects.filter(categoria=categoria).order_by('id')
    
    # Paginación: 12 productos por página
    paginator = Paginator(productos_list, 12)
    page = request.GET.get('page')
    
    try:
        productos_en_categoria = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        productos_en_categoria = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página
        productos_en_categoria = paginator.page(paginator.num_pages)
    
    data = {
        'categoria':categoria,
        'categorias' : categorias,
        'productos_en_categoria': productos_en_categoria
        
    }
    return render(request,'categorias.html', data)

def carrito(request):
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito y subtotales por item
    total = 0
    carrito_con_subtotales = {}
    for key, item in carrito.items():
        subtotal = float(item['precio']) * item['cantidad']
        item['subtotal'] = subtotal
        total += subtotal
        carrito_con_subtotales[key] = item

    return render(request, 'carrito.html', {
        'carrito': carrito_con_subtotales,
        'total': total,
    })

def obtener_agregados(request):
    """Vista para obtener todos los agregados disponibles como JSON"""
    agregados = Agregados.objects.all()
    agregados_data = [{
        'id': agregado.id,
        'nombre': agregado.nombre,
        'precio': agregado.precio
    } for agregado in agregados]
    
    return JsonResponse({'agregados': agregados_data})

def agregar_carrito(request, producto_id):
    # Verificar si el usuario está registrado (tiene RUT en sesión)
    usuario_rut = request.session.get('usuario_rut', None)
    if not usuario_rut:
        return JsonResponse({
            'error': 'registro_requerido',
            'mensaje': 'Debes registrarte antes de agregar productos al carrito'
        }, status=400)
    
    producto = get_object_or_404(Productos, id=producto_id)
    
    # Obtener el carrito de la sesión (si existe)
    carrito = request.session.get('carrito', {})
    
    # Calcular el precio con descuento del producto base
    precio_producto = float(producto.precio_con_descuento())
    
    # Obtener agregados si vienen en el request (JSON)
    agregados_seleccionados = []
    precio_agregados = 0
    
    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body)
        agregados_data = data.get('agregados', [])
        
        for agregado_data in agregados_data:
            agregado = get_object_or_404(Agregados, id=agregado_data['id'])
            agregados_seleccionados.append({
                'id': agregado.id,
                'nombre': agregado.nombre,
                'precio': float(agregado.precio)
            })
            precio_agregados += float(agregado.precio)
    
    # Calcular el precio total (producto + agregados)
    precio_total = precio_producto + precio_agregados
    
    # Verifica si el producto ya está en el carrito
    if str(producto_id) in carrito:
        # Si ya existe, aumentar cantidad pero no sobrescribir agregados
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        # Si no existe, agregarlo con los agregados
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': precio_total,  # Precio total incluyendo agregados
            'precio_base': precio_producto,  # Precio del producto sin agregados
            'cantidad': 1,
            'id': producto.id,
            'agregados': agregados_seleccionados  # Lista de agregados seleccionados
        }

    # Guardar el carrito actualizado en la sesión
    request.session['carrito'] = carrito
    
    mensaje = f'Agregaste {producto.nombre} al carrito'
    if agregados_seleccionados:
        mensaje += f' con {len(agregados_seleccionados)} agregado(s)'

    return JsonResponse({
        'mensaje': mensaje,
        'carrito': carrito,
        'carrito_total': len(carrito)
    })

def eliminar_producto(request, producto_id):
    carrito = request.session.get('carrito', {})

    # Verificar si el producto está en el carrito
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]  # Eliminar el producto del carrito
        request.session['carrito'] = carrito  # Guardar los cambios en la sesión
        messages.success(request, "Producto eliminado del carrito.")
    else:
        messages.error(request, "El producto no está en el carrito.")

    # Redirigir al carrito después de eliminar el producto
    return redirect('carrito')

def iniciar_sesion(request):
    """Vista para iniciar sesión con RUT"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        rut = data.get('rut', '').strip()
        
        if not rut:
            return JsonResponse({'error': 'El RUT es obligatorio'}, status=400)
        
        # Validar y limpiar RUT
        try:
            from misterK.models import validar_rut
            rut_limpio = validar_rut(rut)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        # Buscar usuario por RUT
        try:
            usuario = Usuario.objects.get(rut=rut_limpio)
            
            # Guardar en sesión
            request.session['usuario_rut'] = rut_limpio
            request.session['usuario_nombre'] = usuario.nombre_completo
            request.session['usuario_id'] = usuario.id
            
            return JsonResponse({
                'success': True,
                'mensaje': f'Bienvenido de nuevo, {usuario.nombre_completo}',
                'usuario': {
                    'nombre': usuario.nombre_completo,
                    'rut': rut_limpio
                }
            })
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'RUT no encontrado. Por favor, regístrate primero.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error al iniciar sesión: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def registrar_usuario(request):
    """Vista para registrar un usuario antes de agregar productos al carrito"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        nombre_completo = data.get('nombre_completo', '').strip()
        rut = data.get('rut', '').strip()
        
        # Validaciones básicas
        if not nombre_completo:
            return JsonResponse({'error': 'El nombre completo es obligatorio'}, status=400)
        
        if not rut:
            return JsonResponse({'error': 'El RUT es obligatorio'}, status=400)
        
        # Validar y limpiar RUT
        try:
            from misterK.models import validar_rut
            rut_limpio = validar_rut(rut)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        # Verificar si el RUT ya existe
        if Usuario.objects.filter(rut=rut_limpio).exists():
            return JsonResponse({'error': 'Este RUT ya está registrado. Por favor, inicia sesión.'}, status=400)
        
        # Crear el usuario
        try:
            usuario = Usuario.objects.create(
                nombre_completo=nombre_completo,
                rut=rut_limpio
            )
            
            # Guardar en sesión
            request.session['usuario_rut'] = rut_limpio
            request.session['usuario_nombre'] = nombre_completo
            request.session['usuario_id'] = usuario.id
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': {
                    'nombre': nombre_completo,
                    'rut': rut_limpio
                }
            })
        except Exception as e:
            return JsonResponse({'error': f'Error al registrar usuario: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def procesar_compra(request):
    # Verificar si hay productos en el carrito
    carrito = request.session.get('carrito', {})
    usuario_rut = request.session.get('usuario_rut', None)
    forma_pago = request.POST.get('forma_pago', None)

    if not usuario_rut:
        messages.error(request, "Debes estar registrado para realizar un pedido.")
        return redirect('carrito')

    if not carrito:
        messages.error(request, "Tu carrito está vacío. No puedes realizar el pedido.")
        return redirect('carrito')
    
    if not forma_pago or forma_pago not in ['Transferencia', 'Efectivo']:
        messages.error(request, "Debes seleccionar una forma de pago.")
        return redirect('carrito')

    # Obtener el usuario
    try:
        usuario = Usuario.objects.get(rut=usuario_rut)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado. Por favor, regístrate nuevamente.")
        return redirect('carrito')
    
    # Calcular el total
    total = 0
    for item in carrito.values():
        total += float(item['precio']) * item['cantidad']
    
    # Crear el pedido
    try:
        pedido = Pedido.objects.create(
            usuario=usuario,
            productos=carrito,
            forma_pago=forma_pago,
            estado='Pendiente',
            total=int(total)
        )
        
        # Vaciar el carrito
        request.session['carrito'] = {}
        
        messages.success(request, "Pedido realizado con éxito")
        return redirect('carrito')
    except Exception as e:
        messages.error(request, f"Error al procesar el pedido: {str(e)}")
        return redirect('carrito')

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:  # Verifica si es staff (permiso de admin)
            auth_login(request, user)  # Usa auth_login en lugar de login
            return redirect('administracion')  # Redirige a la URL de administracion.html
        else:
            messages.error(request, 'Error en el nombre de usuario o la contraseña')

    return render(request, 'login.html')

def administracion(request):
    categorias = Categorias.objects.all()    # Carga todas las categorías
    usuarios = User.objects.all()           # Carga todos los usuarios
    
    # Paginación de productos: 12 productos por página
    productos_list = Productos.objects.all().order_by('id')
    paginator = Paginator(productos_list, 12)
    page = request.GET.get('page')
    
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        # Agregar nuevo producto
        if 'add_producto' in request.POST:
            nombre = request.POST['nombre']
            precio = request.POST['precio']
            producto = Productos.objects.create(nombre=nombre, precio=precio)
            
            # Manejar imagen si se subió
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
                producto.save()
            
            messages.success(request, 'Producto agregado exitosamente')
            # Mantener el parámetro de página si existe
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("administracion")}?page={page}')

        # Actualizar producto
        if 'update_producto' in request.POST:
            producto_id = request.POST['producto_id']
            producto = Productos.objects.get(id=producto_id)
            producto.nombre = request.POST['nombre']
            producto.precio = request.POST['precio']
            
            # Manejar imagen si se subió
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
            
            producto.save()
            messages.success(request, 'Producto actualizado exitosamente')
            # Mantener el parámetro de página si existe
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("administracion")}?page={page}')

        # Actualizar oferta del producto
        if 'update_oferta' in request.POST:
            producto_id = request.POST['producto_id']
            producto = Productos.objects.get(id=producto_id)
            # Verificar si se está activando o desactivando la oferta
            oferta_activa = 'oferta_activa' in request.POST
            producto.oferta = oferta_activa
            if oferta_activa:
                porcentaje = request.POST.get('porcentaje_oferta', 0)
                try:
                    producto.porcentajeOferta = int(porcentaje)
                except ValueError:
                    producto.porcentajeOferta = 0
            producto.save()
            if oferta_activa:
                messages.success(request, f'Oferta activada: {producto.nombre} con {producto.porcentajeOferta}% de descuento')
            else:
                messages.success(request, f'Oferta desactivada para {producto.nombre}')
            # Mantener el parámetro de página si existe
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("administracion")}?page={page}')

        # Eliminar producto
        if 'delete_producto' in request.POST:
            producto_id = request.POST['producto_id']
            producto = Productos.objects.get(id=producto_id)
            producto.delete()
            messages.success(request, 'Producto eliminado exitosamente')
            # Mantener el parámetro de página si existe
            page = request.GET.get('page', '1')
            return redirect(f'{reverse("administracion")}?page={page}')

        # Agregar agregado
        if 'add_agregado' in request.POST:
            nombre = request.POST['nombre']
            precio = request.POST['precio']
            Agregados.objects.create(nombre=nombre, precio=precio)
            messages.success(request, 'Agregado agregado exitosamente')
            return redirect('administracion')

        # Actualizar agregado
        if 'update_agregado' in request.POST:
            agregado_id = request.POST['agregado_id']
            agregado = Agregados.objects.get(id=agregado_id)
            agregado.nombre = request.POST['nombre']
            agregado.precio = request.POST['precio']
            agregado.save()
            messages.success(request, 'Agregado actualizado exitosamente')
            return redirect('administracion')

        # Eliminar agregado
        if 'delete_agregado' in request.POST:
            agregado_id = request.POST['agregado_id']
            agregado = Agregados.objects.get(id=agregado_id)
            agregado.delete()
            messages.success(request, 'Agregado eliminado exitosamente')
            return redirect('administracion')

        # Similarmente para Categorías y Usuarios
        # (Agregar, actualizar, eliminar categorías y usuarios de forma similar)

    agregados = Agregados.objects.all()
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    
    # Procesar cambio de estado de pedido
    if request.method == 'POST' and 'update_estado_pedido' in request.POST:
        pedido_id = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('nuevo_estado')
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido #{pedido_id} actualizado a {nuevo_estado}')
            return redirect('administracion')
        except Pedido.DoesNotExist:
            messages.error(request, 'Pedido no encontrado')
    
    data = {
        'productos': productos,
        'categorias': categorias,
        'usuarios': usuarios,
        'agregados': agregados,
        'pedidos': pedidos,
    }

    return render(request, 'administracion.html', data)

def estado_pedido(request):
    """Vista para consultar el estado del pedido usando RUT"""
    pedidos = None
    rut_buscado = None
    usuario_sesion = None
    
    # Verificar si hay un usuario en sesión
    usuario_rut = request.session.get('usuario_rut', None)
    if usuario_rut:
        try:
            usuario_sesion = Usuario.objects.get(rut=usuario_rut)
            # Obtener pedidos del usuario logueado automáticamente
            pedidos_list = Pedido.objects.filter(usuario=usuario_sesion).order_by('-fecha_pedido')
            
            # Calcular subtotales para cada producto en cada pedido
            pedidos = []
            for pedido in pedidos_list:
                productos_con_subtotal = {}
                for key, item in pedido.productos.items():
                    item_copy = item.copy()
                    item_copy['subtotal'] = float(item['precio']) * item['cantidad']
                    productos_con_subtotal[key] = item_copy
                pedido.productos = productos_con_subtotal
                pedidos.append(pedido)
        except Usuario.DoesNotExist:
            pass
    
    # Si hay un POST (búsqueda manual por RUT)
    if request.method == 'POST' and not usuario_sesion:
        rut = request.POST.get('rut', '').strip()
        if rut:
            try:
                from misterK.models import validar_rut
                rut_limpio = validar_rut(rut)
                rut_buscado = rut_limpio
                
                # Buscar usuario por RUT
                try:
                    usuario = Usuario.objects.get(rut=rut_limpio)
                    pedidos_list = Pedido.objects.filter(usuario=usuario).order_by('-fecha_pedido')
                    
                    # Calcular subtotales para cada producto en cada pedido
                    pedidos = []
                    for pedido in pedidos_list:
                        productos_con_subtotal = {}
                        for key, item in pedido.productos.items():
                            item_copy = item.copy()
                            item_copy['subtotal'] = float(item['precio']) * item['cantidad']
                            productos_con_subtotal[key] = item_copy
                        pedido.productos = productos_con_subtotal
                        pedidos.append(pedido)
                except Usuario.DoesNotExist:
                    messages.error(request, "No se encontró ningún usuario con ese RUT.")
            except ValidationError as e:
                messages.error(request, str(e))
    
    return render(request, 'estado_pedido.html', {
        'pedidos': pedidos,
        'rut_buscado': rut_buscado,
        'usuario_sesion': usuario_sesion
    })

def cerrar_sesion(request):
    """Vista para cerrar sesión del usuario"""
    # Limpiar la sesión
    request.session.flush()
    # Cerrar sesión de Django si está autenticado
    if request.user.is_authenticated:
        auth_logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('index')