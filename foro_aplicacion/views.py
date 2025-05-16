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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from foro_aplicacion.menciones import procesar_menciones


def home(request):
    publicaciones = Publicacion.objects.select_related('usuario').order_by('-usuario__reputacion','-fecha_creacion') # Obtener las últimas 5 publicaciones
    return render(request, 'foro_aplicacion/home.html', {'publicaciones': publicaciones})


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

        # Comentarios principales
        comentarios = Comentario.objects.filter(
            publicacion=publicacion, comentario_padre__isnull=True
        ).order_by('fecha_creacion')
        context['comentarios'] = comentarios

        # Respuestas organizadas por comentario padre
        respuestas = Comentario.objects.filter(
            publicacion=publicacion, comentario_padre__isnull=False
        ).order_by('fecha_creacion')

        respuestas_por_comentario = {}
        for respuesta in respuestas:
            padre_id = respuesta.comentario_padre_id
            respuestas_por_comentario.setdefault(padre_id, []).append(respuesta)

        context['respuestas_por_comentario'] = respuestas_por_comentario

        # Likes y dislikes
        context['likes'] = publicacion.votos.filter(valor=1).count()
        context['dislikes'] = publicacion.votos.filter(valor=-1).count()

        # Formulario
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

            padre_id = request.POST.get('comentario_padre_id')
            if padre_id:
                try:
                    padre = Comentario.objects.get(pk=padre_id)
                    comentario.comentario_padre = padre
                    comentario.save()

                    # 🔔 Notificar al autor del comentario padre (respuesta)
                    if padre.usuario != request.user:
                        Notificacion.objects.create(
                            destinatario=padre.usuario,
                            emisor=request.user,
                            tipo='respuesta',
                            mensaje=f"{request.user.username} respondió a tu comentario en '{self.object.titulo}'",
                            url=request.build_absolute_uri(self.object.get_absolute_url())
                        )
                except Comentario.DoesNotExist:
                    comentario.save()
            else:
                comentario.save()

                # 🔔 Notificar al autor de la publicación (nuevo comentario)
                if self.object.usuario != request.user:
                    Notificacion.objects.create(
                        destinatario=self.object.usuario,
                        emisor=request.user,
                        tipo='comentario',
                        mensaje=f"{request.user.username} comentó en tu publicación '{self.object.titulo}'",
                        url=request.build_absolute_uri(self.object.get_absolute_url())
                    )

            # 🔔 Notificaciones por menciones
            mencionados = procesar_menciones(comentario.contenido)
            for usuario in mencionados:
                if usuario != request.user and usuario != self.object.usuario:
                    Notificacion.objects.create(
                        destinatario=usuario,
                        emisor=request.user,
                        tipo='mencion',
                        mensaje=f"{request.user.username} te mencionó en un comentario en '{self.object.titulo}'",
                        url=request.build_absolute_uri(self.object.get_absolute_url()) + f"#comentario-{comentario.id}"
                    )

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
# VISTA EDITAR PUBLICACION
######################

class PublicacionUpdateView(LoginRequiredMixin, UpdateView):
    model = Publicacion
    template_name = 'publicaciones/editar_publicacion.html'
    fields = ['titulo', 'cuerpo', 'categoria', 'etiquetas']
    def get_success_url(self):
        return reverse_lazy('detalle_publicacion', kwargs={'pk': self.object.pk})


######################
# VISTA votar
######################

