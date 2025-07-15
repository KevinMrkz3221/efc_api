
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.organization.models import Organizacion
from .models import DataStage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DataStageViewSetTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.client = APIClient()

    def test_admin_sees_only_own_org(self):
        ds1 = DataStage.objects.create(nombre="DS1", almacenamiento=10, organizacion=self.org, archivo=SimpleUploadedFile("a.txt", b"a"))
        ds2 = DataStage.objects.create(nombre="DS2", almacenamiento=20, organizacion=self.org2, archivo=SimpleUploadedFile("b.txt", b"b"))
        self.client.force_authenticate(user=self.admin)
        url = reverse('datastage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [ds['nombre'] for ds in response.data]
        self.assertIn("DS1", nombres)
        self.assertNotIn("DS2", nombres)

    def test_superuser_sees_all(self):
        ds1 = DataStage.objects.create(nombre="DS1", almacenamiento=10, organizacion=self.org, archivo=SimpleUploadedFile("a.txt", b"a"))
        ds2 = DataStage.objects.create(nombre="DS2", almacenamiento=20, organizacion=self.org2, archivo=SimpleUploadedFile("b.txt", b"b"))
        self.client.force_authenticate(user=self.superuser)
        url = reverse('datastage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nombres = [ds['nombre'] for ds in response.data]
        self.assertIn("DS1", nombres)
        self.assertIn("DS2", nombres)

    def test_importador_cannot_create(self):
        self.client.force_authenticate(user=self.importador)
        url = reverse('datastage-list')
        file_content = BytesIO(b"dummy data")
        file = SimpleUploadedFile("test.txt", file_content.read(), content_type="text/plain")
        data = {
            "nombre": "DataStageImportador",
            "almacenamiento": 10,
            "archivo": file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_list_datastages(self):
        url = reverse('datastage-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_datastage(self):
        url = reverse('datastage-list')
        file_content = BytesIO(b"dummy data")
        file = SimpleUploadedFile("test.txt", file_content.read(), content_type="text/plain")
        data = {
            "nombre": "DataStageTest",
            "almacenamiento": 10,
            "archivo": file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_update_datastage(self):
        # First create
        file_content = BytesIO(b"dummy data")
        file = SimpleUploadedFile("test.txt", file_content.read(), content_type="text/plain")
        ds = DataStage.objects.create(nombre="DataStageTest", almacenamiento=10, organizacion=self.org, archivo=file)
        url = reverse('datastage-detail', args=[ds.id])
        data = {"almacenamiento": 20}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['almacenamiento'], 20)
