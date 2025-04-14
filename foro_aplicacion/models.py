from django.db import models
from django.contrib.auth.models import AbstractUser

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

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


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

    def __str__(self):
        return self.titulo


######################
# Comentario
######################
class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
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
