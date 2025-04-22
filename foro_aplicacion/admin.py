from django.contrib import admin
from .models import Categoria, Publicacion, Etiqueta, Comentario, Usuario, PublicacionEtiqueta

# Registrar modelos básicos
admin.site.register(Categoria)
admin.site.register(Publicacion)
admin.site.register(Etiqueta)
admin.site.register(Comentario)
admin.site.register(Usuario)  # Si deseas gestionar usuarios personalizados
admin.site.register(PublicacionEtiqueta)


