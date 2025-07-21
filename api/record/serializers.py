from rest_framework import serializers

from .models import Document



from api.customs.models import Pedimento

class DocumentSerializer(serializers.ModelSerializer):
    pedimento_numero = serializers.SerializerMethodField(read_only=True)
    pedimento = serializers.PrimaryKeyRelatedField(queryset=Pedimento.objects.all())

    class Meta:
        model = Document
        fields = ('id', 'organizacion', 'pedimento', 'pedimento_numero', 'archivo', 'document_type', 'size', 'extension', 'created_at', 'updated_at')
        read_only_fields = ('id', 'organizacion', 'size', 'extension', 'created_at', 'updated_at', 'pedimento_numero')

    def get_pedimento_numero(self, obj):
        if obj.pedimento:
            return obj.pedimento.pedimento
        return None

    def validate_archivo(self, value):
        """Validar que se proporcione un archivo"""
        if not value:
            raise serializers.ValidationError("Se requiere un archivo para subir")
        return value