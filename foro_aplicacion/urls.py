from django.urls import path
from .views import *

urlpatterns = [
    # Define tus rutas aquí
    path('', home, name='home'),
    path('login/',LoginUsuarioView.as_view(), name='login'),
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),
    
    ###CATEGORIAS###
    path('categorias/listar/', CategoriaListView.as_view(), name='listar'),
    path('categorias/crear/', CategoriaCreateView.as_view(), name='crear_categoria'),
    path('categorias/eliminar_categoria/<int:pk>/', CategoriaDeleteView.as_view(), name='eliminar_categoria'),
    
    
    ###PUBLICACIONES###
    path('publicaciones/listar/', PublicacionListView.as_view(), name='listar_publicaciones'),
    path('publicaciones/crear/', PublicacionCreateView.as_view(), name='crear_publicacion'),
    path('publicaciones/crear_etiqueta/', EtiquetaCreateView.as_view(), name='crear_etiqueta'),
    path('publicaciones/detalle/<int:pk>', PublicacionDetailView.as_view(), name='detalle_publicacion'),
    path('comentario/<int:pk>/eliminar/', EliminarComentarioView.as_view(), name='eliminar_comentario'),
    path('publicaciones/eliminar_publicacion/<int:pk>/', EliminarPublicacionView.as_view(), name='eliminar_publicacion'),
    path('publicaciones/categoria/<int:categoria_id>/', publicaciones_por_categoria, name='publicaciones_por_categoria'),
    path('publicaciones/editar_publicacion/<int:pk>/', PublicacionUpdateView.as_view(), name='editar_publicacion'),
    path('publicaciones/eliminar_comentario/<int:pk>/', ComentarioDeleteView.as_view(), name='eliminar_comentario'),
    path('comentarios/<int:pk>/editar/', editar_comentario, name='editar_comentario'),


    #usuarios
    path('lista_usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:pk>/asignar_rol/', AsignarRolView.as_view(), name='asignar_rol'),  

    #voto
    path('votar/<int:pk>/', crear_voto, name='crear_voto'),
    path('comentarios/votar/<int:comentario_id>/', votar_comentario, name='votar_comentario'),

    
    
    #perfil
    path('perfil/<int:usuario_id>/', perfil_usuario, name='perfil_usuario'),
    path('perfil/subir_imagen/', subir_imagen, name='subir_imagen'),
    
    #notificaciones
    path('notificaciones/', ver_notificaciones, name='ver_notificaciones'),
    path('comentario/<int:comentario_id>/votar/<int:pk>/', votar_comentario, name='votar_comentario'),



]
