from rest_framework import serializers

from .models import Licencia

class LicenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licencia
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')