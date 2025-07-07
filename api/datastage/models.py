from django.db import models

# Create your models here.
class DataStage(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    almacenamiento = models.PositiveIntegerField(default=0, blank=False, null=False)  # in GB
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='datastages')
    archivo = models.FileField(upload_to='datastages/', blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "DataStage"
        verbose_name_plural = "DataStages"
        db_table = 'datastage'

    def __str__(self):
        return self.nombre
    