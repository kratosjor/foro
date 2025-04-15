from django.urls import path
from .views import *

urlpatterns = [
    # Define tus rutas aquí
    path('', home, name='home'),
    path('login/',LoginUsuarioView.as_view(), name='login'),
    path('registro/', RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),
    path('categorias/listar/', CategoriaListView.as_view(), name='listar'),
    path('categorias/crear/', CategoriaCreateView.as_view(), name='crear_categoria'),


]