from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils import timezone
from django.urls import reverse


######################
# Usuario personalizado
######################
class Usuario(AbstractUser):
    correo = models.EmailField(max_length=100, unique=True)
    es_admin = models.BooleanField(default=False)
    es_baneado = models.BooleanField(default=False)
    es_moderador = models.BooleanField(default=False)
    es_autor = models.BooleanField(default=False)
    reputacion = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    @property
    def avatar_url(self):
        # Si no hay avatar, usar una imagen predeterminada en static
        if not self.avatar:
            return static('assets/img/default_avatar.png')
        return self.avatar.url


######################
# Categoría
######################
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='categorias')

    def __str__(self):
        return self.nombre


######################
# Etiqueta
######################
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre


######################
# Publicación
######################
class Publicacion(models.Model):
    titulo = models.CharField(max_length=100)
    cuerpo = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='publicaciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='publicaciones')
    etiquetas = models.ManyToManyField(Etiqueta, through='PublicacionEtiqueta', related_name='publicaciones')
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)  # 👈 NUEVO CAMPO

    def __str__(self):
        return self.titulo
    
    def get_absolute_url(self):
        return reverse('detalle_publicacion', kwargs={'pk': self.pk})


######################
# Comentario
######################
class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    comentario_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respuestas')

    def __str__(self):
        if self.comentario_padre:
            return f"{self.usuario.username} respondió a un comentario en '{self.publicacion.titulo}'"
        return f"{self.usuario.username} comentó en '{self.publicacion.titulo}'"



######################
# Voto
######################
class Voto(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTO_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='votos')
    valor = models.IntegerField(choices=VOTO_CHOICES)

    class Meta:
        unique_together = ('publicacion', 'usuario')
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'

    def __str__(self):
        return f"{self.usuario.username} votó {self.get_valor_display()} en '{self.publicacion.titulo}'"


######################
# Voto COMENTARIO
######################

class VotoComentario(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTO_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    comentario = models.ForeignKey('Comentario', on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='votos_comentarios')
    valor = models.IntegerField(choices=VOTO_CHOICES)

    class Meta:
        unique_together = ('comentario', 'usuario')
        verbose_name = 'Voto en comentario'
        verbose_name_plural = 'Votos en comentarios'

    def __str__(self):
        return f"{self.usuario.username} votó {self.get_valor_display()} en el comentario '{self.comentario.contenido[:20]}'"


######################
# Relación Publicación - Etiqueta (ManyToMany explícito)
######################
class PublicacionEtiqueta(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('publicacion', 'etiqueta')
        verbose_name = 'Etiqueta de publicación'
        verbose_name_plural = 'Etiquetas de publicaciones'

    def __str__(self):
        return f"{self.publicacion.titulo} - {self.etiqueta.nombre}"


######################
# NOTIFICACIONES
######################

class Notificacion(models.Model):
    TIPO_CHOICES =[
        ('like','Like a tu publicación'),
        ('dislike','Dislike a tu publicación'),
        ('comentario','Comentario en tu publicación'),
        ('respuesta','Respuesta a tu comentario'),
        ('mencion','Mención en una publicación o comentario'),
        
    ]
    
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones_realizadas')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    url = models.URLField()
    leida = models.BooleanField(default=False)  
    fecha = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.emisor} → {self.destinatario} ({self.tipo})"