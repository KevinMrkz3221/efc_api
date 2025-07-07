from rest_framework import serializers
from .models import Vucem


class VucemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vucem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'organizacion')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Aquí puedes agregar lógica adicional si es necesario
        return representation