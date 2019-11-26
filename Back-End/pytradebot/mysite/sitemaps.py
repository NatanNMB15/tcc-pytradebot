from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    """
    Classe para Sitemaps estáticos dos navegadores de busca
    """
    priority = 0.5
    changfreq = 'daily'

    def items(self):
        """
        Metódo para retornar os items de URL a partir da View index
        """
        return ['index', 'index_graficos', 'quemsomos', 'valores', 'cadastro', 'login']

    def location(self, item):
        """
        Metódo para retornar as URL da View index
        """
        return reverse(item)
