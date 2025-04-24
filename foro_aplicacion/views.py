from django.shortcuts import render
from .models import *
from .forms import *
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.core.paginator import Paginator


def home(request):
    return render(request, 'foro_aplicacion/home.html')


######################
# VISTA PARA INICIO DE SESIÓN DE USUARIO
######################


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etiquetas'] = Etiqueta.objects.all()
        return context
    

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
# VISTA PUBLICACIONES POR CATEGORIA
######################    

def publicaciones_por_categoria(request, categoria_id):
    publicaciones = Publicacion.objects.filter(categoria_id=categoria_id)
    return render(request, 'publicaciones/listar_por_categoria.html', {'publicaciones': publicaciones})
    

######################
# VISTA detalle PUBLICACION
######################

class PublicacionDetailView(FormMixin, DetailView):
    model = Publicacion
    template_name = 'publicaciones/detalle.html'
    context_object_name = 'publicacion'
    form_class = ComentarioForm

    def get_success_url(self):
        return reverse('detalle_publicacion', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publicacion = self.get_object()

        # Comentarios
        context['comentarios'] = Comentario.objects.filter(publicacion=publicacion).order_by('fecha_creacion')

        # Likes y Dislikes
        context['likes'] = publicacion.votos.filter(valor=1).count()
        context['dislikes'] = publicacion.votos.filter(valor=-1).count()

        # Formulario de comentarios
        if 'form' not in context:
            context['form'] = self.get_form()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect('login')

        form = self.get_form()
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.usuario = request.user
            comentario.publicacion = self.object
            comentario.save()
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
        
######################
# VISTA ELIMINAR COMENTARIO 
######################

class EliminarComentarioView(LoginRequiredMixin, DeleteView):
    model = Comentario
    template_name = 'publicaciones/eliminar_comentario.html'
    context_object_name = 'comentario'
    def get_success_url(self):
        return reverse('detalle_publicacion', kwargs={'pk': self.object.pk})


######################
# VISTA crear publicacion
######################

class PublicacionCreateView(LoginRequiredMixin, CreateView):
    model = Publicacion
    fields = ['titulo','cuerpo','categoria','etiquetas']
    template_name = 'publicaciones/crear.html'
    success_url = reverse_lazy('listar_publicaciones')
    
        
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

######################
# VISTA ELIMINAR PUBLICACION
######################

class EliminarPublicacionView(LoginRequiredMixin, DeleteView):
    model = Publicacion
    template_name = 'publicaciones/eliminar_publicacion.html'
    context_object_name = 'publicacion'
    
    def get_success_url(self):
        return reverse('listar_publicaciones')



######################
# VISTA votar
######################

def crear_voto(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        publicacion = get_object_or_404(Publicacion, pk=pk)
        valor = int(request.POST.get('valor'))

        # Opcional: evitar votos repetidos del mismo usuario
        voto_existente = Voto.objects.filter(usuario=request.user, publicacion=publicacion).first()
        if voto_existente:
            voto_existente.valor = valor
            voto_existente.save()
        else:
            Voto.objects.create(usuario=request.user, publicacion=publicacion, valor=valor)

        return redirect('detalle_publicacion', pk=pk)
    return redirect('login')


######################
# VISTA CREAR ETIQUETA
#####################

class EtiquetaCreateView(LoginRequiredMixin, CreateView):
    model = Etiqueta
    fields = ['nombre']
    template_name = 'publicaciones/crear_etiqueta.html'
    success_url = reverse_lazy('listar')

######################
# VISTA LISTA DE USUARIOS
#####################

def lista_usuarios(request):
    nombre = request.GET.get('nombre', '')
    usuarios = Usuario.objects.all()

    if nombre:
        usuarios = usuarios.filter(username__icontains=nombre)

    # Paginación: mostrar 10 usuarios por página
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    usuarios_paginados = paginator.get_page(page_number)

    return render(request, 'foro_aplicacion/lista_usuarios.html', {
        'usuarios': usuarios_paginados,
        'nombre': nombre  # Para mantener el valor del campo en la barra de búsqueda
    })



######################
# VISTA ASIGNAR ROLES DE USUARIOS
#####################

class AsignarRolView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Usuario
    fields = ['es_admin','es_baneado','es_moderador','es_autor']
    template_name = 'foro_aplicacion/asignar_rol.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        user = self.request.user
        # Si no hay admins aún, permitir acceso al primer usuario autenticado
        if not Usuario.objects.filter(es_admin=True).exists():
            return user.is_authenticated
        # Si ya hay admins, solo ellos pueden acceder
        return user.is_authenticated and user.es_admin


#def listado_de_pacientes(request):
#    pacientes = Paciente.objects.all()
#    formulario = Buscar_PacienteForm(request.GET)
#    
#    if formulario.is_valid():
#        nombre_a_buscar = formulario.cleaned_data.get('nombre')
#        if nombre_a_buscar:
#            pacientes = Paciente.objects.filter(nombre__icontains=nombre_a_buscar)
#            
#    return render(request, 'RegistroPacientes/listado_de_pacientes.html', {'pacientes': pacientes, "formulario":formulario})

######################
# VISTA PERFIL DE USUARIO
#####################

def perfil_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    publicaciones = Publicacion.objects.filter(usuario=usuario).order_by('fecha_creacion')
    comentarios = Comentario.objects.filter(usuario=usuario).order_by('fecha_creacion')
    
    return render(request, 'foro_aplicacion/perfil_usuario.html', {
        'usuario': usuario,
        'publicaciones': publicaciones,
        'comentarios': comentarios
    })


