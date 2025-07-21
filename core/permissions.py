# permissions.py
from rest_framework import permissions
from api.cuser.models import CustomUser

class IsSameOrganization(permissions.BasePermission):
    """
    Permiso personalizado que solo permite acceder a usuarios de la misma organización
    o a administradores/staff.
    """
    def has_permission(self, request, view):
        # Permite listar/crear solo si el usuario está autenticado
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permite operaciones sobre un objeto específico solo si:
        # - El objeto pertenece a la misma organización (acceso por usuario relacionado)
        return (getattr(obj, 'dirigido', None) and obj.dirigido.organizacion == request.user.organizacion)
    
class IsSameOrganizationAndAdmin(permissions.BasePermission):
    """
    Permiso personalizado que solo permite acceder a usuarios de la misma organización
    o a administradores/staff.
    """
    def has_permission(self, request, view):
        # Permite listar/crear solo si el usuario está autenticado
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permite operaciones sobre un objeto específico solo si:
        # - El objeto pertenece a la misma organización
        return (
            getattr(obj, 'dirigido', None) and obj.dirigido.organizacion == request.user.organizacion
        ) and request.user.groups.filter(name='admin').exists()
    
class IsSameOrganizationDeveloper(permissions.BasePermission):
    """
    Permiso personalizado que solo permite acceder a usuarios de la misma organización
    o a administradores/staff.
    """
    def has_permission(self, request, view):
        # Permite listar/crear solo si el usuario está autenticado
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Permite operaciones sobre un objeto específico solo si:
        # - El objeto pertenece a la misma organización
        return (
            getattr(obj, 'dirigido', None) and obj.dirigido.organizacion == request.user.organizacion
        ) and request.user.groups.filter(name='developer').exists()
    
class IsOwnerOrOrgAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user or
            request.user.is_staff or
            request.user.groups.filter(name='admin').exists()
        )
    
class IsSuperUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
    
class HasStoragePermission(permissions.BasePermission):
    """
    Permiso personalizado que permite el acceso a los usuarios que tienen permisos de almacenamiento.
    """
    def has_permission(self, request, view):
        # Permite el acceso si el usuario tiene el permiso 'can_access_storage'
        return request.user.has_perm('api.cuser.can_access_storage')

    def has_object_permission(self, request, view, obj):
        # Permite operaciones sobre un objeto específico si el usuario tiene el permiso
        return request.user.has_perm('api.cuser.can_access_storage')