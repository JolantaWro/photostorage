from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth.models import User, Group
from rest_framework import status


class TestGroupBasicPermissions(APITestCase):
    def setUp(self):
        group_name = "Basic"
        self.group = Group.objects.create(name=group_name)
        self.group.save()
        self.user = User.objects.create_user(username="BasicTest", email="test@test.com", password="Panama2023")
        self.user.save()
        self.user.groups.add(self.group)
        self.user.save()

        self.url = reverse('images-list')
        self.client = APIClient()

    def tearDown(self):
        self.user.delete()
        self.group.delete()

    def test_logged_user(self):
        self.client.login(username="BasicTest", password="Panama2023")

        session_data = self.client.session
        logged_in_user_id = session_data.get('_auth_user_id')

        self.assertIsNotNone(logged_in_user_id)

    def test_user_cannot_access_list_images(self):
        response = self.client.get(reverse('images-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_access_list_images(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('images-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_should_not_create_photo_(self):
        self.client.login(username="BasicTest", password="Panama2023")

        photo_data = {
            "user": self.user,
            "photo_basic": "kitten-4611189_640_BCN5ojr.jpg",
            "photo": "kitten-4611189_640_BCN5ojr.jpg"
        }
        response = self.client.post(self.url, photo_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_not_create_photo_with_no_auth(self):
        self.url = reverse('images-list')
        photo = {"photo_basic": "http://127.0.0.1:8000/media/None/kitten-4611189_640_BCN5ojr.jpg"}

        response = self.client.post(reverse('images-list'), photo)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
