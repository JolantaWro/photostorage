from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from photo.serializers import ImagesSerializer, BasicUserSerializer, PremiumUserSerializer, EnterpriseUserSerializer
from .models import Photo
from PIL import Image


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or added.
    """
    queryset = Photo.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.groups.filter(name='Basic').exists():
            return BasicUserSerializer
        elif user.groups.filter(name='Premium').exists():
            return PremiumUserSerializer
        elif user.groups.filter(name='Enterprise').exists():
            return EnterpriseUserSerializer
        else:
            return ImagesSerializer

    def resize_image(self, source_image, height):
        img = Image.open(source_image)

        if height:
            aspect_ratio = float(height) / img.size[1]
            width = int(float(img.size[0]) * aspect_ratio)
            img = img.resize((width, height), Image.LANCZOS)

        output_buffer = BytesIO()
        img.save(output_buffer, format='JPEG')
        return SimpleUploadedFile(source_image.name, output_buffer.getvalue())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        image_post_original = self.request.data.get('photo')
        image_post_basic = self.request.data.get('photo_basic')
        image_time = self.request.data.get('time_active')

        image_user = user.photo_set.first()
        new_photo = None

        if user.groups.filter(name='Basic').exists():
            if image_user and hasattr(image_user, 'height_basic'):
                height_basic_expected = image_user.height_basic
            else:
                height_basic_expected = 200

            add_photo = self.resize_image(image_post_basic, height_basic_expected)
            new_photo = Photo.objects.create(photo_basic=add_photo, photo=image_post_basic, user=user)

        elif user.groups.filter(name='Premium').exists():
            if image_user and hasattr(image_user, 'height_basic'):
                height_basic_expected = image_user.height_basic
            else:
                height_basic_expected = 200

            if image_user and hasattr(image_user, 'height_premium'):
                height_premium_expected = image_user.height_premium
            else:
                height_premium_expected = 400

            add_photo_basic = self.resize_image(image_post_original, height_basic_expected)
            add_photo_premium = self.resize_image(image_post_original, height_premium_expected)
            new_photo = Photo.objects.create(photo_basic=add_photo_basic, photo_premium=add_photo_premium,
                                             photo=image_post_original, user=user)

        elif user.groups.filter(name='Enterprise').exists():
            if image_user and hasattr(image_user, 'height_basic'):
                height_basic_expected = image_user.height_basic
            else:
                height_basic_expected = 200

            if image_user and hasattr(image_user, 'height_premium'):
                height_premium_expected = image_user.height_premium
            else:
                height_premium_expected = 400

            if image_time is not None and image_time != "":
                try:
                    image_activ_link = int(image_time)
                    if image_activ_link < 300 or image_activ_link > 30000:
                        return Response({'error': 'Expiration time should be between 300 and 30000 seconds'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    image_activ = image_post_original
                except ValueError:
                    return Response({'error': 'Invalid expiration time format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                image_activ_link = None
                image_activ = None

            add_photo_basic = self.resize_image(image_post_original, height_basic_expected)
            add_photo_premium = self.resize_image(image_post_original, height_premium_expected)
            new_photo = Photo.objects.create(photo_basic=add_photo_basic, photo_premium=add_photo_premium,
                                             photo=image_post_original, user=user,
                                             time_active=image_activ_link)

            if image_activ_link is not None and image_activ_link > 0:
                expiration_time_user = timezone.now() + timedelta(seconds=image_activ_link)
                n_expiration_time_user = expiration_time_user.astimezone(timezone.utc)
                new_photo.active_until = n_expiration_time_user
            else:
                new_photo.active_until = None
            new_photo.save()

            serializer = self.get_serializer_class()(new_photo, many=False, context={'request': request})
            headers = self.get_success_headers(serializer.data)

            photo_basic_url = request.build_absolute_uri(new_photo.photo_basic.url)
            photo_premium_url = request.build_absolute_uri(new_photo.photo_premium.url)
            photo_url = request.build_absolute_uri(new_photo.photo.url)

            serializer_data = serializer.data
            serializer_data['photo_basic'] = photo_basic_url
            serializer_data['photo'] = photo_url
            serializer_data['photo_premium'] = photo_premium_url

            if image_activ_link is not None and image_activ_link > 0:
                expiration_time = timezone.now() + timedelta(seconds=image_activ_link)
                serializer_data['expiring_link'] = request.build_absolute_uri(new_photo.photo.url)
                new_photo.active_until = expiration_time
                new_photo.save()
            return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)

        else:
            return Response({'error': 'User does not belong to any group'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer_class()(new_photo, many=False)
        headers = self.get_success_headers(serializer.data)

        photo_basic_url = request.build_absolute_uri(new_photo.photo_basic.url)
        serializer_data = serializer.data
        serializer_data['photo_basic'] = photo_basic_url

        if user.groups.filter(name='Premium').exists() or user.groups.filter(name='Enterprise').exists():
            photo_premium_url = request.build_absolute_uri(new_photo.photo_premium.url)
            photo_url = request.build_absolute_uri(new_photo.photo.url)
            serializer_data['photo'] = photo_url
            serializer_data['photo_premium'] = photo_premium_url

        return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)
