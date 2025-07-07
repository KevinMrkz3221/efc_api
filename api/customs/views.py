from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsSameOrganizationAndAdmin,IsSameOrganizationDeveloper
from api.customs.models import Pedimento, AgenteAduanal, Aduana, ClavePedimento, TipoOperacion, ProcesamientoPedimento, Regimen
from api.customs.serializers import PedimentoSerializer, AgenteAduanalSerializer, ClavePedimentoSerializer, AduanaSerializer, TipoOperacionSerializer, ProcesamientoPedimentoSerializer, RegimenSerializer
from api.logger.mixins import LoggingMixin


class CustomPagination(PageNumberPagination):
    """
    Paginación personalizada con parámetros flexibles
    - Si no se especifica page_size, devuelve todos los resultados (sin paginación)
    - Si se especifica page_size, usa paginación normal
    """
    page_size = None  # Sin paginación por defecto
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Límite máximo de seguridad
    page_query_param = 'page'
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Si no se especifica page_size en los parámetros, devolver None (sin paginación)
        Si se especifica, usar paginación normal
        """
        # Verificar si se especificó page_size en la query
        if self.page_size_query_param not in request.query_params:
            # No hay page_size, devolver None para indicar "sin paginación"
            return None
        
        # Hay page_size, usar paginación normal
        try:
            page_size = int(request.query_params[self.page_size_query_param])
            if page_size <= 0:
                return None
            # Establecer el page_size temporalmente para esta request
            self.page_size = min(page_size, self.max_page_size)
        except (ValueError, TypeError):
            return None
            
        return super().paginate_queryset(queryset, request, view)
# Create your views here.
class ViewSetPedimento(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for Pedimento model.
    Soporta paginación, filtros y búsqueda.
    
    Parámetros disponibles:
    - page: Número de página (solo si se especifica page_size)
    - page_size: Elementos por página (si NO se especifica, devuelve TODOS los resultados)
    - search: Búsqueda en pedimento, contribuyente, agente_aduanal
    - patente: Filtro por patente
    - aduana: Filtro por aduana
    - tipo_operacion: Filtro por tipo de operación
    - clave_pedimento: Filtro por clave de pedimento
    - ordering: Ordenar por campo (ej: -created_at, pedimento)
    
    Ejemplos:
    - /pedimentos/ → Devuelve TODOS los pedimentos
    - /pedimentos/?page_size=10 → Devuelve los primeros 10
    - /pedimentos/?page_size=10&page=2 → Devuelve los pedimentos 11-20
    """
    permission_classes = [IsAuthenticated, IsSameOrganizationDeveloper]
    serializer_class = PedimentoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['patente', 'aduana', 'tipo_operacion', 'clave_pedimento']
    search_fields = ['pedimento', 'contribuyente', 'agente_aduanal']
    ordering_fields = ['created_at', 'updated_at', 'pedimento', 'contribuyente']
    ordering = ['-created_at']

    def get_queryset(self):
        # Verificar que el usuario esté autenticado y tenga organización
        if not self.request.user.is_authenticated:
            return Pedimento.objects.none()
        
        if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
            return Pedimento.objects.none()
            
        return Pedimento.objects.filter(
            organizacion=self.request.user.organizacion,
            organizacion__is_active=True,
            organizacion__is_verified=True
        )

    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un pedimento.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")
        serializer.save(organizacion=self.request.user.organizacion)

    my_tags = ['Pedimentos']

class ViewSetAgenteAduanal(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for AgenteAduanal model.
    """
    permission_classes = [IsAuthenticated, IsSameOrganizationDeveloper]
    queryset = AgenteAduanal.objects.all()
    serializer_class = AgenteAduanalSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id_aduana', 'id_patente']
    search_fields = ['nombre', 'patente']
    ordering_fields = ['nombre', 'patente']
    ordering = ['nombre']

    my_tags = ['Agentes_Aduanales']

class ViewSetAduana(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for Aduana model.
    """
    permission_classes = [IsAuthenticated]
    queryset = Aduana.objects.all()
    serializer_class = AduanaSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['aduana']
    search_fields = ['nombre', 'aduana']
    ordering_fields = ['nombre', 'aduana']
    ordering = ['nombre']
    
    my_tags = ['Aduanas']

class ViewSetClavePedimento(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for ClavePedimento model.
    """
    permission_classes = [IsAuthenticated]
    queryset = ClavePedimento.objects.all()
    serializer_class = ClavePedimentoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['clave']
    search_fields = ['clave', 'descripcion']
    ordering_fields = ['clave', 'descripcion']
    ordering = ['clave']
    
    my_tags = ['Claves_Pedimento']

class ViewSetTipoOperacion(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for TipoOperacion model.
    """
    permission_classes = [IsAuthenticated]
    queryset = TipoOperacion.objects.all()
    serializer_class = TipoOperacionSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo']
    search_fields = ['tipo', 'descripcion']
    ordering_fields = ['tipo', 'descripcion']
    ordering = ['tipo']
    
    my_tags = ['Tipos_Operacion']

class ViewSetProcesamientoPedimento(viewsets.ModelViewSet):
    """
    ViewSet for ProcesamientoPedimento model.
    Soporta paginación, filtros y búsqueda.
    
    Parámetros disponibles:
    - page: Número de página (solo si se especifica page_size)
    - page_size: Elementos por página (si NO se especifica, devuelve TODOS los resultados)
    - pedimento: Filtro por pedimento
    - estado: Filtro por estado
    - servicio: Filtro por servicio
    - tipo_procesamiento: Filtro por tipo de procesamiento
    - ordering: Ordenar por campo (ej: -created_at, -updated_at)
    
    Ejemplos:
    - /procesamientopedimentos/ → Devuelve TODOS los procesamientos
    - /procesamientopedimentos/?page_size=5 → Devuelve los primeros 5
    """
    permission_classes = [IsAuthenticated, IsSameOrganizationDeveloper]
    serializer_class = ProcesamientoPedimentoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['pedimento', 'estado', 'servicio', 'tipo_procesamiento']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Verificar que el usuario esté autenticado y tenga organización
        if not self.request.user.is_authenticated:
            return ProcesamientoPedimento.objects.none()
        
        if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
            return ProcesamientoPedimento.objects.none()
            
        return ProcesamientoPedimento.objects.filter(
            pedimento__organizacion=self.request.user.organizacion,
            pedimento__organizacion__is_active=True,
            pedimento__organizacion__is_verified=True
        )
    
    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un procesamiento de pedimento.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")
        serializer.save(organizacion=self.request.user.organizacion)
    
    my_tags = ['Procesamientos_Pedimentos']

class ViewSetRegimen(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for Regimen model.
    """
    permission_classes = [IsAuthenticated]
    queryset = Regimen.objects.all()
    serializer_class = RegimenSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['clave']
    search_fields = ['clave', 'descripcion']
    ordering_fields = ['clave', 'descripcion']
    ordering = ['clave']
    
    my_tags = ['Regimenes']