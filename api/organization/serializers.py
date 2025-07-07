from rest_framework import serializers

from .models import Organizacion, UsoAlmacenamiento#, UsuarioOrganizacion

class OrganizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizacion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class UsoAlmacenamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsoAlmacenamiento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')