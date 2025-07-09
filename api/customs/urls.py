# This file defines the URL patterns for the customs app in a Django project.
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# import necessary viewsets
from .views import (
    ViewSetPedimento,
    ViewSetAgenteAduanal,
    ViewSetAduana,
    ViewSetClavePedimento,
    ViewSetTipoOperacion,
    ViewSetProcesamientoPedimento,
    ViewSetRegimen,
    ViewSetEDocument
)
# from .views import YourViewSet  # Import your viewsets here

router = DefaultRouter()

# Register your viewsets with the router here
# Example:
# from .views import MyViewSet
# router.register(r'myviewset', MyViewSet, basename='myviewset')

router.register(r'pedimentos', ViewSetPedimento, basename='Pedimento')
router.register(r'agentesaduanales', ViewSetAgenteAduanal, basename='AgenteAduanal')
router.register(r'aduanas', ViewSetAduana, basename='Aduana')
router.register(r'clavespedimento', ViewSetClavePedimento, basename='ClavePedimento')
router.register(r'tiposoperacion', ViewSetTipoOperacion, basename='TipoOperacion')
router.register(r'procesamientopedimentos', ViewSetProcesamientoPedimento, basename='ProcesamientoPedimento')
router.register(r'regimenes', ViewSetRegimen, basename='Regimen')
router.register(r'edocuments', ViewSetEDocument, basename='EDocument')

# Import your viewsets here

urlpatterns = [
    path('', include(router.urls)),
]