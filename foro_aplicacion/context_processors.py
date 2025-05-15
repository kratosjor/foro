from .models import *

def cantidad_notificaciones(request):
    if request.user.is_authenticated:
        cantidad = request.user.notificaciones.filter(leida=False).count()
        return {'cantidad_no_leidas': cantidad}
    return {}