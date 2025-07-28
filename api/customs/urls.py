# This file defines the URL patterns for the customs app in a Django project.
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# import necessary viewsets
from .views import (
    ViewSetPedimento,
    ViewSetTipoOperacion,
    ViewSetProcesamientoPedimento,
    ViewSetEDocument,
    ViewSetCove
)
# from .views import YourViewSet  # Import your viewsets here

router = DefaultRouter()

# Register your viewsets with the router here
# Example:
# from .views import MyViewSet
# router.register(r'myviewset', MyViewSet, basename='myviewset')

router.register(r'pedimentos', ViewSetPedimento, basename='Pedimento')
router.register(r'tiposoperacion', ViewSetTipoOperacion, basename='TipoOperacion')
router.register(r'procesamientopedimentos', ViewSetProcesamientoPedimento, basename='ProcesamientoPedimento')
router.register(r'edocuments', ViewSetEDocument, basename='EDocument')
router.register(r'coves', ViewSetCove, basename='Cove')

# Import your viewsets here

urlpatterns = [
    path('', include(router.urls)),
]