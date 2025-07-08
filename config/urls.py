"""
URL configuration for confischema_view = get_schema_view(
   openapi.Info(
      title="EFC API",
      default_version='v1',
      description="API para el sistema EFC V2 - Gestión de Pedimentos y Aduanas.\n\n"
                 "## Autenticación\n"
                 "Esta API utiliza JWT (JSON Web Tokens) para autenticación.\n\n"
                 "### Cómo obtener un token:\n"
                 "1. Haz POST a `/api/v1/token/` con username y password\n"
                 "2. Usa el token obtenido en el header: `Authorization: Bearer {token}`\n\n"
                 "### Endpoints principales:\n"
                 "- **Autenticación**: `/api/v1/token/` - Obtener token JWT\n"
                 "- **Refresh Token**: `/api/v1/token/refresh/` - Renovar token\n"
                 "- **Pedimentos**: `/api/v1/customs/pedimentos/` - Gestión de pedimentos\n"
                 "- **Documentos**: `/api/v1/record/documents/` - Gestión de documentos\n",
      terms_of_service="https://www.aduanasoft.com.mx/terms/",
      contact=openapi.Contact(email="support@aduanasoft.com.mx"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[],  # Desactivar auth para ver la documentación
)he `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
# 
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="EFC API",
      default_version='v1',
      description="API para el sistema EFC V2 - Gestión de Expediente electronicos de Comercio Exterior",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@aduanasoft.com.mx"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[],  # Desactivar auth para ver la documentación
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.licence.urls')),

    # JWT Authentication
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/user/', include('api.cuser.urls')),  # Custom user app

    #path('api-auth/', include('rest_framework.urls')),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/v1/customs/', include('api.customs.urls')),
    path('api/v1/organization/', include('api.organization.urls')),
    path('api/v1/record/', include('api.record.urls')),
    path('api/v1/datastage/', include('api.datastage.urls')),
    path('api/v1/vucem/', include('api.vucem.urls')),
    path('api/v1/logger/', include('api.logger.urls')),  # Logger app
    
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)