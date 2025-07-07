from django.shortcuts import render
from django.http import FileResponse, Http404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from core.permissions import IsSameOrganization
from .serializers import DocumentSerializer
from .models import Document
from api.organization.models import UsoAlmacenamiento
from io import BytesIO
import zipfile
from django.utils.text import slugify
from django.http import HttpResponse
from rest_framework.decorators import action


# Create your views here.
class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document model.
    """
    permission_classes = [IsAuthenticated, IsSameOrganization]
    
    serializer_class = DocumentSerializer
    filterset_fields = ['extension', 'size', 'document_type']
    
    my_tags = ['Documents']

    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return Document.objects.none()
        return Document.objects.filter(organizacion=self.request.user.organizacion)
    
    @transaction.atomic
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            raise ValidationError({"error": "Usuario no autenticado o sin organización"})
        
        organizacion = self.request.user.organizacion
        archivo = self.request.FILES.get('archivo')
        
        if not archivo:
            raise ValidationError({"archivo": "Se requiere un archivo para subir"})
        
        # Obtener o crear registro de uso de almacenamiento con bloqueo SELECT FOR UPDATE
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
    
class ProtectedDocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsSameOrganization]
    serializer_class = DocumentSerializer
    my_tags = ['Documents']

    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return Document.objects.none()
        return Document.objects.filter(organizacion=self.request.user.organizacion)

    def get(self, request, pk):
        if not request.user.is_authenticated or not hasattr(request.user, 'organizacion'):
            raise Http404("Usuario no autenticado")
        
        try:
            doc = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            raise Http404("Documento no encontrado")
        # Verifica que el usuario pertenece a la organización del documento
        if doc.organizacion != request.user.organizacion:
            raise Http404("No autorizado")
        return FileResponse(doc.archivo.open('rb'))
    

class BulkDownloadZipView(APIView):
    permission_classes = [IsAuthenticated, IsSameOrganization]
    my_tags = ['Documents']

    def post(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, 'organizacion'):
            return Response({"error": "Usuario no autenticado o sin organización"}, status=401)
        
        pks = request.data.get('document_ids', [])
        pedimento_nombre = request.data.get('pedimento_nombre', 'documentos')
        if not isinstance(pks, list) or not pks:
            return Response({"error": "Debe proporcionar una lista de IDs de documentos en 'document_ids'."}, status=400)

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


