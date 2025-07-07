import uuid
from django.db import models

# Create your models here.
class Aduana(models.Model):
    seccion = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.seccion}"
    
    class Meta:
        verbose_name = "Aduana"
        verbose_name_plural = "Aduanas"
        db_table = 'aduana'
        ordering = ['seccion']

class Patente(models.Model):
    numero = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.numero}"

    class Meta:
        verbose_name = "Patente"
        verbose_name_plural = "Patentes"
        db_table = 'patente'
        ordering = ['numero']
       
class ClavePedimento(models.Model):
    clave = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.clave}"

    class Meta:
        verbose_name = "Clave de Pedimento"
        verbose_name_plural = "Claves de Pedimento"
        db_table = 'clave_pedimento'
        ordering = ['clave']

class TipoOperacion(models.Model):
    tipo = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.tipo}"

    class Meta:
        verbose_name = "Tipo de Operacion"
        verbose_name_plural = "Tipos de Operacion"
        db_table = 'tipo_operacion'
        ordering = ['tipo']

class Regimen(models.Model):
    clave = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.clave} - {self.descripcion}"

    class Meta:
        verbose_name = "Regimen"
        verbose_name_plural = "Regimenes"
        db_table = 'regimen'
        ordering = ['clave']

class Pedimento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedimento = models.CharField(max_length=20, unique=True, help_text="Número de pedimento aduanal")
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='pedimentos', help_text="Organización a la que pertenece el pedimento")
    
    patente = models.CharField(max_length=20, blank=True, null=True, help_text="Número de patente aduanal")
    aduana = models.CharField(max_length=10, blank=True, null=True, help_text="Clave de la aduana según la clasificación aduanera")
    regimen = models.CharField(max_length=10, blank=True, null=True, help_text="Clave del régimen aduanero según la clasificación aduanera")
    tipo_operacion = models.BooleanField(default=False, help_text="Indica si es una operación de 1 (importación) o 0 (exportación)")
    clave_pedimento = models.CharField(max_length=10, blank=True, null=True, help_text="Clave del pedimento según la clasificación aduanera")

    fecha_inicio = models.DateField(help_text="Fecha de inicio del pedimento")
    fecha_fin = models.DateField(help_text="Fecha de fin del pedimento")
    fecha_pago = models.DateField(help_text="Fecha de pago del pedimento", blank=True, null=True)
    
    alerta = models.BooleanField(default=False, help_text="Indica si el pedimento tiene una alerta asociada")
    
    contribuyente = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre del contribuyente/importador asociado al pedimento")
    agente_aduanal = models.CharField(max_length=100, blank=True, null=True, help_text="RFC del agente aduanal")
    
    curp_apoderado = models.CharField(max_length=18, blank=True, null=True, help_text="CURP del apoderado aduanal")

    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    importe_pedimento = models.DecimalField(max_digits=10, decimal_places=2)
    existe_expediente = models.BooleanField(default=False)
    numero_operacion = models.CharField(max_length=20, blank=True, null=True, help_text="Número de operación del pedimento")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del registro")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del registro")
    
    def __str__(self):
        return f"{self.pedimento}"

    class Meta:
        verbose_name = "Pedimento"
        verbose_name_plural = "Pedimentos"
        db_table = 'pedimento'
        ordering = ['pedimento']

class AgenteAduanal(models.Model):
    id_aduana = models.ForeignKey(Aduana, on_delete=models.CASCADE, related_name='agentes_aduanales')
    id_patente = models.ForeignKey('Patente', on_delete=models.CASCADE, related_name='agentes_aduanales')
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - ({self.id_patente})"

    class Meta:
        verbose_name = "Agente Aduanal"
        verbose_name_plural = "Agentes Aduanales"
        db_table = 'agente_aduanal'
        ordering = ['nombre']

class EstadoDeProcesamiento(models.Model):
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.estado

    class Meta:
        verbose_name = "Estado de Procesamiento"
        verbose_name_plural = "Estados de Procesamiento"
        db_table = 'estado_de_procesamiento'
        ordering = ['estado']

class TipoDeProcesamiento(models.Model):
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo

    class Meta:
        verbose_name = "Tipo de Procesamiento"
        verbose_name_plural = "Tipos de Procesamiento"
        db_table = 'tipo_de_procesamiento'
        ordering = ['tipo']

class Servicio(models.Model):
    endpoint = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    hora_inicio = models.TimeField(max_length=50, blank=True, null=True)
    hora_fin = models.TimeField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.endpoint

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        db_table = 'servicio'
        ordering = ['endpoint']

class ProcesamientoPedimento(models.Model):
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='procesamientos')
    estado = models.ForeignKey(EstadoDeProcesamiento, on_delete=models.CASCADE, related_name='procesamientos')
    tipo_procesamiento = models.ForeignKey(TipoDeProcesamiento, on_delete=models.CASCADE, related_name='procesamientos', blank=True, null=True)
    pedimento = models.ForeignKey(Pedimento, on_delete=models.CASCADE, related_name='procesamientos')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='procesamientos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pedimento.pedimento} - {self.estado.estado}"
    
    class Meta:
        verbose_name = "Procesamiento de Pedimento"
        verbose_name_plural = "Procesamientos de Pedimento"
        db_table = 'procesamiento_pedimento'
        ordering = ['created_at']