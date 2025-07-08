from rest_framework import routers
from .views import healthcheck

from django.urls import path, include

# Create a router and register the healthcheck view