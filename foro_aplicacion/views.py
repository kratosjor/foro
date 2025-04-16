from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import reverse_lazy


def home(request):
    return render(request, 'foro_aplicacion/home.html')


######################
# VISTA PARA INICIO DE SESIÓN DE USUARIO
######################

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

class LoginUsuarioView(LoginView):
    template_name = 'foro_aplicacion/login_usuario.html'
    redirect_authenticated_user = True  # Redirige si ya está logueado

    def get_success_url(self):
        return reverse_lazy('home')


######################
# VISTA PARA REGISTRO DE USUARIO
######################


class RegistroUsuarioView(CreateView):
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = 'foro_aplicacion/registro_usuario.html'
    success_url = '/foro/'  # Redirigir a la página principal del foro después del registro 

######################
# VISTA logout voiew
######################

class LogoutUsuarioView(LogoutView):
    next_page = 'login'

######################
# VISTA PARA UPTADE DE USUARIO
######################

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'foro_aplicacion/editar_usuarrio.html'
    success_url = '/foro/'  # Redirigir a la página principal del foro después de la edición
    

######################
#LISTA DE CATEGORIAS
#######################

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'categorias/listar.html'
    

######################
# VISTA CREAR CATEGORIA
######################

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    fields = ['nombre', 'descripcion']
    template_name = 'categorias/crear_categoria.html'
    success_url = reverse_lazy('listar')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
    
######################
# VISTA ELIMINAR CATEGORIA
######################

class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'categorias/eliminar_categoria.html'
        
    def get_success_url(self):
        return reverse_lazy('listar')
    

######################
# VISTA LISTA PUBLICACIONES
######################

class PublicacionListView(ListView):
    model = Publicacion
    template_name = 'publicaciones/listar.html'
    context_object_name = 'publicaciones'
    

######################
# VISTA detalle PUBLICACION
######################

class PublicacionDetailView(DetailView):
    model = Publicacion
    template_name = 'publicaciones/detalle.html'

######################
# VISTA crear publicacion
######################

class PublicacionCreateView(LoginRequiredMixin, CreateView):
    model = Publicacion
    fields = ['titulo','cuerpo','categoria','etiquetas']
    template_name = 'publicaciones/crear.html'
    success_url = reverse_lazy('publicaciones')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


######################
# VISTA agregar comentario
######################

def agregar_comentario(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.nethod == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario  = request.user
            comentario.publicacion = publicacion
            comentario.save()
            return redirect('foro_aplicacion:detalle_publicacion', pk=publicacion.pk)
    
    else:
        form = ComentarioForm()
    return render(request, 'comentarios/agregar.html',{'form':form})


######################
# VISTA votar
######################

def votar (request, publicacion_id, valor):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    voto, created = Voto.objects.update_or_create(
        publicacion = publicacion,
        usuario = request.user,
        defaults={'valor': valor}
    )
    return HttpResponseRedirect(reverse('detalle_publicacion', args=[publicacion.id]))  # No content, solo actualiza el voto sin redirigir


######################
# VISTA CREAR ETIQUETA
#####################

class EtiquetaCreateView(LoginRequiredMixin, CreateView):
    model = Etiqueta
    fields = ['nombre']
    template_name = 'publicaciones/crear_etiqueta.html'
    success_url = reverse_lazy('listar_publicaciones')
