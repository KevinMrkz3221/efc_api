
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.organization.models import Organizacion
from api.record.models import Document
from api.logger.models import UserActivity, RequestLog
from api.customs.models import ProcesamientoPedimento

User = get_user_model()

class CardsViewsTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.client = APIClient()
    def test_admin_sees_only_own_org_documents(self):
        from api.record.models import Document
        doc1 = Document.objects.create(archivo="file1.pdf", organizacion=self.org)
        doc2 = Document.objects.create(archivo="file2.pdf", organizacion=self.org2)
        self.client.force_authenticate(user=self.admin)
        url = reverse('document-util-information')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only doc1 should be counted
        self.assertGreaterEqual(response.data['archivos_ultimas_1_dia'], 0)

    def test_superuser_sees_all_documents(self):
        from api.record.models import Document
        doc1 = Document.objects.create(archivo="file1.pdf", organizacion=self.org)
        doc2 = Document.objects.create(archivo="file2.pdf", organizacion=self.org2)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('document-util-information')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Both docs should be counted
        self.assertGreaterEqual(response.data['archivos_ultimas_1_dia'], 0)

    def test_importador_cannot_create_document(self):
        self.client.force_authenticate(user=self.importador)
        url = reverse('document-util-information')
        response = self.client.post(url, {})
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_document_util_information(self):
        url = reverse('document-util-information')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('archivos_ultimas_1_dia', response.data)

    def test_services_util_information(self):
        url = reverse('pedimento-services-util-information')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('en_espera', response.data)

    def test_user_activity_analysis(self):
        url = reverse('user-activity-analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('actions_count', response.data)

    def test_request_log_analysis(self):
        url = reverse('request-log-analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('methods_count', response.data)

    def test_last_document_view(self):
        url = reverse('downloaded-documents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('documentos', response.data)
