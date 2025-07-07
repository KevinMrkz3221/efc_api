from rest_framework import serializers

from .models import Document



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ('id', 'organizacion', 'pedimento', 'archivo', 'document_type', 'size', 'extension', 'created_at', 'updated_at')
        read_only_fields = ('id', 'organizacion', 'size', 'extension', 'created_at', 'updated_at')
        
    def validate_archivo(self, value):
        """Validar que se proporcione un archivo"""
        if not value:
            raise serializers.ValidationError("Se requiere un archivo para subir")
        return value