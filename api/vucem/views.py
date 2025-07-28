from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated


from .serializers import VucemSerializer
from .models import Vucem
from  core.permissions import IsSameOrganizationDeveloper
from rest_framework import mixins

from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)

class CustomVucemPagination(PageNumberPagination):
    """
    Paginación personalizada para VUCEM
    """
    page_size = None  # Sin paginación por defecto
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = 'page'
    
    def paginate_queryset(self, queryset, request, view=None):
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size is None:
            return None
        return super().paginate_queryset(queryset, request, view)
# Create your views here.

class VucemView(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated &  (IsSuperUser | IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper )]

    serializer_class = VucemSerializer  
    queryset = Vucem.objects.all()
    pagination_class = CustomVucemPagination
    filterset_fields = ['organizacion', 'patente', 'usuario', 'is_importador', 'acusecove', 'acuseedocument', 'is_active']
    search_fields = ['usuario', 'patente']
    ordering_fields = ['created_at', 'updated_at', 'usuario', 'patente']
    ordering = ['-created_at']

    def get_queryset(self):
        # Verificar que el usuario esté autenticado y tenga organización
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        if self.request.user.is_superuser:
            # Si es superusuario, devolver todos los registros
            return self.queryset.all()
        
        if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
            return self.queryset.none()
            
        return self.queryset.filter(organizacion=self.request.user.organizacion)