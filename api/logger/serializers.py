from rest_framework import serializers
from .models import RequestLog, UserActivity, ErrorLog
from api.cuser.models import CustomUser

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class RequestLogSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = RequestLog
        fields = '__all__'

class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = UserActivity
        fields = '__all__'

class ErrorLogSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = ErrorLog
        fields = '__all__'