from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from api.record.models import Document
from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)
from .serializers import OrganizacionSerializer, UsoAlmacenamientoSerializer
from .models import Organizacion, UsoAlmacenamiento
from api.customs.models import Pedimento
from api.logger.mixins import LoggingMixin
from mixins.filtrado_organizacion import OrganizacionFiltradaMixin

# Create your views here.

class ViewSetOrganizacion(LoggingMixin, viewsets.ModelViewSet, OrganizacionFiltradaMixin):
    """
    ViewSet for Organizacion model.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]

    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer
    filterset_fields = ['nombre', 'descripcion']
    
    my_tags = ['Organizaciones']

    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return Organizacion.objects.none()
        
        if self.request.user.is_superuser:
            # Superuser can see all organizations
            return Organizacion.objects.all()
        
        if (self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter('developer').exists() or self.request.user.groups.filter('user')) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            # Importers can only see their own organization
            return Organizacion.objects.filter(users=self.request.user)
        
        if self.request.user.groups.filter(name='importador').exists():
            return Organizacion.objects.filter(users=self.request.user)
        
        return Organizacion.objects.none()

class UsoAlmacenamientoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    Vista para consultar el uso de almacenamiento
    Solo lectura (GET) ya que la actualización se hace automáticamente
    """
    queryset = UsoAlmacenamiento.objects.all()
    serializer_class = UsoAlmacenamientoSerializer
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]

    my_tags = ['Uso de Almacenamiento'] 

    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return UsoAlmacenamiento.objects.none()
        

        if self.request.user.is_superuser:
            # Superuser can see all storage usage
            return UsoAlmacenamiento.objects.all()
        
        if (self.request.user.groups.filter(name='developer').exists() or 
            self.request.user.groups.filter(name='admin').exists() or 
            self.request.user.groups.filter(name='user').exists()) and self.request.user.groups.filter(name='Agente Aduanal').exists():
            # Developers, Admins, and Users can see their organization's storage usage
            return UsoAlmacenamiento.objects.filter(organizacion=self.request.user.organizacion)
        
        if self.request.user.groups.filter(name='importador').exists():
            # Importers can only see their own organization's storage usage
            raise PermissionDenied("Los importadores no tienen acceso al uso de almacenamiento.")

        return UsoAlmacenamiento.objects.none()

    @action(detail=False, methods=['get'])
    def mi_organizacion(self, request):

        """Obtiene el uso de almacenamiento de la organización del usuario actual"""
        organizacion = request.user.organizacion
        
        # Obtener o crear el registro de uso
        uso, created = UsoAlmacenamiento.objects.get_or_create(
            organizacion=organizacion,
            defaults={'espacio_utilizado': 0}
        )
        
        # Calcular el total sumando todos los documentos (en bytes)
        total_utilizado = Document.objects.filter(
            organizacion=organizacion
        ).aggregate(total=Sum('size'))['total'] or 0
        
        # Sincronizar con el registro de uso (por si hay discrepancias)
        if uso.espacio_utilizado != total_utilizado:
            uso.espacio_utilizado = total_utilizado
            uso.save()
        
        # Calcular métricas adicionales
        max_almacenamiento_bytes = organizacion.licencia.almacenamiento * 1024 ** 3
        porcentaje = (total_utilizado / max_almacenamiento_bytes * 100) if max_almacenamiento_bytes > 0 else 0
        
        data = {
            'organizacion': organizacion.nombre,
            'limite_almacenamiento_gb': organizacion.licencia.almacenamiento,
            'espacio_utilizado_bytes': total_utilizado,
            'espacio_utilizado_gb': total_utilizado / (1024 ** 3),
            'espacio_disponible_bytes': max(max_almacenamiento_bytes - total_utilizado, 0),
            'porcentaje_utilizado': round(porcentaje, 2),
            'total_documentos': Document.objects.filter(organizacion=organizacion).count(),
            'total_pedimentos': Pedimento.objects.filter(organizacion=organizacion).count(),
            'total_usuarios': organizacion.users.count()
        }
        
        return Response(data)
    