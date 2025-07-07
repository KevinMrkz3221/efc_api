from django.contrib import admin
from .models import Organizacion
# Register your models here.

class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'rfc', 'email', 'telefono', 'is_active', 'is_verified', 'inicia', 'vencimiento')
    search_fields = ('nombre', 'rfc', 'email')
    list_filter = ('is_active', 'is_verified')
    ordering = ('nombre',)

# class UsuarioOrganizacionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'email', 'telefono', 'puesto', 'is_active', 'is_verified')
#     search_fields = ('email', 'telefono', 'puesto')
#     list_filter = ('is_active', 'is_verified')
#     ordering = ('email',)

admin.site.register(Organizacion)
# admin.site.register(UsuarioOrganizacion)