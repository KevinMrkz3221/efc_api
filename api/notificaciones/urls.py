from rest_framework import routers
from django.urls import path, include
from .views import TipoNotificacionViewSet, NotificacionViewSet

# Create a router and register the viewsets
router = routers.DefaultRouter()
router.register(r'tipos', TipoNotificacionViewSet, basename='tipo-notificacion')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

# Create a router and register the healthcheck view
urlpatterns = [
    path('', include(router.urls)),
]