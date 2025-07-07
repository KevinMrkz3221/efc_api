from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def jwt_required_swagger_schema(**kwargs):
    """
    Decorador para endpoints que requieren autenticación JWT
    """
    security_requirement = [{'Bearer': []}]
    
    # Obtener las respuestas existentes o crear un diccionario vacío
    responses = kwargs.get('responses', {})
    
    # Agregar respuesta 401 para endpoints autenticados
    responses[401] = openapi.Response(
        description="No autorizado - Token JWT requerido",
        examples={
            'application/json': {
                'detail': 'Given token not valid for any token type',
                'code': 'token_not_valid',
                'messages': [
                    {
                        'token_class': 'AccessToken',
                        'token_type': 'access',
                        'message': 'Token is invalid or expired'
                    }
                ]
            }
        }
    )
    
    # Agregar respuesta 403 para problemas de permisos
    responses[403] = openapi.Response(
        description="Acceso denegado - Permisos insuficientes",
        examples={
            'application/json': {
                'detail': 'No tiene permisos para realizar esta acción.'
            }
        }
    )
    
    kwargs['responses'] = responses
    kwargs['security'] = security_requirement
    
    return swagger_auto_schema(**kwargs)


# Headers comunes para autenticación
JWT_AUTH_HEADER = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="JWT Token - Formato: Bearer {token}",
    type=openapi.TYPE_STRING,
    required=True
)