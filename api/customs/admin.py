from django.contrib import admin
from .models import (
    Aduana,
    AgenteAduanal,
    ClavePedimento,
    EstadoDeProcesamiento,
    Patente,
    Pedimento,
    ProcesamientoPedimento,
    Regimen,
    Servicio,
    TipoDeProcesamiento,
    TipoOperacion,
    EDocument
)

class PatenteAdmin(admin.ModelAdmin):
    model = Patente
    list_display = ('id', 'numero', 'descripcion')
    search_fields = ('numero', 'descripcion')

class AduanaAdmin(admin.ModelAdmin):
    model = Aduana
    list_display = ('id', 'seccion',)
    search_fields = ('nombre', 'codigo')

class ClavePedimentoAdmin(admin.ModelAdmin):
    model = ClavePedimento
    list_display = ('id', 'clave')
    search_fields = ('clave', 'descripcion')


class TipoOperacionAdmin(admin.ModelAdmin):
    model = TipoOperacion
    list_display = ('id', 'tipo')
    search_fields = ('nombre',)

class PedimentoAdmin(admin.ModelAdmin):
    model = Pedimento
    list_display = ('id', 'pedimento', 'aduana', 'patente')
    search_fields = ('numero',)
    list_filter = ('aduana', 'agente_aduanal')

class AgenteAduanalAdmin(admin.ModelAdmin):
    model = AgenteAduanal
    list_display = ('id', 'id_aduana', 'id_patente', 'nombre', 'rfc')
    search_fields = ('nombre', 'rfc')

class ProcesamientoPedimentoAdmin(admin.ModelAdmin):
    model = ProcesamientoPedimento
    list_display = ('id', 'estado', 'pedimento', 'created_at', 'updated_at')
    list_filter = ('estado',)


class EstadoDeProcesamientoAdmin(admin.ModelAdmin):
    model = EstadoDeProcesamiento
    list_display = ('id', 'estado')
    search_fields = ('estado',)

class TipoDeProcesamientoAdmin(admin.ModelAdmin):
    model = TipoDeProcesamiento
    list_display = ('id', 'tipo')
    search_fields = ('tipo',)

class ServicioAdmin(admin.ModelAdmin):
    model = Servicio
    list_display = ('id', 'endpoint', 'descripcion')
    search_fields = ('endpoint', 'descripcion')

class RegimenAdmin(admin.ModelAdmin):
    model = Regimen
    list_display = ('id', 'clave', 'descripcion')
    search_fields = ('clave', 'descripcion')

class EDocumentAdmin(admin.ModelAdmin):
    model = EDocument
    list_display = ('id', 'pedimento', 'numero_edocument', 'organizacion')
    search_fields = ('numero_edocument',)
    list_filter = ('pedimento', 'organizacion')

admin.site.register(Aduana, AduanaAdmin)
admin.site.register(ClavePedimento, ClavePedimentoAdmin)
admin.site.register(TipoOperacion, TipoOperacionAdmin)
admin.site.register(Pedimento, PedimentoAdmin)
admin.site.register(AgenteAduanal, AgenteAduanalAdmin)
admin.site.register(Patente, PatenteAdmin)
admin.site.register(ProcesamientoPedimento, ProcesamientoPedimentoAdmin)
admin.site.register(EstadoDeProcesamiento, EstadoDeProcesamientoAdmin)
admin.site.register(TipoDeProcesamiento, TipoDeProcesamientoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Regimen, RegimenAdmin)
admin.site.register(EDocument, EDocumentAdmin)