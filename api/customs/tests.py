
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.organization.models import Organizacion
from .models import Pedimento, TipoOperacion, ProcesamientoPedimento, EDocument

User = get_user_model()


class CustomsViewsTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.client = APIClient()

    def test_admin_sees_only_own_pedimentos(self):
        from .models import Pedimento
        p1 = Pedimento.objects.create(pedimento="P1", organizacion=self.org)
        p2 = Pedimento.objects.create(pedimento="P2", organizacion=self.org2)
        self.client.force_authenticate(user=self.admin)
        url = reverse('Pedimento-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedimentos = [p['pedimento'] for p in response.data]
        self.assertIn("P1", pedimentos)
        self.assertNotIn("P2", pedimentos)

    def test_superuser_sees_all_pedimentos(self):
        from .models import Pedimento
        p1 = Pedimento.objects.create(pedimento="P1", organizacion=self.org)
        p2 = Pedimento.objects.create(pedimento="P2", organizacion=self.org2)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('Pedimento-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedimentos = [p['pedimento'] for p in response.data]
        self.assertIn("P1", pedimentos)
        self.assertIn("P2", pedimentos)

    def test_importador_cannot_create_pedimento(self):
        self.client.force_authenticate(user=self.importador)
        url = reverse('Pedimento-list')
        data = {
            "pedimento": "P3",
            "patente": "1234",
            "aduana": "001",
            "regimen": "A1",
            "clave_pedimento": "A1",
            "contribuyente": "ImportadorTest"
        }
        response = self.client.post(url, data)
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_list_tipos_operacion(self):
        url = reverse('TipoOperacion-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_procesamientos(self):
        url = reverse('ProcesamientoPedimento-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_edocuments(self):
        url = reverse('EDocument-list')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
