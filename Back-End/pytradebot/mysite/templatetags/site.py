from django import template
from django.conf import settings
from django.contrib.sites.models import Site

register = template.Library()

@register.simple_tag
def current_domain():
    """
    Metódo para retornar a Tag do domínio do Site
    """
    url = ''
    # Se estiver com Debug ativo utiliza protocolo HTTP
    if settings.DEBUG:
        url = 'http://' + Site.objects.get_current().domain
    # Senão utiliza protocolo HTTPS
    else:
        url = 'https://' + Site.objects.get_current().domain
    return url
