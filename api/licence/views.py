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