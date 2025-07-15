
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Licencia

User = get_user_model()

class LicenciaViewSetTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.user = User.objects.create_user(username="user", password="userpass")
        self.client = APIClient()

    def test_superuser_can_list_licencias(self):
        Licencia.objects.create(nombre="Lic1", descripcion="desc1", almacenamiento=10)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('licencia-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_superuser_can_create_licencia(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse('licencia-list')
        data = {"nombre": "Lic2", "descripcion": "desc2", "almacenamiento": 20}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_superuser_can_update_licencia(self):
        lic = Licencia.objects.create(nombre="Lic3", descripcion="desc3", almacenamiento=30)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('licencia-detail', args=[lic.id])
        data = {"descripcion": "updated"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descripcion'], "updated")

    def test_user_cannot_create_licencia(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('licencia-list')
        data = {"nombre": "Lic4", "descripcion": "desc4", "almacenamiento": 40}
        response = self.client.post(url, data)
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_user_cannot_update_licencia(self):
        lic = Licencia.objects.create(nombre="Lic5", descripcion="desc5", almacenamiento=50)
        self.client.force_authenticate(user=self.user)
        url = reverse('licencia-detail', args=[lic.id])
        data = {"descripcion": "updated"}
        response = self.client.patch(url, data)
        self.assertNotIn(response.status_code, [status.HTTP_200_OK])
