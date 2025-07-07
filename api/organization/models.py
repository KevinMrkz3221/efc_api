from django.db import models
from api.licence.models import Licencia
from django.conf import settings
import uuid

class UsoAlmacenamiento(models.Model):
    organizacion = models.OneToOneField('Organizacion', on_delete=models.CASCADE)
    espacio_utilizado = models.PositiveBigIntegerField(default=0)  # en bytes
    
    class Meta:
        verbose_name = "Uso de Almacenamiento"
        verbose_name_plural = "Usos de Almacenamiento"
        db_table = 'uso_almacenamiento'
    
    def __str__(self):
        return f"{self.organizacion} - {self.espacio_utilizado} bytes"
    
    @property
    def espacio_disponible(self):
        # Convertir GB de la licencia a bytes (1 GB = 1024^3 bytes)
        max_almacenamiento_bytes = self.organizacion.licencia.almacenamiento * 1024 ** 3
        return max_almacenamiento_bytes - self.espacio_utilizado
    
    @property
    def porcentaje_utilizado(self):
        max_almacenamiento_bytes = self.organizacion.licencia.almacenamiento * 1024 ** 3
        if max_almacenamiento_bytes == 0:
            return 0
        return (self.espacio_utilizado / max_almacenamiento_bytes) * 100
    
class Organizacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    licencia = models.ForeignKey(Licencia, on_delete=models.CASCADE, related_name='organizaciones') 
    is_agente_aduanal = models.BooleanField(default=False)
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=25)
    titular = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=25)
    estado = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    inicio = models.DateField(null=True, blank=True)
    vencimiento = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    observaciones = models.TextField(null=True, blank=True)
    membretado = models.ImageField(upload_to='membretado/', null=True, blank=True)
    membretado_2 = models.ImageField(upload_to='membretado/', null=True, blank=True)

    @property
    def espacio_utilizado(self):
        uso, created = UsoAlmacenamiento.objects.get_or_create(organizacion=self)
        return uso.espacio_utilizado
    
    @property
    def espacio_disponible(self):
        uso, created = UsoAlmacenamiento.objects.get_or_create(organizacion=self)
        return (self.licencia.almacenamiento * 1024 ** 3) - uso.espacio_utilizado
    
    @property
    def porcentaje_utilizado(self):
        uso, created = UsoAlmacenamiento.objects.get_or_create(organizacion=self)
        if self.licencia.almacenamiento == 0:
            return 0
        return (uso.espacio_utilizado / (self.licencia.almacenamiento * 1024 ** 3)) * 100

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Organizacion"
        verbose_name_plural = "Organizaciones"
        db_table = 'organizacion'
        ordering = ['nombre']