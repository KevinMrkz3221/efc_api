from django.db import models
from api.cuser.models import CustomUser
import uuid



# Create your models here.
class Vucem(models.Model):
    """
    Modelo para almacenar información de VUCEM.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_by = models.ForeignKey('cuser.CustomUser', on_delete=models.CASCADE, related_name='vucems_created', help_text="Usuario que creó el VUCEM")
    updated_by = models.ForeignKey('cuser.CustomUser', on_delete=models.CASCADE, related_name='vucems_updated', null=True, blank=True, help_text="Usuario que actualizó el VUCEM")
    
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='vucems', help_text="Organización a la que pertenece el VUCEM")
    usuario = models.CharField(max_length=100, unique=True, help_text="Usuario de VUCEM")
    password = models.CharField(max_length=100, help_text="Contraseña de VUCEM")
    patente = models.CharField(max_length=100, unique=True, help_text="Patente de VUCEM")
    key = models.FileField(upload_to='vucem_keys/', help_text="Llave privada de VUCEM")
    cer = models.FileField(upload_to='vucem_certs/', help_text="Certificado de VUCEM")

    is_importador = models.BooleanField(default=False, help_text="Indica si es importador")
    acusecove = models.BooleanField(default=False, help_text="Indica si generara acusecove")
    acuseedocument = models.BooleanField(default=False, help_text="Indica si generara acusee edocumento")
    is_active = models.BooleanField(default=True, help_text="Indica si el registro está activo")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del registro")

    class Meta:
        verbose_name = 'VUCEM'
        verbose_name_plural = 'VUCEMs'
        db_table = 'vucem'

    def __str__(self):
        return self.organizacion.nombre + ' - ' + str(self.id)

class UsuarioImportador(models.Model):
    """
    Modelo para almacenar información de usuarios importadores.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='usuarios_importadores', help_text="Organización a la que pertenece el usuario importador", blank=True, null=True)
    vucem = models.ForeignKey(Vucem, on_delete=models.CASCADE, related_name='usuarios_importadores', help_text="VUCEM asociado al usuario importador")
    user = models.ForeignKey('cuser.CustomUser', on_delete=models.CASCADE, related_name='usuarios_importadores', help_text="Usuario de la plataforma asociado al importador")
    
    rfc = models.CharField(max_length=13, unique=True, help_text="RFC del usuario importador")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del registro")

    class Meta:
        verbose_name = 'Usuario Importador'
        verbose_name_plural = 'Usuarios Importadores'
        db_table = 'usuario_importador'

    def __str__(self):
        return self.nombre + ' - ' + self.rfc