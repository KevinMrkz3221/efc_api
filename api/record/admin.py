from django.contrib import admin
from .models import Document, DocumentType

# Register your models here.

class DocumentAdmin(admin.ModelAdmin):
    model = Document
    list_display = ('id', 'pedimento', 'archivo', 'size', 'extension', 'created_at', 'updated_at')
    search_fields = ('pedimento.pedimento', 'archivo')
    list_filter = ('created_at', 'updated_at')

class DocumentTypeAdmin(admin.ModelAdmin):
    model = DocumentType
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)