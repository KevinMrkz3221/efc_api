from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VucemView
# Create a router and register your viewsets with it
router = DefaultRouter()


# Register your viewsets with the router here

router.register(r'vucem', VucemView, basename='Vucem')
urlpatterns = [
    path('', include(router.urls)),
]