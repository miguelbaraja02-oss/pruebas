from django import template
import time

register = template.Library()

@register.filter
def avatar_url_cache_bust(avatar):
    """Añade un timestamp a la URL del avatar para evitar caché del navegador"""
    if avatar and hasattr(avatar, 'url'):
        timestamp = int(time.time())
        return f"{avatar.url}?v={timestamp}"
    return ""
