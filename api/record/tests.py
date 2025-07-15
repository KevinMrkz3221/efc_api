
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from api.organization.models import Organizacion, UsoAlmacenamiento
from api.cuser.models import CustomUser
from api.customs.models import Pedimento
from .models import Document
import io

class DocumentViewSetTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.pedimento = Pedimento.objects.create(organizacion=self.org, numero="123456")
        self.admin = CustomUser.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = CustomUser.objects.create_superuser(username="superuser", password="superpass")
        self.client = APIClient()

    def test_list_documents_only_own_org(self):
        doc1 = Document.objects.create(organizacion=self.org, pedimento=self.pedimento, archivo="documents/test1.pdf", size=100, extension="pdf")
        org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        ped2 = Pedimento.objects.create(organizacion=org2, numero="654321")
        Document.objects.create(organizacion=org2, pedimento=ped2, archivo="documents/test2.pdf", size=200, extension="pdf")
        self.client.force_authenticate(user=self.admin)
        url = reverse('Document-list')
        response = self.client.get(url)
        ids = [d['id'] for d in response.data]
        self.assertIn(str(doc1.id), ids)
        self.assertEqual(len(ids), 1)

    def test_create_document_success(self):
        self.client.force_authenticate(user=self.admin)
        file_content = b"dummy pdf content"
        archivo = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")
        url = reverse('Document-list')
        data = {
            "pedimento": str(self.pedimento.id),
            "archivo": archivo,
            "size": len(file_content),
            "extension": "pdf"
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc = Document.objects.get(id=response.data['id'])
        self.assertEqual(doc.organizacion, self.org)

    def test_update_document_size(self):
        doc = Document.objects.create(organizacion=self.org, pedimento=self.pedimento, archivo="documents/test1.pdf", size=100, extension="pdf")
        self.client.force_authenticate(user=self.admin)
        url = reverse('Document-detail', args=[doc.id])
        file_content = b"new content"
        archivo = SimpleUploadedFile("test2.pdf", file_content, content_type="application/pdf")
        data = {
            "archivo": archivo,
            "size": len(file_content),
            "extension": "pdf"
        }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc.refresh_from_db()
        self.assertEqual(doc.size, len(file_content))

    def test_delete_document_frees_storage(self):
        doc = Document.objects.create(organizacion=self.org, pedimento=self.pedimento, archivo="documents/test1.pdf", size=100, extension="pdf")
        UsoAlmacenamiento.objects.create(organizacion=self.org, espacio_utilizado=100)
        self.client.force_authenticate(user=self.admin)
        url = reverse('Document-detail', args=[doc.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        uso = UsoAlmacenamiento.objects.get(organizacion=self.org)
        self.assertEqual(uso.espacio_utilizado, 0)

    def test_permission_denied_for_other_org(self):
        org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        ped2 = Pedimento.objects.create(organizacion=org2, numero="654321")
        doc2 = Document.objects.create(organizacion=org2, pedimento=ped2, archivo="documents/test2.pdf", size=200, extension="pdf")
        self.client.force_authenticate(user=self.admin)
        url = reverse('Document-detail', args=[doc2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superuser_can_access_all(self):
        org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        ped2 = Pedimento.objects.create(organizacion=org2, numero="654321")
        doc2 = Document.objects.create(organizacion=org2, pedimento=ped2, archivo="documents/test2.pdf", size=200, extension="pdf")
        self.client.force_authenticate(user=self.superuser)
        url = reverse('Document-detail', args=[doc2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_download_requires_auth(self):
        doc = Document.objects.create(organizacion=self.org, pedimento=self.pedimento, archivo="documents/test1.pdf", size=100, extension="pdf")
        url = reverse('descargar-documento', args=[doc.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
