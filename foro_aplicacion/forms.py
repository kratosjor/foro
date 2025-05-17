from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

######################
# Registro de Usuario
######################
class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'correo', 'password1', 'password2','avatar']

######################
# Edición de Usuario (Admin/Moderador)
######################
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'correo', 'first_name', 'last_name', 
            'es_admin', 'es_baneado', 'es_moderador', 'es_autor'
        ]

######################
# Categoría
######################
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'usuario']

######################
# Publicación
######################
class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['titulo', 'cuerpo', 'categoria', 'etiquetas','imagen','video']
    
    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')

        if imagen:
            max_tamano = 10 * 1024 * 1024  # 10 MB
            tamano = imagen.size

            if tamano > max_tamano:
                raise forms.ValidationError("La imagen es demasiado grande. El tamaño máximo permitido es 10 MB.")

            # Puedes agregar etiquetas si quieres mostrar el tipo
            if tamano <= 1 * 1024 * 1024:
                self.tamano_imagen = 'Pequeña'
            elif tamano <= 5 * 1024 * 1024:
                self.tamano_imagen = 'Mediana'
            else:
                self.tamano_imagen = 'Grande'

        return imagen

######################
# Comentario
######################
class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']

######################
# Voto
######################
class VotoForm(forms.ModelForm):
    class Meta:
        model = Voto
        fields = ['valor']

######################
# Etiqueta
######################
class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre']

######################
# Publicación-Etiqueta (relación manual)
######################
class PublicacionEtiquetaForm(forms.ModelForm):
    class Meta:
        model = PublicacionEtiqueta
        fields = ['publicacion', 'etiqueta']