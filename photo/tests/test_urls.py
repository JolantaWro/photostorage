from django.test import SimpleTestCase
from django.urls import reverse, resolve
from photo.views import ImageViewSet


class TestUrls(SimpleTestCase):

    def test_admin_url_resolves(self):
        url = reverse('admin:index')
        self.assertEqual(resolve(url).url_name, 'index')

    def test_images_list_url_resolves(self):
        url = reverse('images-list')
        self.assertEqual(resolve(url).func.cls, ImageViewSet)

    def test_api_auth_url_resolves(self):
        url = reverse('rest_framework:login')
        self.assertEqual(resolve(url).url_name, 'login')