def crear_voto(request, pk):
    if request.method == 'POST' and request.user.is_authenticated:
        publicacion = get_object_or_404(Publicacion, pk=pk)
        valor = int(request.POST.get('valor'))

        voto_existente = Voto.objects.filter(usuario=request.user, publicacion=publicacion).first()
        if voto_existente:
            diferencia = valor - voto_existente.valor
            publicacion.usuario.reputacion += diferencia * 5

            if publicacion.usuario.reputacion < 0:
                publicacion.usuario.reputacion = 0

            publicacion.usuario.save()

            voto_existente.valor = valor
            voto_existente.save()

        else:
            Voto.objects.create(usuario=request.user, publicacion=publicacion, valor=valor)

            publicacion.usuario.reputacion += valor * 5

            if publicacion.usuario.reputacion < 0:
                publicacion.usuario.reputacion = 0

            publicacion.usuario.save()

        # Crear notificación solo si no es el autor quien vota
        if request.user != publicacion.usuario:
            tipo = 'like' if valor == 1 else 'dislike'
            Notificacion.objects.create(
                destinatario=publicacion.usuario,
                emisor=request.user,
                tipo=tipo,
                mensaje=f"{request.user.username} ha dado un {tipo} a tu publicación '{publicacion.titulo}'",
                url=request.build_absolute_uri(publicacion.get_absolute_url())
            )

        return redirect('detalle_publicacion', pk=pk)

    return redirect('login')


######################
# VISTA votar COMENTARIO
######################

@login_required
def votar_comentario(request, comentario_id, pk):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, pk=comentario_id)
        valor = int(request.POST.get('valor'))

        voto_existente = VotoComentario.objects.filter(usuario=request.user, comentario=comentario).first()

        if voto_existente:
            diferencia = valor - voto_existente.valor
            comentario.usuario.reputacion += diferencia * 2
            voto_existente.valor = valor
            voto_existente.save()
        else:
            VotoComentario.objects.create(usuario=request.user, comentario=comentario, valor=valor)
            comentario.usuario.reputacion += valor * 2

        # Asegurar que la reputación no sea negativa
        if comentario.usuario.reputacion < 0:
            comentario.usuario.reputacion = 0
        comentario.usuario.save()

        # Notificación si no es el autor votando su propio comentario
        if request.user != comentario.usuario:
            tipo = 'like' if valor == 1 else 'dislike'
            Notificacion.objects.create(
                destinatario=comentario.usuario,
                emisor=request.user,
                tipo=tipo,
                mensaje=f"{request.user.username} ha dado un {tipo} a tu comentario en '{comentario.publicacion.titulo}'",
                url=request.build_absolute_uri(comentario.publicacion.get_absolute_url())
            )

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


######################
# VISTA SUBIR FOTO DE PERFIL
#####################

@login_required
def subir_imagen(request):
    usuario = request.user

    if request.method == 'POST' and 'avatar' in request.FILES:
        usuario.avatar = request.FILES['avatar']
        usuario.save()
        messages.success(request, "Imagen de perfil actualizada correctamente.")
        return redirect('perfil_usuario', usuario_id=usuario.id)

    return render(request, 'foro_aplicacion/subir_imagen.html')

######################
# VISTA ELIMINAR COMENTARIO
#####################

class ComentarioDeleteView(LoginRequiredMixin, View):
    @method_decorator(login_required)
    def post(self, request, pk):
        comentario = get_object_or_404(Comentario, pk=pk)
        
        # Verifica si el usuario es el autor o es admin
        if comentario.usuario == request.user or request.user.es_admin:
            comentario.delete()
        
        return redirect('detalle_publicacion', pk=comentario.publicacion.pk)
    
######################
# VISTA EDITAR COMENTARIO
#####################

@login_required
def editar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)

    if request.user != comentario.usuario and not request.user.es_admin:
        raise PermissionDenied

    if request.method == 'POST':
        nuevo_contenido = request.POST.get('contenido', '').strip()
        if nuevo_contenido:
            comentario.contenido = nuevo_contenido
            comentario.save()

    # Redirige al detalle de la publicación usando reverse()
    return redirect('detalle_publicacion', pk=comentario.publicacion.pk)


######################
# VISTA VER NOTIFICACIONES
#####################
@login_required
def ver_notificaciones(request):
    notificaciones = request.user.notificaciones.order_by('-fecha')
    cantidad_no_leidas = request.user.notificaciones.filter(leida=False).count()
    notificaciones.update(leida=True)  # Opcional
    return render(request, 'foro_aplicacion/notificaciones.html', {
        'notificaciones': notificaciones,
        'cantidad_no_leidas': cantidad_no_leidas
    })