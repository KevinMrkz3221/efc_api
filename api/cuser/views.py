from .password_reset_utils import send_password_reset_email
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str

# Vista para solicitar recuperación de contraseña
from rest_framework import status

import uuid
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from rest_framework.exceptions import PermissionDenied
from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)

from .serializers import CustomUserSerializer
from .models import CustomUser
from api.logger.mixins import LoggingMixin
from api.vucem.models import Vucem
from mixins.filtrado_organizacion import OrganizacionFiltradaMixin

from .utils import send_activation_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from django.utils.encoding import force_str
from django.conf import settings

class CustomPagination(PageNumberPagination):

    """
    Paginación personalizada con parámetros flexibles
    - Si no se especifica page_size, devuelve todos los resultados (sin paginación)
    - Si se especifica page_size, usa paginación normal
    """
    page_size = None  # Sin paginación por defecto
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Límite máximo de seguridad
    page_query_param = 'page'
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Si no se especifica page_size en los parámetros, devolver None (sin paginación)
        Si se especifica, usar paginación normal
        """
        # Verificar si se especificó page_size en la query
        if self.page_size_query_param not in request.query_params:
            # No hay page_size, devolver None para indicar "sin paginación"
            return None
        
        # Hay page_size, usar paginación normal
        try:
            page_size = int(request.query_params[self.page_size_query_param])
            if page_size <= 0:
                return None
            # Establecer el page_size temporalmente para esta request
            self.page_size = min(page_size, self.max_page_size)
        except (ValueError, TypeError):
            return None
            
        return super().paginate_queryset(queryset, request, view)

class CustomUserViewSet(viewsets.ModelViewSet, OrganizacionFiltradaMixin):
    """
    ViewSet for CustomUser model.
    """
    permission_classes = [IsAuthenticated &  (IsSuperUser | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSameOrganization )]
    pagination_class = CustomPagination
    model = CustomUser
    serializer_class = CustomUserSerializer
    filterset_fields = ['username', 'email', 'first_name', 'last_name', 'organizacion', 'is_importador']
    my_tags = ['User Profile']
    

    def get_permissions(self):
        # Permitir eliminar usuarios solo a admin, Agente Aduanal y user de la misma organización
        if self.action == 'destroy':
            user = self.request.user
            if not (
                user.is_superuser or
                user.groups.filter(name='admin').exists() or
                user.groups.filter(name='Agente Aduanal').exists() or
                user.groups.filter(name='user').exists()
            ):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Solo admin, Agente Aduanal o user pueden eliminar usuarios.")
        elif self.action in ['create', 'update', 'partial_update']:
            if not (self.request.user.is_superuser or self.request.user.groups.filter(name='admin').exists()):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Solo admin o superusuario pueden modificar usuarios.")
        return super().get_permissions()

    def perform_destroy(self, instance):
        # Solo permitir eliminar usuarios de la misma organización
        if self.request.user.is_superuser or instance.organizacion == self.request.user.organizacion:
            instance.delete()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo puedes eliminar usuarios de tu organización.")

    def get_queryset(self):
        # Handle Swagger schema generation where user might be AnonymousUser
        if self.request.user.groups.filter(name='importador').exists():
            return CustomUser.objects.none()
        
        return self.get_queryset_filtrado_por_organizacion()

    def perform_create(self, serializer):
        # Always assign the creator's organization
        if self.request.user.groups.filter(name='admin').exists() and self.request.user.groups.filter(name='Agente Aduanal').exists():
            if not self.request.user.organizacion:
                raise PermissionDenied("Los administradores deben tener una organización asignada para crear usuarios.")
            user = serializer.save(organizacion=self.request.user.organizacion, is_active=False)
            send_activation_email(user, self.request)  # Usa template HTML
            return

        if self.request.user.is_superuser:
            # If superuser, allow creating users without organization
            user = serializer.save(is_active=False)
            send_activation_email(user, self.request)  # Usa template HTML
            return

        if self.request.user.groups.filter(name='developer').exists():
            # Developers can create users but must assign an organization
            if not self.request.user.organizacion:
                raise PermissionDenied("Los desarrolladores deben tener una organización asignada para crear usuarios.")
            user = serializer.save(organizacion=self.request.user.organizacion, is_active=False)
            send_activation_email(user, self.request)  # Usa template HTML
            return

        if self.request.user.groups.filter(name='importador').exists():
            # No puedes crear un usuario si eres importador
            raise PermissionDenied("Los importadores no pueden crear usuarios.")

        user = serializer.save(organizacion=self.request.user.organizacion, is_active=False)
        send_activation_email(user, self.request)  # Usa template HTML
        return
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener la información del usuario autenticado.
        GET /api/v1/user/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ActivateUserView(APIView):
    """
    Vista para activar usuario desde el link enviado por correo.
    """
    permission_classes = []  # Permitir acceso público a la activación de usuario
    my_tags = ['User Authentication']

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            from .models import CustomUser
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # Aquí puedes redirigir a una página de éxito o login
            return redirect(settings.SITE_URL + 'login?activated=1')
        else:
            return Response({'detail': 'El enlace de activación no es válido o ha expirado.'}, status=400)

    def perform_update(self, serializer):
        # Only allow update if user is in the same organization
        instance = self.get_object()
        if instance.organizacion != self.request.user.organizacion:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo puedes actualizar usuarios de tu organización.")

        password = serializer.validated_data.pop('password', None)

        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()

class ProfilePictureView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    my_tags = ['User Profile']

    def get(self, request, user_id):
        # Obtiene el usuario (automáticamente 404 si no existe)
        user = get_object_or_404(CustomUser, pk=user_id)
        
        # El permiso IsOwnerOrAdmin ya verificó que request.user == user o es admin
        # Así que no necesitas validar manualmente los permisos aquí.

        if not user.profile_picture:
            raise Http404("El usuario no tiene imagen de perfil")
        
        return FileResponse(user.profile_picture.open('rb'))

class PasswordResetRequestView(APIView):
    permission_classes = []  # Permitir acceso público a la recuperación de contraseña
    my_tags = ['User Authentication']
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        if not email or not username:
            return Response({'detail': 'Se requieren username y email.'}, status=400)
        User = get_user_model()
        try:
            user = User.objects.get(email=email, username=username)
        except User.DoesNotExist:
            return Response({'detail': 'No existe usuario con ese username y email.'}, status=404)
        send_password_reset_email(user, request)  # Usa template HTML
        return Response({'detail': 'Se ha enviado un correo para restablecer la contraseña.'}, status=status.HTTP_200_OK)
# Vista para confirmar recuperación de contraseña
class PasswordResetConfirmView(APIView):
    permission_classes = []  # Permitir acceso público a la confirmación de recuperación de contraseña
    my_tags = ['User Authentication']
    def post(self, request, uidb64, token):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Enlace inválido.'}, status=400)
        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Token inválido o expirado.'}, status=400)
        password = request.data.get('password')
        if not password:
            return Response({'detail': 'La nueva contraseña es requerida.'}, status=400)
        user.set_password(password)
        user.save()
        return Response({'detail': 'Contraseña restablecida correctamente.'}, status=status.HTTP_200_OK)