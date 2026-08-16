from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """Desabilita cache do navegador em modo desenvolvimento."""

    def process_response(self, request, response):
        if settings.DEBUG:
            # Aplica headers anti-cache para todas as respostas
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            # Remove Last-Modified para forçar revalidação
            if 'Last-Modified' in response:
                del response['Last-Modified']
        return response
