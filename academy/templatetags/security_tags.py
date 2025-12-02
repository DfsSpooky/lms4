import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='sanitize')
def sanitize_html(value):
    """
    Sanitizes HTML content using bleach.
    Allows a set of safe tags and attributes.
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

    allowed_styles = [
        'color', 'font-weight', 'background-color', 'text-align', 'font-size', 'padding', 'margin'
    ]

    cleaned_text = bleach.clean(
        value,
        tags=allowed_tags,
        attributes=allowed_attributes,
        styles=allowed_styles,
        strip=True
    )

    return mark_safe(cleaned_text)
