from django.db import models
from api.cuser.models import CustomUser as User  # Asegúrate de que este es el modelo de usuario correcto
from django.utils import timezone

class RequestLog(models.Model):
    METHODS = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('OPTIONS', 'OPTIONS'),
        ('HEAD', 'HEAD'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    method = models.CharField(max_length=10, choices=METHODS)
    path = models.URLField(max_length=500)
    query_params = models.TextField(blank=True)
    body = models.TextField(blank=True)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # en milisegundos
    timestamp = models.DateTimeField(default=timezone.now)
    referer = models.URLField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'logger_request_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.timestamp})"

class UserActivity(models.Model):
    ACTIONS = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('search', 'Search'),
        ('export', 'Export'),
        ('import', 'Import'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTIONS)
    object_type = models.CharField(max_length=100, blank=True)  # modelo afectado
    object_id = models.CharField(max_length=100, blank=True)   # ID del objeto
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'logger_user_activity'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} ({self.timestamp})"

class ErrorLog(models.Model):
    ERROR_LEVELS = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )
    
    level = models.CharField(max_length=10, choices=ERROR_LEVELS)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_path = models.URLField(max_length=500, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'logger_error_log'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.level}: {self.message[:50]}... ({self.timestamp})"




