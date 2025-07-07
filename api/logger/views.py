from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, UserActivity, ErrorLog
from .serializers import RequestLogSerializer, UserActivitySerializer, ErrorLogSerializer
from .utils import log_user_activity

class RequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequestLog.objects.all()
    serializer_class = RequestLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'status_code', 'user']
    search_fields = ['path', 'ip_address', 'user_agent']
    ordering_fields = ['timestamp', 'response_time', 'status_code']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas de requests"""
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        stats = {
            'total_requests': self.queryset.count(),
            'today_requests': self.queryset.filter(timestamp__date=today).count(),
            'week_requests': self.queryset.filter(timestamp__gte=week_ago).count(),
            'methods': self.queryset.values('method').annotate(count=Count('method')),
            'status_codes': self.queryset.values('status_code').annotate(count=Count('status_code')),
            'top_endpoints': self.queryset.values('path').annotate(count=Count('path')).order_by('-count')[:10],
            'avg_response_time': self.queryset.aggregate(avg_time=Count('response_time'))['avg_time']
        }
        
        return Response(stats)

class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user', 'object_type']
    search_fields = ['description', 'object_id']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        # Check if user is authenticated first
        if not self.request.user.is_authenticated:
            return UserActivity.objects.none()
        
        # Los usuarios normales solo ven su propia actividad
        if self.request.user.is_staff:
            return UserActivity.objects.all()
        return UserActivity.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_activity(self, request):
        """Actividad del usuario actual"""
        if not request.user.is_authenticated:
            return Response({"error": "Usuario no autenticado"}, status=401)
        
        activities = UserActivity.objects.filter(user=request.user)[:20]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

class ErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'user']
    search_fields = ['message', 'request_path']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def recent_errors(self, request):
        """Errores recientes (últimas 24 horas)"""
        yesterday = timezone.now() - timedelta(days=1)
        recent_errors = self.queryset.filter(timestamp__gte=yesterday)
        serializer = self.get_serializer(recent_errors, many=True)
        return Response(serializer.data)