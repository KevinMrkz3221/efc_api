from django.shortcuts import render
from django.http import FileResponse, Http404
from django.db import transaction

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .serializers import DocumentSerializer
from .models import Document
from api.organization.models import UsoAlmacenamiento
from io import BytesIO
import zipfile
from django.utils.text import slugify
from django.http import HttpResponse
from rest_framework.decorators import action
from datetime import timedelta
from django.utils import timezone

from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)
import logging
logger = logging.getLogger(__name__)

from mixins.filtrado_organizacion import DocumentosFiltradosMixin

class CustomPagination(PageNumberPagination):

    """
    Paginación personalizada con parámetros flexibles
    - Si no se especifica page_size, devuelve todos los resultados (sin paginación)
    - Si se especifica page_size, usa paginación normal
    """
    page_size = None  # Por defecto 10000 por página
    page_size_query_param = 'page_size'
    max_page_size = 10000  # Límite máximo de seguridad
    page_query_param = 'page'
    
    # Usar la paginación estándar de DRF, pero con page_size=10000 por defecto y máximo 10000

# Create your views here.
class DocumentViewSet(viewsets.ModelViewSet, DocumentosFiltradosMixin):
    """
    ViewSet for Document model.
    """
    permission_classes = [IsAuthenticated &  (IsSuperUser | IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper )]
    model = Document
    
    pagination_class = CustomPagination
    serializer_class = DocumentSerializer
    # Habilitar filtro por pedimento (UUID) y pedimento_numero (campo pedimento del modelo relacionado)
    filterset_fields = ['extension', 'size', 'document_type', 'pedimento', 'pedimento__pedimento']

    # Puedes filtrar por pedimento usando: /api/record/documents/?pedimento=<id> o /api/record/documents/?pedimento__pedimento=<numero>
    # Ejemplo: /api/record/documents/?pedimento_numero=12345678
    my_tags = ['Documents']

    def get_queryset(self):
        queryset = self.get_queryset_filtrado_por_organizacion()
        pedimento_numero = self.request.query_params.get('pedimento_numero')
        if pedimento_numero:
            queryset = queryset.filter(pedimento__pedimento=pedimento_numero)

        return queryset
    
    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'organizacion'):
            raise ValidationError({"error": "Usuario no autenticado o sin organización"})

        archivo = self.request.FILES.get('archivo')
        if not archivo:
            raise ValidationError({"archivo": "Se requiere un archivo para subir"})

        # Permitir que el superusuario especifique la organización
        organizacion = user.organizacion
        
        if self.request.user.is_superuser:
            organizacion = serializer.validated_data.get('organizacion', organizacion)

        uso = UsoAlmacenamiento.objects.select_for_update().get_or_create(
            organizacion=organizacion,
            defaults={'espacio_utilizado': 0}
        )[0]

        # Calcular límites
        max_almacenamiento_bytes = organizacion.licencia.almacenamiento * 1024 ** 3
        nuevo_espacio_utilizado = uso.espacio_utilizado + archivo.size

        # Validación estricta con raise ValidationError
        if nuevo_espacio_utilizado > max_almacenamiento_bytes:
            espacio_faltante = nuevo_espacio_utilizado - max_almacenamiento_bytes
            raise ValidationError({
                "error": "Espacio de almacenamiento insuficiente",
                "detalle": {
                    "espacio_faltante_gb": round(espacio_faltante / (1024 ** 3), 2),
                    "espacio_utilizado_gb": round(uso.espacio_utilizado / (1024 ** 3), 2),
                    "limite_gb": organizacion.licencia.almacenamiento,
                    "archivo_gb": round(archivo.size / (1024 ** 3), 4)
                },
                "codigo": "storage_limit_exceeded"
            }, code=status.HTTP_400_BAD_REQUEST)

        # Guardar documento y actualizar espacio atómicamente
        documento = serializer.save(
            organizacion=organizacion,
            size=archivo.size,
            extension=archivo.name.split('.')[-1].lower()
        )

        uso.espacio_utilizado = nuevo_espacio_utilizado
        uso.save()
        
    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()
        new_file = self.request.FILES.get('archivo')
        
        if new_file:
            if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
                raise ValidationError({"error": "Usuario no autenticado o sin organización"})
            
            organizacion = self.request.user.organizacion
            uso = UsoAlmacenamiento.objects.select_for_update().get(organizacion=organizacion)
            
            diferencia = new_file.size - instance.size
            max_almacenamiento_bytes = organizacion.licencia.almacenamiento * 1024 ** 3
            nuevo_espacio_utilizado = uso.espacio_utilizado + diferencia
            
            if nuevo_espacio_utilizado > max_almacenamiento_bytes:
                espacio_faltante = nuevo_espacio_utilizado - max_almacenamiento_bytes
                raise ValidationError({
                    "error": "Espacio insuficiente para actualizar el archivo",
                    "detalle": {
                        "espacio_faltante_bytes": espacio_faltante,
                        "tamaño_nuevo_archivo": new_file.size,
                        "tamaño_anterior_archivo": instance.size
                    },
                    "codigo": "update_storage_limit_exceeded"
                }, code=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar documento y espacio
            serializer.save(size=new_file.size)
            uso.espacio_utilizado = nuevo_espacio_utilizado
            uso.save()
        else:
            serializer.save()

    def perform_destroy(self, instance):
        # Restar el espacio al eliminar
        uso = UsoAlmacenamiento.objects.get(organizacion=instance.organizacion)
        uso.espacio_utilizado -= instance.size
        uso.save()
        instance.delete()
    
class ProtectedDocumentDownloadView(APIView, DocumentosFiltradosMixin):
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    serializer_class = DocumentSerializer
    model = Document
    my_tags = ['Documents']

    def get_queryset(self):
        return self.get_queryset_filtrado_por_organizacion()

    def get(self, request, pk):
        if not request.user.is_authenticated or not hasattr(request.user, 'organizacion'):
            raise Http404("Usuario no autenticado")
        

        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            raise Http404("Documento no encontrado")

        # Verifica que el usuario pertenece a la organización del documento
        
        if self.request.user.is_superuser:
            return FileResponse(doc.archivo.open('rb'))

        if doc.organizacion != request.user.organizacion:
            raise Http404("No autorizado")

        return FileResponse(doc.archivo.open('rb'))
    
class BulkDownloadZipView(APIView):
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    my_tags = ['Documents']

    def post(self, request):
        
        if not request.user.is_authenticated or not hasattr(request.user, 'organizacion'):
            return Response({"error": "Usuario no autenticado o sin organización"}, status=401)
        
        pks = request.data.get('document_ids', [])
        pedimento_nombre = request.data.get('pedimento_nombre', 'documentos')
        if not isinstance(pks, list) or not pks:
            return Response({"error": "Debe proporcionar una lista de IDs de documentos en 'document_ids'."}, status=400)

        if self.request.user.is_superuser:
            docs = Document.objects.filter(pk__in=pks)
        else:
            docs = Document.objects.filter(pk__in=pks, organizacion=request.user.organizacion)

        if docs.count() != len(pks):
            return Response({"error": "Uno o más documentos no existen o no pertenecen a su organización."}, status=404)

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for doc in docs:
                # Usar solo el nombre del archivo sin descripcion
                file_name = slugify(doc.archivo.name.rsplit('/', 1)[-1].rsplit('.', 1)[0])
                ext = doc.archivo.name.split('.')[-1]
                zip_name = f"{file_name}.{ext}"
                doc.archivo.open('rb')
                zip_file.writestr(zip_name, doc.archivo.read())
                doc.archivo.close()

        buffer.seek(0)
        safe_name = slugify(pedimento_nombre)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={safe_name or "documentos"}.zip'
        
        return response


