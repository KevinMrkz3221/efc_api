from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsSuperUser
from .models import Licencia
from .serializers import LicenciaSerializer

from api.logger.mixins import LoggingMixin
# Create your views here.

class ViewSetLicencia(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for Licencia model.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]

    queryset = Licencia.objects.all()
    serializer_class = LicenciaSerializer
    filterset_fields = ['nombre', 'descripcion', 'fecha_emision']

    my_tags = ['Licencias']

    def perform_create(self, serializer):
        """
        Override to add custom logic for creating a Licencia.
        """
        if not self.request.user.is_authenticated:
            raise ValueError("Usuario no autenticado")
        
        # If superuser, allow creating without organization
        if self.request.user.is_superuser:
            serializer.save()
        else:
            raise ValueError("Solo los superusuarios pueden crear licencias sin organización asignada")

    def perform_update(self, serializer):
        """
        Override to add custom logic for updating a Licencia.
        """
        if not self.request.user.is_authenticated:
            raise ValueError("Usuario no autenticado")
        
        # If superuser, allow updating without organization
        if self.request.user.is_superuser:
            serializer.save()
        else:
            raise ValueError("Solo los superusuarios pueden actualizar licencias sin organización asignada")

    def perform_destroy(self, instance):
        """
        Override to add custom logic for deleting a Licencia.
        """
        if not self.request.user.is_authenticated:
            raise ValueError("Usuario no autenticado")
        
        # If superuser, allow deleting without organization
        if self.request.user.is_superuser:
            instance.delete()
        else:
            raise ValueError("Solo los superusuarios pueden eliminar licencias sin organización asignada")
