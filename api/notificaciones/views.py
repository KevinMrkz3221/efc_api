from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notificacion, TipoNotificacion
from .serializers import NotificacionSerializer, TipoNotificacionSerializer
from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)
# Create your views here.

class TipoNotificacionViewSet(viewsets.ModelViewSet):
    queryset = TipoNotificacion.objects.all()
    serializer_class = TipoNotificacionSerializer
    http_method_names = ['get']

    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]

    my_tags = ['Notificaciones']
    
    def get_queryset(self):
        return self.queryset.order_by('tipo')

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    

    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    my_tags = ['Notificaciones']
    
    def get_queryset(self):
        
        if self.request.user.is_superuser:
            return self.Notificacion.objects.all()
        
        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists():
            return Notificacion.objects.filter(dirigido__organizacion=self.request.user.organizacion)

        if self.request.user.groups.filter(name='importador').exists():
            return Notificacion.objects.filter(dirigido=self.request.user)

    
    def perform_create(self, serializer):

        if not self.request.user.is_authenticated:
            raise PermissionDenied("Usuario no autenticado")
        
        if self.request.user.is_superuser:
            # Allow superusers and admins to create notifications for any user
            serializer.save()
        
        raise PermissionDenied("No tienes permiso para crear notificaciones para otros usuarios")