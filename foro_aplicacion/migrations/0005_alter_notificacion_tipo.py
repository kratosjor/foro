# Generated by Django 5.2 on 2025-05-15 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foro_aplicacion', '0004_notificacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacion',
            name='tipo',
            field=models.CharField(choices=[('like', 'Like a tu publicación'), ('dislike', 'Dislike a tu publicación'), ('comentario', 'Comentario en tu publicación'), ('respuesta', 'Respuesta a tu comentario'), ('mencion', 'Mención en una publicación o comentario')], max_length=20),
        ),
    ]
