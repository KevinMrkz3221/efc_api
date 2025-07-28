from django.urls import path, include
from .views import ProfilePictureView, ActivateUserView, PasswordResetRequestView, PasswordResetConfirmView, CustomUserViewSet
customuser_me = CustomUserViewSet.as_view({'get': 'me'})
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')


urlpatterns = [
    path('', include(router.urls)),
    path('me/', customuser_me, name='user-me'),
    path('profile-picture/<uuid:user_id>/', ProfilePictureView.as_view(), name='profile-picture'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]