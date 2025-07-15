
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notificacion, TipoNotificacion
from api.organization.models import Organizacion

User = get_user_model()

class NotificacionesViewSetTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.client = APIClient()

    def test_list_tipo_notificacion(self):
        TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        self.client.force_authenticate(user=self.admin)
        url = reverse('tipo-notificacion-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_admin_sees_only_org_notificaciones(self):
        tipo = TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        notif1 = Notificacion.objects.create(tipo=tipo, dirigido=self.admin, mensaje="msg1")
        notif2 = Notificacion.objects.create(tipo=tipo, dirigido=self.importador, mensaje="msg2")
        self.client.force_authenticate(user=self.admin)
        url = reverse('notificacion-list')
        response = self.client.get(url)
        mensajes = [n['mensaje'] for n in response.data]
        self.assertIn("msg1", mensajes)
        self.assertNotIn("msg2", mensajes)

    def test_superuser_sees_all_notificaciones(self):
        tipo = TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        notif1 = Notificacion.objects.create(tipo=tipo, dirigido=self.admin, mensaje="msg1")
        notif2 = Notificacion.objects.create(tipo=tipo, dirigido=self.importador, mensaje="msg2")
        self.client.force_authenticate(user=self.superuser)
        url = reverse('notificacion-list')
        response = self.client.get(url)
        mensajes = [n['mensaje'] for n in response.data]
        self.assertIn("msg1", mensajes)
        self.assertIn("msg2", mensajes)

    def test_importador_sees_only_own_notificaciones(self):
        tipo = TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        notif1 = Notificacion.objects.create(tipo=tipo, dirigido=self.admin, mensaje="msg1")
        notif2 = Notificacion.objects.create(tipo=tipo, dirigido=self.importador, mensaje="msg2")
        self.client.force_authenticate(user=self.importador)
        url = reverse('notificacion-list')
        response = self.client.get(url)
        mensajes = [n['mensaje'] for n in response.data]
        self.assertNotIn("msg1", mensajes)
        self.assertIn("msg2", mensajes)

    def test_superuser_can_create_notificacion(self):
        tipo = TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        self.client.force_authenticate(user=self.superuser)
        url = reverse('notificacion-list')
        data = {"tipo": tipo.id, "dirigido": self.admin.id, "mensaje": "msg3"}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_admin_cannot_create_notificacion(self):
        tipo = TipoNotificacion.objects.create(tipo="info", descripcion="informativa")
        self.client.force_authenticate(user=self.admin)
        url = reverse('notificacion-list')
        data = {"tipo": tipo.id, "dirigido": self.importador.id, "mensaje": "msg4"}
        response = self.client.post(url, data)
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
