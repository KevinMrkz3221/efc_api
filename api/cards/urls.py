from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentUtilInformation,
    ViewPedimentoServicesUtilInformation,
    UserActivityAnalysis,
    RequestLogAnalysis,
    LastDocumentView,
)


# Create a router and register our viewset with it.

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('document-util-information/', DocumentUtilInformation.as_view(), name='document-util-information'),
    path('services-util-information/', ViewPedimentoServicesUtilInformation.as_view(), name='pedimento-services-util-information'),
    path('user-activity-analysis/', UserActivityAnalysis.as_view(), name='user-activity-analysis'),
    path('request-log-analysis/', RequestLogAnalysis.as_view(), name='request-log-analysis'),
    path('downloaded-documents/', LastDocumentView.as_view(), name='downloaded-documents'),
]