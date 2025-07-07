from rest_framework import serializers
from api.customs.models import Pedimento, Aduana, AgenteAduanal, ClavePedimento, TipoOperacion, ProcesamientoPedimento, Regimen
from api.record.models import Document  # Asegúrate de importar el modelo Documento
from api.record.serializers import DocumentSerializer  

class PedimentoSerializer(serializers.ModelSerializer):
    documentos = DocumentSerializer(many=True, read_only=True, source='documents')
    
    class Meta:
        model = Pedimento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es una actualización (PUT/PATCH), hacer opcionales ciertos campos
        if self.instance is not None:
            # Campos que no son requeridos en actualizaciones
            optional_fields = [
                'fecha_inicio', 
                'fecha_fin', 
                'importe_total', 
                'saldo_disponible', 
                'importe_pedimento'
            ]
            
            for field_name in optional_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = False

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