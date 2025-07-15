from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile_picture', 'organizacion', 'is_importador', 'rfc', 'is_active', 'is_superuser']
        read_only_fields = ['id', 'organizacion', 'is_superuser']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # ✅ esto hashea la contraseña
        user.save()
        return user
