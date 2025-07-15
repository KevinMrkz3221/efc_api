
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.organization.models import Organizacion
from .models import CustomUser

User = get_user_model()

class CustomUserViewSetTests(APITestCase):
    def setUp(self):
        self.org = Organizacion.objects.create(nombre="OrgTest", is_active=True, is_verified=True)
        self.org2 = Organizacion.objects.create(nombre="OrgTest2", is_active=True, is_verified=True)
        self.admin = User.objects.create_user(username="admin", password="adminpass", organizacion=self.org)
        self.admin.groups.create(name="admin")
        self.superuser = User.objects.create_superuser(username="superuser", password="superpass")
        self.importador = User.objects.create_user(username="importador", password="importpass", organizacion=self.org2, is_importador=True, rfc="RFC123456789")
        self.importador.groups.create(name="importador")
        self.user = User.objects.create_user(username="user1", password="userpass", organizacion=self.org)
        self.client = APIClient()
    def test_admin_sees_only_own_org_users(self):
        user2 = User.objects.create_user(username="user2", password="userpass2", organizacion=self.org2)
        self.client.force_authenticate(user=self.admin)
        url = reverse('customuser-list')
        response = self.client.get(url)
        usernames = [u['username'] for u in response.data]
        self.assertIn("admin", usernames)
        self.assertIn("user1", usernames)
        self.assertNotIn("user2", usernames)

    def test_superuser_sees_all_users(self):
        user2 = User.objects.create_user(username="user2", password="userpass2", organizacion=self.org2)
        self.client.force_authenticate(user=self.superuser)
        url = reverse('customuser-list')
        response = self.client.get(url)
        usernames = [u['username'] for u in response.data]
        self.assertIn("admin", usernames)
        self.assertIn("user1", usernames)
        self.assertIn("user2", usernames)

    def test_importador_cannot_create_user(self):
        self.client.force_authenticate(user=self.importador)
        url = reverse('customuser-list')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpass123"
        }
        response = self.client.post(url, data)
        self.assertNotIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_list_users(self):
        url = reverse('customuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_me_endpoint(self):
        url = reverse('customuser-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.admin.username)

    def test_create_user_as_admin(self):
        url = reverse('customuser-list')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], "newuser")

    def test_update_user_as_admin(self):
        url = reverse('customuser-detail', args=[str(self.user.id)])
        data = {"first_name": "Updated"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Updated")

    def test_profile_picture_view(self):
        # No profile picture, should return 404
        url = reverse('profile-picture', args=[str(self.user.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
