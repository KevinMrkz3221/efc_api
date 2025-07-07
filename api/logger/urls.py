from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestLogViewSet, UserActivityViewSet, ErrorLogViewSet

router = DefaultRouter()
router.register(r'requests', RequestLogViewSet)
router.register(r'activities', UserActivityViewSet)
router.register(r'errors', ErrorLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]