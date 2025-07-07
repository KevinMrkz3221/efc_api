from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from api.record.models import Document
from core.permissions import IsSameOrganization

from .serializers import OrganizacionSerializer, UsoAlmacenamientoSerializer
from .models import Organizacion, UsoAlmacenamiento
from api.customs.models import Pedimento
from api.logger.mixins import LoggingMixin

# Create your views here.

class ViewSetOrganizacion(LoggingMixin, viewsets.ModelViewSet):
    """
    ViewSet for Organizacion model.
    """
    permission_classes = [IsAuthenticated, IsSameOrganization]
    queryset = Organizacion.objects.all()
    serializer_class = OrganizacionSerializer
    filterset_fields = ['nombre', 'descripcion']
    
    my_tags = ['Organizaciones']

class UsoAlmacenamientoViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """
    Vista para consultar el uso de almacenamiento
    Solo lectura (GET) ya que la actualización se hace automáticamente
    """
    queryset = UsoAlmacenamiento.objects.all()
    serializer_class = UsoAlmacenamientoSerializer
    permission_classes = [IsAuthenticated, IsSameOrganization]

    my_tags = ['Uso de Almacenamiento'] 

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
    