import uuid
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

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

class CustomUserViewSet(viewsets.ModelViewSet, OrganizacionFiltradaMixin):
    """
    ViewSet for CustomUser model.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = CustomUser
    serializer_class = CustomUserSerializer
    filterset_fields = ['username', 'email', 'first_name', 'last_name', 'organizacion', 'is_importador']
    my_tags = ['User Profile']
    
    def get_permissions(self):
        # Only admin and superuser can modify users
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if not (self.request.user.is_superuser or self.request.user.groups.filter(name='admin').exists()):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Solo admin o superusuario pueden modificar usuarios.")

        return super().get_permissions()

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
            serializer.save(organizacion=self.request.user.organizacion)
        
        if self.request.user.is_superuser:
            # If superuser, allow creating users without organization
            serializer.save()
        
        if self.request.user.groups.filter(name='developer').exists():
            # Developers can create users but must assign an organization
            if not self.request.user.organizacion:
                raise PermissionDenied("Los desarrolladores deben tener una organización asignada para crear usuarios.")
            serializer.save(organizacion=self.request.user.organizacion)
        
        if self.request.user.groups.filter(name='importador').exists():
            # No puedes crear un usuario si eres importador
            raise PermissionDenied("Los importadores no pueden crear usuarios.")
        
        serializer.save(organizacion=self.request.user.organizacion)

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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint para obtener la información del usuario autenticado.
        GET /api/v1/user/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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

