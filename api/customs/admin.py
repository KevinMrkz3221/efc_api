from django.contrib import admin
from .models import (
    EstadoDeProcesamiento,
    Pedimento,
    ProcesamientoPedimento,
    Servicio,
    TipoDeProcesamiento,
    TipoOperacion,
    EDocument
)

class TipoOperacionAdmin(admin.ModelAdmin):
    model = TipoOperacion
    list_display = ('id', 'tipo')
    search_fields = ('nombre',)

class PedimentoAdmin(admin.ModelAdmin):
    model = Pedimento
    list_display = ('id', 'pedimento', 'aduana', 'patente')
    search_fields = ('numero',)
    list_filter = ('aduana', 'agente_aduanal')

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

class EDocumentAdmin(admin.ModelAdmin):
    model = EDocument
    list_display = ('id', 'pedimento', 'numero_edocument', 'organizacion')
    search_fields = ('numero_edocument',)
    list_filter = ('pedimento', 'organizacion')

admin.site.register(TipoOperacion, TipoOperacionAdmin)
admin.site.register(Pedimento, PedimentoAdmin)
admin.site.register(ProcesamientoPedimento, ProcesamientoPedimentoAdmin)
admin.site.register(EstadoDeProcesamiento, EstadoDeProcesamientoAdmin)
admin.site.register(TipoDeProcesamiento, TipoDeProcesamientoAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(EDocument, EDocumentAdmin)