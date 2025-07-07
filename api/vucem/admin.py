from django.contrib import admin
from .models import Vucem

# Register your models here.

class VucemAdmin(admin.ModelAdmin):
    list_display = ('id', 'organizacion', 'usuario', 'patente', 'is_importador', 'is_active', 'created_at', 'updated_at')
    search_fields = ('usuario', 'patente')
    list_filter = ('is_importador', 'acusecove', 'acuseedocument', 'is_active')
    ordering = ('-created_at',)

admin.site.register(Vucem, VucemAdmin)