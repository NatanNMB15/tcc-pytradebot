import logging
from django.http import HttpResponse, HttpResponseServerError, HttpResponsePermanentRedirect
from django.db import connections
from django.core.cache import caches
from django.core.cache.backends.memcached import BaseMemcachedCache

LOGGER = logging.getLogger("healthz")

class HealthCheckMiddleware(object):
    """
    Classe para verificar integridade do sistema Kubernetes
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            # Teste para verificar se o container está pronto
            if request.path == "/readiness":
                return self.readiness(request)
            # Teste para verificar se o container está funcionando
            elif request.path == "/healthz":
                return self.healthz(request)
        return self.get_response(request)

    def healthz(self, request):
        """
        Metódo para retornar uma confirmação de OK (status 200) para o protocolo HTTP
        """
        return HttpResponse("OK")

    def readiness(self, request):
        """
        Metódo para realizar teste de conexão com o banco de dados
        """
        try:
            for name in connections:
                cursor = connections[name].cursor()
                cursor.execute("SELECT 1;")
                row = cursor.fetchone()
                if row is None:
                    return HttpResponseServerError("Banco de dados: erro de banco de dados.")
        except (Exception) as erro_banco:
            LOGGER.exception(erro_banco)
            return HttpResponseServerError("Banco de dados: não foi possível conectar.")

        # Chama o metódo get_stats() para conectar em todas as instâncias cache do Django 
        # e verifica o status.
        # Se todas as instâncias estiverem OK, o Django está em pleno funcionamento
        try:
            for cache in caches.all():
                if isinstance(cache, BaseMemcachedCache):
                    stats = cache._cache.get_stats()
                    if len(stats) != len(cache._servers):
                        return HttpResponseServerError("Cache: erro de cache.")
        except (Exception) as erro_cache:
            LOGGER.exception(erro_cache)
            return HttpResponseServerError("Cache: não foi possível conectar ao cache.")

        # Retorna uma confirmação de OK para o protocolo HTTP
        return HttpResponse("OK")

class NoWWWRedirectMiddleware(object):
    """
    Classe para redirecionar solicitações com WWW para sem WWW
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET":
            host = request.get_host()
            if host.startswith('www.'):
                return self.process_request(request, host)
        return self.get_response(request)

    def process_request(self, request, host):
        """
        Metódo para retirar o WWW da URL
        """
        no_www_host = host[4:]
        url = request.build_absolute_uri().replace(host, no_www_host, 1)
        return HttpResponsePermanentRedirect(url)
