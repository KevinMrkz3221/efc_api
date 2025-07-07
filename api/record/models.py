from django.db import models
import uuid

from api.organization.models import UsoAlmacenamiento

# Create your models here.

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='documents')
    pedimento = models.ForeignKey('customs.Pedimento', on_delete=models.CASCADE, related_name='documents')
    archivo = models.FileField(upload_to='documents/', max_length=400)
    document_type = models.ForeignKey('DocumentType', on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    extension = models.CharField(max_length=60, blank=True, null=True)
    size = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # Usar get_or_create en lugar de get para manejar el caso cuando no existe
        uso_almacenamiento, created = UsoAlmacenamiento.objects.get_or_create(
            organizacion=self.organizacion,
            defaults={'espacio_utilizado': 0}
        )
        
        almacenamiento_licencia_bytes = self.organizacion.licencia.almacenamiento * 1024 ** 3
        
        if is_new:
            if uso_almacenamiento.espacio_utilizado + self.size > almacenamiento_licencia_bytes:
                raise ValueError("La organización no tiene suficiente espacio de almacenamiento disponible")
            
            super().save(*args, **kwargs)
            
            uso_almacenamiento.espacio_utilizado += self.size
            uso_almacenamiento.save()
        else:
            old_file = Document.objects.get(pk=self.pk)
            if old_file.size != self.size:
                diferencia = self.size - old_file.size
                if uso_almacenamiento.espacio_utilizado + diferencia > almacenamiento_licencia_bytes:
                    raise ValueError("No hay suficiente espacio para la actualización")
                
                uso_almacenamiento.espacio_utilizado += diferencia
                uso_almacenamiento.save()
            
            super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        # Usar get_or_create aquí también por si acaso
        uso_almacenamiento, created = UsoAlmacenamiento.objects.get_or_create(
            organizacion=self.organizacion,
            defaults={'espacio_utilizado': 0}
        )
        
        uso_almacenamiento.espacio_utilizado -= self.size
        uso_almacenamiento.save()
        
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return f"{self.archivo.name}"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        db_table = 'document'
        ordering = ['created_at']

class DocumentType(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"
        db_table = 'document_type'
        ordering = ['nombre']