from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.permissions import IsSameOrganizationAndAdmin
from .models import DataStage
from .serializer import DataStageSerializer

from api.logger.mixins import LoggingMixin
# Create your views here.

class DataStageViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing DataStage instances.
    Provides CRUD operations for DataStage.
    """
    
    serializer_class = DataStageSerializer
    permission_classes = [IsAuthenticated]

    my_tags = ['DataStage']

    def get_queryset(self):
        """
        Returns DataStages only for the requesting user's organization.
        """
        # Verificar que el usuario esté autenticado y tenga organización
        if not self.request.user.is_authenticated:
            return DataStage.objects.none()
        
        if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
            return DataStage.objects.none()
            
        return DataStage.objects.filter(organizacion=self.request.user.organizacion)
    
    