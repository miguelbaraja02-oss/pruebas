from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
import os

register = template.Library()

@register.simple_tag
def static_version(path):
    """Devuelve la URL estática con ?v=<mtime> para bustear caché en desarrollo.
    Uso en template: {% static_version 'img/logo.png' %}
    """
    try:
        real_path = finders.find(path)
    except Exception:
        real_path = None

    url = static(path)
    if real_path and os.path.exists(real_path):
        try:
            ts = int(os.path.getmtime(real_path))
            return f"{url}?v={ts}"
        except Exception:
            return url
    return url
