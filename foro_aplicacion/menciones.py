import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='procesar_menciones')
def procesar_menciones(texto):
    if not texto:
        return ''

    def reemplazar_mencion(match):
        username = match.group(1)
        return f'<span class="mention">@{username}</span>'

    resultado = re.sub(r'@(\w+)', reemplazar_mencion, texto)
    return mark_safe(resultado)
