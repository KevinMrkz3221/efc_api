from rest_framework import serializers
from api.customs.models import (
    Pedimento, 
    TipoOperacion, 
    ProcesamientoPedimento, 
    EDocument
)

from api.record.models import Document  # Asegúrate de importar el modelo Documento
from api.record.serializers import DocumentSerializer  

class PedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedimento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')

class TipoOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoOperacion
        fields = '__all__'

class ProcesamientoPedimentoSerializer(serializers.ModelSerializer):
    organizacion_name = serializers.CharField(source='organizacion.nombre', read_only=True)
    class Meta:
        model = ProcesamientoPedimento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['pedimento'] = PedimentoSerializer(instance.pedimento).data
        return representation
    
class EDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EDocument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si no es superusuario, hacer organizacion read_only
        request = self.context.get('request')
        if request and hasattr(request, 'user') and not request.user.is_superuser:
            self.fields['organizacion'].read_only = True