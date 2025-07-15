from django.contrib import admin
from .models import Notificacion, TipoNotificacion
# Register your models here.


class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'dirigido', 'mensaje', 'fecha_envio', 'created_at', 'visto')
    search_fields = ('mensaje', 'tipo__tipo', 'dirigido__username')
    list_filter = ('tipo', 'visto', 'fecha_envio')
    ordering = ('-created_at',)
    date_hierarchy = 'fecha_envio'

class TipoNotificacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion')
    search_fields = ('tipo',)
    ordering = ('tipo',)

admin.site.register(Notificacion, NotificacionAdmin)
admin.site.register(TipoNotificacion, TipoNotificacionAdmin)
admin.site.empty_value_display = '-vacío-'  # Display this when a field is empty
