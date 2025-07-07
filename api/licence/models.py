from django.db import models

# Create your models here.
class Licencia(models.Model):
    # Define the Licencia model minimally for ForeignKey reference
    # Add fields as needed
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    almacenamiento = models.PositiveIntegerField(default=0, blank=False, null=False)  # in GB


    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"
        db_table = 'licencia'


    def __str__(self):
        return self.nombre
    