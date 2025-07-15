from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DataStage
from .serializer import DataStageSerializer

from api.logger.mixins import LoggingMixin
from mixins.filtrado_organizacion import OrganizacionFiltradaMixin
from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)
# Create your views here.

class DataStageViewSet(LoggingMixin, viewsets.ModelViewSet, OrganizacionFiltradaMixin):
    """
    ViewSet for managing DataStage instances.
    Provides CRUD operations for DataStage.
    """
    
    serializer_class = DataStageSerializer
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = DataStage

    my_tags = ['DataStage']

    def get_queryset(self):
        return self.filter_queryset_by_organization()

    def perform_create(self, serializer):
        """
        Override to set the organization automatically on creation.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")

        if self.request.user.is_superuser:
            # Allow superuser to create without organization
            serializer.save()
            return
        
        if (self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            serializer.save(organizacion=self.request.user.organizacion)

        raise ValueError("No cuentas con los permisos necesarios para crear un DataStage")
    
    def perform_update(self, serializer):
        """
        Override to ensure organization is set on update.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")

        if self.request.user.is_superuser:
            # Allow superuser to update without organization
            serializer.save()
            return
        
        if (self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            serializer.save(organizacion=self.request.user.organizacion)
        
        raise ValueError("No cuentas con los permisos necesarios para actualizar un DataStage")
    