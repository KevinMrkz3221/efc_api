import uuid
from django.db import models

# Create your models here.

class TipoOperacion(models.Model):
    tipo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.tipo}"

    class Meta:
        verbose_name = "Tipo de Operacion"
        verbose_name_plural = "Tipos de Operacion"
        db_table = 'tipo_operacion'
        ordering = ['tipo']

class Pedimento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedimento = models.CharField(max_length=20, unique=True, help_text="Número de pedimento aduanal")
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='pedimentos', help_text="Organización a la que pertenece el pedimento")
    
    patente = models.CharField(max_length=20, blank=True, null=True, help_text="Número de patente aduanal")
    aduana = models.CharField(max_length=10, blank=True, null=True, help_text="Clave de la aduana según la clasificación aduanera")
    regimen = models.CharField(max_length=10, blank=True, null=True, help_text="Clave del régimen aduanero según la clasificación aduanera")
    tipo_operacion = models.ForeignKey('TipoOperacion', on_delete=models.SET_NULL, blank=True, null=True, help_text="Tipo de operación del pedimento", related_name='pedimentos')
    clave_pedimento = models.CharField(max_length=10, blank=True, null=True, help_text="Clave del pedimento según la clasificación aduanera")

    fecha_inicio = models.DateField(help_text="Fecha de inicio del pedimento", blank=True, null=True)
    fecha_fin = models.DateField(help_text="Fecha de fin del pedimento", blank=True, null=True)
    fecha_pago = models.DateField(help_text="Fecha de pago del pedimento", blank=True, null=True)
    
    alerta = models.BooleanField(default=False, help_text="Indica si el pedimento tiene una alerta asociada")
    
    contribuyente = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre del contribuyente/importador asociado al pedimento")
    agente_aduanal = models.CharField(max_length=100, blank=True, null=True, help_text="RFC del agente aduanal")
    
    curp_apoderado = models.CharField(max_length=18, blank=True, null=True, help_text="CURP del apoderado aduanal")

    importe_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Importe total del pedimento")
    saldo_disponible = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Saldo disponible del pedimento")
    importe_pedimento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Importe del pedimento")
    existe_expediente = models.BooleanField(default=False)
    remesas = models.BooleanField(default=False, help_text="Indica si el pedimento tiene remesas asociadas")

    numero_partidas = models.PositiveIntegerField(default=0, help_text="Número de partidas asociadas al pedimento", blank=True, null=True)
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

class EDocument(models.Model):
    pedimento = models.ForeignKey(Pedimento, on_delete=models.CASCADE, related_name='documentos', help_text="Pedimento asociado al documento")
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, related_name='edocuments', help_text="Organización a la que pertenece el EDocument")
    numero_edocument = models.CharField(max_length=20, unique=True, help_text="Número único del e-documento")
    clave = models.CharField(max_length=10, blank=True, null=True, help_text="Clave del e-documento según la clasificación aduanera")
    cadena_original = models.TextField(blank=True, null=True, help_text="Cadena original del e-documento")
    sello_digital = models.TextField(blank=True, null=True, help_text="Firma digital del e-documento")
    descripcion = models.CharField(max_length=200, blank=True, null=True, help_text="Descripción del documento")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación del documento")   
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización del documento")

    def __str__(self):
        return f"{self.descripcion} - {self.pedimento.pedimento}"

    class Meta:
        verbose_name = "EDocument"
        verbose_name_plural = "EDocuments"
        db_table = 'edocs'
        ordering = ['created_at']

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

