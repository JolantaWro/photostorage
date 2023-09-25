from django.test import TestCase
from django.contrib.auth.models import User
from photo.models import Photo


class TestPhotoModel(TestCase):

    def test_photo_creation(self):
        user = User.objects.create_user(username='BasicTest', password='Panama2023')

        photo = Photo.objects.create(
            user=user,
            active_until=None,
            height_basic=200,
            height_premium=400,
            time_active=None
        )

        self.assertFalse(photo.photo)
        self.assertFalse(photo.photo_basic)
        self.assertFalse(photo.photo_premium)

        self.assertEqual(photo.user, user)
        self.assertIsNone(photo.active_until)
        self.assertEqual(photo.height_basic, 200)
        self.assertEqual(photo.height_premium, 400)
        self.assertIsNone(photo.time_active)
