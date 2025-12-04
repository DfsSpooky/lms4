import nh3
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
    Sanitizes HTML content using nh3 (ammonia), replacing bleach.
    """
    if not value:
        return ""

    allowed_tags = {
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
        'p', 'br', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'table', 'tbody',
        'tr', 'td', 'th', 'thead', 'u', 's', 'pre', 'iframe'
    }

    allowed_attributes = {
        '*': {'class', 'style'},
        'a': {'href', 'title', 'target'},
        'img': {'src', 'alt', 'width', 'height'},
        'iframe': {'src', 'width', 'height', 'frameborder', 'allowfullscreen'}
    }

    try:
        # nh3.clean(html, tags=..., attributes=...)
        # attributes should be a dict of tag -> set of attributes
        # '*' acts as global allowed attributes in nh3 as well.
        cleaned_text = nh3.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            # strip_comments=True is default
            # link_rel='noopener noreferrer' is default for 'a' tags in some cases, or configurable
        )
    except Exception as e:
        print(f"nh3 error: {e}")
        # Fallback or re-raise. For now return empty or safe minimal.
        # But nh3 is robust.
        return mark_safe("")

    return mark_safe(cleaned_text)
