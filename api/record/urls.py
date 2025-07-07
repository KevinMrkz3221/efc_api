# This file defines the URL patterns for the customs app in a Django project.
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# import necessary viewsets
# from .views import YourViewSet  # Import your viewsets here
from .views import  DocumentViewSet, ProtectedDocumentDownloadView, BulkDownloadZipView
# Create a router and register your viewsets with it

router = DefaultRouter()

# Register your viewsets with the router here
# Example:
# from .views import MyViewSet
# router.register(r'myviewset', MyViewSet, basename='myviewset')
router.register(r'documents', DocumentViewSet, basename='Document')
# No registres ProtectedDocumentDownloadView en el router, solo como path individual

urlpatterns = [
    path('documents/bulk-download/', BulkDownloadZipView.as_view(), name='bulk-download-documents'),
    path('documents/descargar/<uuid:pk>/', ProtectedDocumentDownloadView.as_view(), name='descargar-documento'),
    path('', include(router.urls)),
]