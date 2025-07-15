from django.db import models
from api.cuser.models import CustomUser
# Create your models here.

class TipoNotificacion(models.Model):
    tipo = models.CharField(max_length=100, unique=True, help_text="Tipo de notificación")
    descripcion = models.CharField(max_length=200, help_text="Descripción del tipo de notificación")

    def __str__(self):
        return self.tipo

    class Meta:
        verbose_name = "Tipo de Notificación"
        verbose_name_plural = "Tipos de Notificación"
        db_table = 'tipo_notificacion'
        ordering = ['tipo']

class Notificacion(models.Model):
    tipo = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE, related_name='notificaciones', help_text="Tipo de notificación")
    dirigido = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notificaciones', help_text="Usuario al que se dirige la notificación")
    

    mensaje = models.TextField(help_text="Mensaje de la notificación")
    fecha_envio = models.DateTimeField(blank=True, null=True, help_text="Fecha de envío de la notificación")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación de la notificación")
    visto = models.BooleanField(default=False, help_text="Indica si la notificación ha sido vista")

    def __str__(self):
        return f"{self.tipo} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}" 
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        db_table = 'notificaciones'
        ordering = ['-created_at']