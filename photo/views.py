from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import permissions, serializers, viewsets, status
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from photo.serializers import ImagesSerializer, BasicUserSerializer, PremiumUserSerializer, EnterpriseUserSerializer
from .models import Photo
from PIL import Image


def validate_format_file(file):
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise serializers.ValidationError("Invalid image format")


def resize_file(source_file, height, output_format=None):
    img = Image.open(source_file)

    if height:
        aspect_ratio = float(height) / img.size[1]
        width = int(float(img.size[0]) * aspect_ratio)
        img = img.resize((width, height), Image.LANCZOS)

    output_buffer = BytesIO()

    if output_format:
        img.save(output_buffer, format=output_format)
    else:
        img.save(output_buffer, format=img.format)

    return SimpleUploadedFile(source_file.name, output_buffer.getvalue())


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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        img_post_original = self.request.data.get('photo')
        img_post_basic = self.request.data.get('photo_basic')
        time_active_link = self.request.data.get('time_active')

        height_basic_expected = 200
        height_premium_expected = 400

        if user.groups.filter(name='Basic').exists():
            validate_format_file(img_post_basic)
            add_photo = resize_file(img_post_basic, height_basic_expected, output_format='png')
            new_photo = Photo.objects.create(photo_basic=add_photo, photo=img_post_basic, user=user)

        elif user.groups.filter(name='Premium').exists():
            validate_format_file(img_post_original)
            add_photo_basic = resize_file(img_post_original, height_basic_expected, output_format='png')
            add_photo_premium = resize_file(img_post_original, height_premium_expected, output_format='png')
            new_photo = Photo.objects.create(photo_basic=add_photo_basic, photo_premium=add_photo_premium,
                                             photo=img_post_original, user=user)

        elif user.groups.filter(name='Enterprise').exists():
            validate_format_file(img_post_original)
            add_photo_basic = resize_file(img_post_original, height_basic_expected, output_format='png')
            add_photo_premium = resize_file(img_post_original, height_premium_expected, output_format='png')

            if time_active_link is not None and time_active_link != "":
                try:
                    time_expiring_link = int(time_active_link)
                    if time_expiring_link < 300 or time_expiring_link > 30000:
                        return Response({'error': 'Expiration time should be between 300 and 30000 seconds'},
                                        status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    return Response({'error': 'Invalid expiration time format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                time_expiring_link = None

            new_photo = Photo.objects.create(photo_basic=add_photo_basic, photo_premium=add_photo_premium,
                                             photo=img_post_original, user=user,
                                             time_active=time_expiring_link)

            if time_expiring_link is not None and time_expiring_link > 0:
                expiration_time_user = timezone.now() + timedelta(seconds=time_expiring_link)
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

            if time_expiring_link is not None and time_expiring_link > 0:
                expiration_time = timezone.now() + timedelta(seconds=time_expiring_link)
                serializer_data['expiring_link'] = request.build_absolute_uri(new_photo.photo.url)
                new_photo.active_until = expiration_time
                new_photo.save()
            return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)

        else:
            return Response({'error': 'User does not belong to any Group'}, status=status.HTTP_400_BAD_REQUEST)

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
