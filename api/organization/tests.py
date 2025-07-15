
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Organizacion, UsoAlmacenamiento
from api.licence.models import Licencia

User = get_user_model()

class OrganizationViewSetTests(APITestCase):
    def setUp(self):
        self.lic = Licencia.objects.create(nombre="LicTest", almacenamiento=100)
        self.org = Organizacion.objects.create(nombre="OrgTest", licencia=self.lic, is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", licencia=self.lic, is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.client = APIClient()

    def test_admin_sees_only_own_organization(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('Organizacion-list')
        response = self.client.get(url)
        nombres = [o['nombre'] for o in response.data]
        self.assertIn("OrgTest", nombres)
        self.assertNotIn("OrgTest2", nombres)

    def test_superuser_sees_all_organizations(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('Organizacion-list')
        response = self.client.get(url)
        nombres = [o['nombre'] for o in response.data]
        self.assertIn("OrgTest", nombres)
        self.assertIn("OrgTest2", nombres)

    def test_admin_sees_only_own_storage(self):
        UsoAlmacenamiento.objects.create(organizacion=self.org, espacio_utilizado=1000)
        UsoAlmacenamiento.objects.create(organizacion=self.org2, espacio_utilizado=2000)
        self.client.force_authenticate(user=self.admin)
        url = reverse('UsoAlmacenamiento-list')
        response = self.client.get(url)
        orgs = [u['organizacion'] for u in response.data]
        self.assertIn(self.org.id, orgs)
        self.assertNotIn(self.org2.id, orgs)

    def test_superuser_sees_all_storage(self):
        UsoAlmacenamiento.objects.create(organizacion=self.org, espacio_utilizado=1000)
        UsoAlmacenamiento.objects.create(organizacion=self.org2, espacio_utilizado=2000)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('UsoAlmacenamiento-list')
        response = self.client.get(url)
        orgs = [u['organizacion'] for u in response.data]
        self.assertIn(self.org.id, orgs)
        self.assertIn(self.org2.id, orgs)

    def test_importador_cannot_access_storage(self):
        UsoAlmacenamiento.objects.create(organizacion=self.org2, espacio_utilizado=2000)
        self.client.force_authenticate(user=self.importador)
        url = reverse('UsoAlmacenamiento-list')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)