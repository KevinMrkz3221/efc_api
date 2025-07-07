from rest_framework import serializers

from .models import DataStage


class DataStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStage
        fields = (
            'id',
            'nombre',
            'almacenamiento',
            'organizacion',
            'archivo',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')