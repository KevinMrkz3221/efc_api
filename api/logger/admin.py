
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import RequestLog, UserActivity, ErrorLog
import json
from config.settings import SITE_URL

class ReadOnlyAdminMixin:
    """Mixin para hacer que los modelos sean solo lectura en el admin."""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RequestLog)
class RequestLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        'timestamp', 'user_display', 'method', 'path', 'status_code', 
        'response_time', 'ip_address'
    ]
    list_filter = [
        'method', 'status_code', 'timestamp', 'user_agent'
    ]
    search_fields = [
        'path', 'ip_address', 'user__username', 'user__email'
    ]
    readonly_fields = [
        'timestamp', 'user', 'method', 'path', 'query_params_display', 
        'status_code', 'response_time', 'ip_address', 'user_agent', 
        'body_display', 'referer'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Anónimo"
    user_display.short_description = "Usuario"
    
    def query_params_display(self, obj):
        if obj.query_params:
            try:
                params = json.loads(obj.query_params) if isinstance(obj.query_params, str) else obj.query_params
                formatted = json.dumps(params, indent=2, ensure_ascii=False)
                return format_html('<pre>{}</pre>', formatted)
            except:
                return obj.query_params
        return "Sin parámetros"
    query_params_display.short_description = "Parámetros de consulta"
    
    def body_display(self, obj):
        if obj.body:
            try:
                # Intentar formatear como JSON si es posible
                body_data = json.loads(obj.body) if isinstance(obj.body, str) else obj.body
                formatted = json.dumps(body_data, indent=2, ensure_ascii=False)
                return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', formatted)
            except:
                # Si no es JSON válido, mostrar como texto
                return format_html('<pre style="max-height: 200px; overflow-y: auto;">{}</pre>', obj.body[:1000])
        return "Sin body"
    body_display.short_description = "Cuerpo del request"


@admin.register(UserActivity)
class UserActivityAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        'timestamp', 'user_display', 'action', 'object_type', 
        'object_id', 'ip_address'
    ]
    list_filter = [
        'action', 'object_type', 'timestamp'
    ]
    search_fields = [
        'user__username', 'user__email', 'action', 'object_type', 
        'object_id', 'ip_address', 'description'
    ]
    readonly_fields = [
        'timestamp', 'user', 'action', 'object_type', 'object_id', 
        'description', 'ip_address'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Sistema"
    user_display.short_description = "Usuario"


@admin.register(ErrorLog)
class ErrorLogAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [
        'timestamp', 'user_display', 'level', 'message_short', 
        'request_path'
    ]
    list_filter = [
        'level', 'timestamp'
    ]
    search_fields = [
        'user__username', 'user__email', 'level', 'message', 
        'request_path', 'traceback'
    ]
    readonly_fields = [
        'timestamp', 'user', 'level', 'message', 'traceback_display', 
        'request_path', 'ip_address'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Sistema/Anónimo"
    user_display.short_description = "Usuario"
    
    def message_short(self, obj):
        if obj.message and len(obj.message) > 100:
            return f"{obj.message[:100]}..."
        return obj.message or "Sin mensaje"
    message_short.short_description = "Mensaje"
    
    def traceback_display(self, obj):
        if obj.traceback:
            return format_html(
                '<pre style="max-height: 400px; overflow-y: auto; background: #f8f8f8; padding: 10px; border: 1px solid #ddd;">{}</pre>', 
                obj.traceback
            )
        return "Sin traceback"
    traceback_display.short_description = "Stack trace"


# Personalización del admin site
admin.site.site_header = "EFC V2 "
admin.site.site_title = "EFC V2"
admin.site.index_title = "Administración del Sistema"
admin.site.site_url = SITE_URL