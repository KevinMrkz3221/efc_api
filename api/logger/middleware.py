import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import RequestLog, ErrorLog

logger = logging.getLogger('django')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Calcular tiempo de respuesta
        response_time = (time.time() - getattr(request, 'start_time', 0)) * 1000
        
        # Obtener información del usuario
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        
        # Obtener IP del cliente
        ip_address = self.get_client_ip(request)
        
        # Obtener query parameters
        query_params = dict(request.GET) if request.GET else {}
        
        # Obtener body de la request (solo para POST, PUT, PATCH)
        body = ""
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body'):
                    body = request.body.decode('utf-8')[:1000]  # Limitar a 1000 caracteres
            except Exception:
                body = "Could not decode body"
        
        # Crear log de la request
        try:
            RequestLog.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                method=request.method,
                path=request.path,
                query_params=json.dumps(query_params),
                body=body,
                status_code=response.status_code,
                response_time=response_time,
                referer=request.META.get('HTTP_REFERER', '')
            )
        except Exception as e:
            logger.error(f"Error logging request: {e}")
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ErrorLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        import traceback
        
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        ip_address = self.get_client_ip(request)
        
        try:
            ErrorLog.objects.create(
                level='ERROR',
                message=str(exception),
                traceback=traceback.format_exc(),
                user=user,
                ip_address=ip_address,
                request_path=request.path
            )
        except Exception as e:
            logger.error(f"Error logging exception: {e}")
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip