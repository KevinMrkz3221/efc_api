from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)
from api.customs.models import (
    Pedimento,
    TipoOperacion,
    ProcesamientoPedimento,
    EDocument,
)
from api.customs.serializers import (
    PedimentoSerializer,
    TipoOperacionSerializer,
    ProcesamientoPedimentoSerializer,
    EDocumentSerializer,
)
from api.logger.mixins import LoggingMixin
from mixins.filtrado_organizacion import OrganizacionFiltradaMixin
import requests


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
class ViewSetPedimento(LoggingMixin, viewsets.ModelViewSet, OrganizacionFiltradaMixin): # Pendiente de permisos de creacion
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
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    serializer_class = PedimentoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    model = Pedimento

    filterset_fields = ['patente', 'aduana', 'tipo_operacion', 'clave_pedimento']
    search_fields = ['pedimento', 'contribuyente', 'agente_aduanal']
    ordering_fields = ['created_at', 'updated_at', 'pedimento', 'contribuyente']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.get_queryset_filtrado_por_organizacion() # Tambien filtra por importador

    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un pedimento.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")
        serializer.save(organizacion=self.request.user.organizacion)

        try:
            # Usar el nombre del servicio de Docker Compose en lugar de localhost
            response = requests.request('POST', 'http://microservice:8001/api/v1/services/pedimento_completo', params={},
                json={
                    'estado': 1,
                    'servicio': 3,
                    'tipo_procesamiento': 2,
                    'pedimento': str(serializer.instance.id),
                    'organizacion': str(self.request.user.organizacion.id),
                },
                timeout=10
            )
            
            # Verificar si la respuesta fue exitosa
            if response.status_code == 200:
                print(f"✅ Servicio FastAPI ejecutado exitosamente: {response.status_code}")
                print(f"📄 Respuesta: {response.json()}")
            elif response.status_code == 201:
                print(f"✅ Recurso creado exitosamente en FastAPI: {response.status_code}")
                print(f"📄 Respuesta: {response.json()}")
            else:
                print(f"⚠️  Servicio FastAPI respondió con error: {response.status_code}")
                print(f"📄 Respuesta: {response.text}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ No se pudo conectar al servicio FastAPI: {e}")
            print("🔧 Verifica que el servicio FastAPI esté corriendo en http://localhost:8001")
        except requests.exceptions.Timeout as e:
            print(f"⏰ Timeout al conectar con el servicio FastAPI: {e}")
        except requests.exceptions.RequestException as e:
            print(f"🚨 Error de request al servicio FastAPI: {e}")
        except Exception as e:
            print(f"💥 Error inesperado al llamar al servicio FastAPI: {e}")

    my_tags = ['Pedimentos']

class ViewSetTipoOperacion(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for TipoOperacion model.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]

    queryset = TipoOperacion.objects.all()
    serializer_class = TipoOperacionSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo']
    search_fields = ['tipo', 'descripcion']
    ordering_fields = ['tipo', 'descripcion']
    ordering = ['tipo']
    
    my_tags = ['Tipos_Operacion']

    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un tipo de operación.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")
        # Solo el supoerusuario puede crear tipos de operación
        if not self.request.user.is_superuser:
            raise PermissionDenied("Solo los superusuarios pueden crear tipos de operación")
        
        serializer.save(organizacion=self.request.user.organizacion)

    def perform_update(self, serializer):
        """
        Solo el superusuario puede actualizar tipos de operación.
        """
        if not self.request.user.is_superuser:
            raise PermissionDenied("Solo los superusuarios pueden actualizar tipos de operación")
        
        serializer.save()

class ViewSetProcesamientoPedimento(viewsets.ModelViewSet, OrganizacionFiltradaMixin):
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
    permission_classes = [IsAuthenticated, IsSameOrganizationDeveloper, IsSuperUser]
    serializer_class = ProcesamientoPedimentoSerializer
    pagination_class = CustomPagination
    model = ProcesamientoPedimento
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['pedimento', 'estado', 'servicio', 'tipo_procesamiento']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return self.get_queryset_filtrado_por_organizacion()
    
    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un procesamiento de pedimento.
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValueError("Usuario no autenticado o sin organización")
        if not self.request.user.is_superuser or ((self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists()) :
            raise PermissionDenied("No tienes permisos para crear procesamientos de pedimentos")
        
        if self.request.user.is_superuser:
            # Si es superusuario, permite crear sin organización
            serializer.save()
        
        if (self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            # Si es developer, admin o user, asigna la organización del usuario
            if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
                raise ValueError("Usuario sin organización")
            
            serializer.save(organizacion=self.request.user.organizacion)
    
    my_tags = ['Procesamientos_Pedimentos']

class ViewSetEDocument(LoggingMixin, viewsets.ModelViewSet, OrganizacionFiltradaMixin):
    """
    ViewSet for EDocument model.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    serializer_class = EDocumentSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['pedimento', 'numero_edocument', 'organizacion']
    search_fields = ['numero_edocument', 'descripcion', 'organizacion']
    ordering_fields = ['created_at', 'updated_at', 'numero_edocument']
    ordering = ['-created_at']
    model = EDocument
    my_tags = ['EDocuments']

    def get_queryset(self):
        return self.get_queryset_filtrado_por_organizacion()

    def perform_create(self, serializer):
        """
        Asigna automáticamente la organización del usuario autenticado al crear un EDocument.
        Para superusuarios, permite especificar una organización diferente.
        """
        if not self.request.user.is_authenticated:
            raise ValueError("Usuario no autenticado")
        
        # Si es superusuario y se especifica organizacion en los datos validados
        if self.request.user.is_superuser:
            # Permitir que el superusuario especifique la organización
            serializer.save()
        
        if (self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            # Para usuarios normales, usar siempre su organización
            if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
                raise ValueError("Usuario sin organización")
            serializer.save(organizacion=self.request.user.organizacion)
        
        raise ValueError("Usuario no autenticado o sin permisos para crear EDocument")

    def perform_update(self, serializer):
        """
        Permite actualizar un EDocument, pero solo si el usuario es superusuario o pertenece a la misma organización.
        """
        if not self.request.user.is_authenticated:
            raise ValueError("Usuario no autenticado")
        
        # Si es superusuario, permite actualizar sin restricciones
        if self.request.user.is_superuser:
            serializer.save()
            return
        
        if (self.request.user.groups.filter(name='developer').exists() or self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            # Para usuarios normales, usar siempre su organización
            if not hasattr(self.request.user, 'organizacion') or not self.request.user.organizacion:
                raise ValueError("Usuario sin organización")
            serializer.save(organizacion=self.request.user.organizacion)

        raise ValueError("Usuario no autenticado o sin permisos para actualizar EDocument")

