from django.urls import path, include
from .views import ProfilePictureView
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')


urlpatterns = [
    path('', include(router.urls)),
    path('profile-picture/<uuid:user_id>/', ProfilePictureView.as_view(), name='profile-picture'),
]