from django.contrib import admin
from .models import Licencia
# Register your models here.

class LicenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)
    list_filter = ('nombre',)

admin.site.register(Licencia, LicenciaAdmin)