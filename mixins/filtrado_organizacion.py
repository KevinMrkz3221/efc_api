import logging
logger = logging.getLogger(__name__)

class FiltroPorOrganizacionMixin:
    model = None
    campo_usuario = 'user'
    campo_organizacion = 'organizacion'
    campo_rfc = 'rfc'
    campo_contribuyente = 'pedimento__contribuyente'  # solo si aplica

    def get_queryset_filtrado(self):
        user = self.request.user

        if not user.is_authenticated or not hasattr(user, self.campo_organizacion):
            return self.model.objects.none()

        if user.is_superuser:
            return self.model.objects.all()

        if (user.groups.filter(name='admin').exists() or user.groups.filter(name='developer').exists()) and user.is_authenticated and user.groups.filter(name='Agente Aduanal').exists():
            model_fields = [f.name for f in self.model._meta.get_fields()]
            if self.campo_organizacion in model_fields:
                filtro = {f"{self.campo_organizacion}": getattr(user, self.campo_organizacion)}
            elif self.campo_usuario in model_fields:
                filtro = {f"{self.campo_usuario}": user}
            else:
                return self.model.objects.none()
            return self.model.objects.filter(**filtro)

        if user.groups.filter(name='importador').exists() and getattr(user, 'is_importador', False):
            filtro = {
                f"{self.campo_usuario}__{self.campo_rfc}": getattr(user, self.campo_rfc),
                f"{self.campo_usuario}__{self.campo_organizacion}": getattr(user, self.campo_organizacion)
            }
            return self.model.objects.filter(**filtro)

        return self.model.objects.none()
        
# en core/mixins/organizacion.py o similar
class OrganizacionFiltradaMixin:
    model = None  # Puedes sobreescribir esto en la vista
    campo_organizacion = 'organizacion'
    campo_contribuyente = 'contribuyente'  # solo si aplica

    def get_queryset_filtrado_por_organizacion(self):
        model = self.model or self.queryset.model

        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return model.objects.none()

        if self.request.user.is_superuser:
            return model.objects.all()

        org = self.request.user.organizacion
        filtros_base = {
            f"{self.campo_organizacion}": org,
            f"{self.campo_organizacion}__is_active": True,
            f"{self.campo_organizacion}__is_verified": True,
        }

        grupos = self.request.user.groups.values_list('name', flat=True)

        if self.request.user.is_authenticated and 'Agente Aduanal' in grupos and (('admin' in grupos or 'developer' in grupos) and 'user' in grupos) :
            if 'Agente Aduanal' in grupos:
                return model.objects.filter(**filtros_base)
        
        if hasattr(model, self.campo_contribuyente):
            if self.request.user.is_authenticated and'Importador' in grupos and getattr(self.request.user, 'is_importador', False):
                filtros_base[f"{self.campo_contribuyente}"] = self.request.user.rfc
                return model.objects.filter(**filtros_base)

        # Si no entra en los roles válidos
        return model.objects.none()

class DocumentosFiltradosMixin:
    model = None
    campo_organizacion = 'organizacion'
    campo_contribuyente = 'pedimento'  # solo si aplica

    def get_queryset_filtrado_por_organizacion(self):
        model = self.model or self.queryset.model

        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return model.objects.none()

        if self.request.user.is_superuser:
            return model.objects.all()

        org = self.request.user.organizacion
        filtros_base = {
            f"{self.campo_organizacion}": org.id,
            f"{self.campo_organizacion}__is_active": True,
            f"{self.campo_organizacion}__is_verified": True,
        }

        grupos = self.request.user.groups.values_list('name', flat=True)

        if self.request.user.is_authenticated and 'Agente Aduanal' in grupos and ('admin' in grupos or 'developer' in grupos or 'user' in grupos):
            if 'Agente Aduanal' in grupos:
                return model.objects.filter(**filtros_base)
        
        if hasattr(model, self.campo_contribuyente):
            if self.request.user.is_authenticated and 'Importador' in grupos and getattr(self.request.user, 'is_importador', False):
                filtros_base[f"{self.campo_contribuyente}__contribuyente"] = self.request.user.rfc
                return model.objects.filter(**filtros_base)

        # Si no entra en los roles válidos
        return model.objects.none()

class ProcesosPorOrganizacionMixin:
    model = None  # Puedes sobreescribir esto en la vista
    campo_organizacion = 'organizacion'
    campo_pedimento = 'pedimento'  # solo si aplica

    def get_queryset_filtrado_por_organizacion(self):
        model = self.model or self.queryset.model

        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return model.objects.none()

        if self.request.user.is_superuser:
            return model.objects.all()

        org = self.request.user.organizacion
        filtros_base = {
            f"{self.campo_organizacion}": org,
            f"{self.campo_organizacion}__is_active": True,
            f"{self.campo_organizacion}__is_verified": True,
        }

        grupos = self.request.user.groups.values_list('name', flat=True)


        if self.request.user.is_authenticated and 'Agente Aduanal' in grupos and ('admin' in grupos or 'developer' in grupos or 'user' in grupos) :
            if 'Agente Aduanal' in grupos:
                return model.objects.filter(**filtros_base)
        
        if hasattr(model, self.campo_pedimento):
            if self.request.user.is_authenticated and'Importador' in grupos and getattr(self.request.user, 'is_importador', False):
                filtros_base[f"{self.campo_pedimento}__contribuyente"] = self.request.user.rfc
                return model.objects.filter(**filtros_base)

        # Si no entra en los roles válidos
        return model.objects.none()

