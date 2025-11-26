from misterK.models import Usuario

def usuario_sesion(request):
    """Context processor para hacer disponible el usuario de la sesión en todos los templates"""
    usuario_sesion = None
    usuario_rut = request.session.get('usuario_rut', None)
    if usuario_rut:
        try:
            usuario_sesion = Usuario.objects.get(rut=usuario_rut)
        except Usuario.DoesNotExist:
            pass
    return {'usuario_sesion': usuario_sesion}

