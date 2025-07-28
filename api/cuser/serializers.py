
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.models import Group

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    """

    password = serializers.CharField(write_only=True)
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)


    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'profile_picture', 'organizacion', 'is_importador', 'rfc', 'is_active', 'is_superuser', 'groups']
        read_only_fields = ['id', 'organizacion', 'is_superuser']

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        if groups:
            user.groups.set(groups)
        return user
