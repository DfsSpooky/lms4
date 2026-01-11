import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='trim')
def trim(value):
    """Elimina espacios en blanco al inicio y al final de la cadena."""
    if isinstance(value, str):
        return value.strip()
    return value

@register.filter(name='sanitize')
def sanitize_html(value):
    """
    Sanitizes HTML content using bleach, removing any possibility of injecting 
    unsupported CSS style arguments.
    """
    if not value:
        return ""

    allowed_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
        'p', 'br', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'table', 'tbody',
        'tr', 'td', 'th', 'thead', 'u', 's', 'pre', 'iframe'
    ]

    allowed_attributes = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen']
    }

    # FIX FINAL: Se llama a bleach.clean() sin el argumento de estilos.
    # Esto resuelve la incompatibilidad de versiones al no depender de 'styles' ni 'allowed_css_properties'.
    try:
        cleaned_text = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    except Exception as e:
        # En caso de que ocurra otro error, usamos el método más seguro (aunque básico).
        print(f"Bleach fallback error: {e}")
        cleaned_text = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    return mark_safe(cleaned_text)