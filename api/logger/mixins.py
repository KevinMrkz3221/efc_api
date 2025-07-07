from .utils import log_user_activity

class LoggingMixin:
    """
    Mixin para añadir logging automático a ViewSets
    """
    log_actions = True
    log_object_type = None
    
    def get_log_object_type(self):
        """Obtiene el tipo de objeto del modelo del ViewSet"""
        if self.log_object_type:
            return self.log_object_type
        
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model.__name__
        
        if hasattr(self, 'model') and self.model is not None:
            return self.model.__name__
            
        return self.__class__.__name__.replace('ViewSet', '')
    
    def perform_create(self, serializer):
        """Override para loggear creaciones"""
        instance = serializer.save()
        
        if self.log_actions and self.request.user.is_authenticated:
            log_user_activity(
                user=self.request.user,
                action='create',
                object_type=self.get_log_object_type(),
                object_id=instance.pk,
                description=f'Creado {self.get_log_object_type()} {instance.pk}',
                request=self.request
            )
        
        return instance
    
    def perform_update(self, serializer):
        """Override para loggear actualizaciones"""
        instance = serializer.save()
        
        if self.log_actions and self.request.user.is_authenticated:
            log_user_activity(
                user=self.request.user,
                action='update',
                object_type=self.get_log_object_type(),
                object_id=instance.pk,
                description=f'Actualizado {self.get_log_object_type()} {instance.pk}',
                request=self.request
            )
        
        return instance
    
    def perform_destroy(self, instance):
        """Override para loggear eliminaciones"""
        object_id = instance.pk
        object_type = self.get_log_object_type()
        
        instance.delete()
        
        if self.log_actions and self.request.user.is_authenticated:
            log_user_activity(
                user=self.request.user,
                action='delete',
                object_type=object_type,
                object_id=object_id,
                description=f'Eliminado {object_type} {object_id}',
                request=self.request
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Override para loggear visualizaciones de detalle"""
        response = super().retrieve(request, *args, **kwargs)
        
        if self.log_actions and request.user.is_authenticated:
            instance = self.get_object()
            log_user_activity(
                user=request.user,
                action='view',
                object_type=self.get_log_object_type(),
                object_id=instance.pk,
                description=f'Visto detalle de {self.get_log_object_type()} {instance.pk}',
                request=request
            )
        
        return response
    
    def list(self, request, *args, **kwargs):
        """Override para loggear listados"""
        response = super().list(request, *args, **kwargs)
        
        if self.log_actions and request.user.is_authenticated:
            log_user_activity(
                user=request.user,
                action='view',
                object_type=self.get_log_object_type(),
                object_id='',
                description=f'Visto listado de {self.get_log_object_type()}',
                request=request
            )
        
        return response