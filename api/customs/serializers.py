from rest_framework import serializers
from api.customs.models import Pedimento, Aduana, AgenteAduanal, ClavePedimento, TipoOperacion, ProcesamientoPedimento, Regimen
from api.record.models import Document  # Asegúrate de importar el modelo Documento
from api.record.serializers import DocumentSerializer  

class PedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedimento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')

class AgenteAduanalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenteAduanal
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class AduanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aduana
        fields = '__all__'

class ClavePedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClavePedimento
        fields = '__all__'

class TipoOperacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoOperacion
        fields = '__all__'

class ProcesamientoPedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcesamientoPedimento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['pedimento'] = PedimentoSerializer(instance.pedimento).data
        return representation
    
class RegimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regimen
        fields = '__all__'