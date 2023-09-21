from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response


from photo.serializers import ImagesSerializer
from .models import Photo
from PIL import Image


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or added.
    """
    queryset = Photo.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [permissions.IsAuthenticated]

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
        image_post = self.request.data.get('photo')
        image_user = user.photo_set.first()
        if image_user:
            height_basic_expected = user.photo_set.first().height_basic
            height_premium_expected = user.photo_set.first().height_premium

            if user.groups.filter(name='Basic').exists():
                add_photo = self.resize_image(image_post, height_basic_expected)
                new_photo = Photo.objects.create(photo_basic=add_photo, user=user)
                serializer = ImagesSerializer(new_photo, many=False)
                return Response(serializer.data)

            elif user.groups.filter(name='Premium').exists():
                add_photo_basic = self.resize_image(image_post, height_basic_expected)
                add_photo_premium = self.resize_image(image_post, height_premium_expected)
                new_photo = Photo.objects.create(photo_basic=add_photo_basic,
                                                 photo_premium=add_photo_premium,
                                                 photo=image_post,
                                                 user=user)
                serializer = ImagesSerializer(new_photo, many=False)
                return Response(serializer.data)
            elif user.groups.filter(name='Enterprise').exists():
                add_photo_basic = self.resize_image(image_post, height_basic_expected)
                add_photo_premium = self.resize_image(image_post, height_premium_expected)
                new_photo = Photo.objects.create(photo_basic=add_photo_basic,
                                                 photo_premium=add_photo_premium,
                                                 photo=image_post,
                                                 user=user)
                serializer = ImagesSerializer(new_photo, many=False)
                return Response(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

