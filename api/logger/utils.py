from django.contrib.auth.models import User
from .models import UserActivity, ErrorLog
import logging

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_user_activity(user, action, object_type='', object_id='', description='', request=None):
    """
    Registra actividad del usuario
    
    Args:
        user: Usuario que realiza la acción
        action: Tipo de acción (login, logout, create, update, delete, view, search, export, import)
        object_type: Tipo de objeto afectado (opcional)
        object_id: ID del objeto afectado (opcional)
        description: Descripción adicional (opcional)
        request: Request object para obtener IP (opcional)
    """
    ip_address = '127.0.0.1'
    if request:
        ip_address = get_client_ip(request)
    
    try:
        UserActivity.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=str(object_id) if object_id else '',
            description=description,
            ip_address=ip_address
        )
    except Exception as e:
        logging.error(f"Error logging user activity: {e}")

def log_error(level, message, traceback='', user=None, request=None):
    """
    Registra errores personalizados
    
    Args:
        level: Nivel del error (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Mensaje del error
        traceback: Traceback del error (opcional)
        user: Usuario relacionado (opcional)
        request: Request object (opcional)
    """
    ip_address = None
    request_path = ''
    
    if request:
        ip_address = get_client_ip(request)
        request_path = request.path
    
    try:
        ErrorLog.objects.create(
            level=level,
            message=message,
            traceback=traceback,
            user=user,
            ip_address=ip_address,
            request_path=request_path
        )
    except Exception as e:
        logging.error(f"Error logging custom error: {e}")

# Decorador para loggear automáticamente acciones
def log_action(action, object_type=''):
    """
    Decorador para loggear automáticamente acciones en vistas
    
    Usage:
        @log_action('create', 'Pedimento')
        def create_pedimento(request):
            # tu código aquí
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            
            if hasattr(request, 'user') and request.user.is_authenticated:
                object_id = kwargs.get('pk', kwargs.get('id', ''))
                log_user_activity(
                    user=request.user,
                    action=action,
                    object_type=object_type,
                    object_id=object_id,
                    request=request
                )
            
            return result
        return wrapper
    return decorator