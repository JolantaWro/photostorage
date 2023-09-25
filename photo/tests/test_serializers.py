from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.utils import timezone
from photo.models import Photo
from photo.serializers import ImagesSerializer, BasicUserSerializer, PremiumUserSerializer, EnterpriseUserSerializer


class TestSerializers(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.photo = Photo.objects.create(
            user=self.user,
            photo_basic='basic.jpg',
            photo_premium='premium.jpg',
            photo='original.jpg'
        )

    def test_images_serializer(self):
        request = self.factory.get('/images/')
        request.user = self.user
        serializer = ImagesSerializer(instance=self.photo, context={'request': request})

        self.assertTrue(serializer.fields['user'].read_only)
        self.assertTrue(serializer.fields['photo_basic'].read_only)
        self.assertTrue(serializer.fields['photo_premium'].read_only)
        self.assertTrue(serializer.fields['active_until'].read_only)
        self.assertTrue(serializer.fields['height_basic'].read_only)
        self.assertTrue(serializer.fields['height_premium'].read_only)
        self.assertTrue(serializer.fields['time_active'].read_only)

    def test_basic_user_serializer(self):
        serializer = BasicUserSerializer(instance=self.photo)
        self.assertIn('photo_basic', serializer.data)

    def test_premium_user_serializer(self):
        serializer = PremiumUserSerializer(instance=self.photo)

        self.assertIn('photo_basic', serializer.data)
        self.assertIn('photo_premium', serializer.data)
        self.assertIn('photo', serializer.data)

    def test_enterprise_user_serializer(self):
        request = self.factory.get('/images/')
        request.user = self.user
        serializer = EnterpriseUserSerializer(instance=self.photo, context={'request': request})

        self.assertIn('photo_basic', serializer.data)
        self.assertIn('photo_premium', serializer.data)
        self.assertIn('photo', serializer.data)
        self.assertIn('expiring_link', serializer.data)
        self.assertIn('time_active', serializer.data)
        self.assertIn('id', serializer.data)

    def test_expiring_link_in_enterprise_user_serializer(self):
        request = self.factory.get('/images/')
        request.user = self.user

        self.photo.active_until = timezone.now() + timezone.timedelta(days=1)
        self.photo.save()

        serializer = EnterpriseUserSerializer(instance=self.photo, context={'request': request})

        self.assertIn('expiring_link', serializer.data)
        self.assertEqual(serializer.data['expiring_link'], request.build_absolute_uri(self.photo.photo.url))
