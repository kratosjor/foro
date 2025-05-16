from django import template
import re
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def resaltar_menciones(texto):
    """
    Busca @usuarios en el texto y les aplica un <span> con clase CSS.
    """
    texto = escape(texto)  # evita inyección de HTML

    def reemplazar(match):
        nombre_usuario = match.group(1)
        return f'<span class="mencion">@{nombre_usuario}</span>'

    resultado = re.sub(r'@(\w+)', reemplazar, texto)
    return mark_safe(resultado)
