from rest_framework import serializers
from .models import Notificacion, TipoNotificacion

class TipoNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoNotificacion
        fields = ['id', 'tipo', 'descripcion']
        read_only_fields = ['id', 'tipo', 'descripcion']


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'id',
            'tipo',
            'dirigido',
            'mensaje',
            'fecha_envio',
            'created_at',
            'visto'
        ]
        read_only_fields = ['id', 'created_at', 'tipo', 'dirigido', 'fecha_envio', 'mensaje']

    