from rest_framework import serializers
from .models import Photo
from django.utils import timezone


class ImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = '__all__'
        read_only_fields = ('user', 'photo_basic', 'photo_premium', 'photo_active', 'date_added', 'active_until',
                            'height_basic', 'height_premium', 'time_active', 'photo_active')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('photo_basic',)


class PremiumUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('photo_basic', 'photo_premium', 'photo')
        read_only_fields = ('photo_basic', 'photo_premium')


class EnterpriseUserSerializer(serializers.ModelSerializer):
    expiring_link = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ('photo_basic', 'photo_premium', 'photo', 'expiring_link', 'time_active')
        read_only_fields = ('photo_basic', 'photo_premium', 'expiring_link', 'id')

    def get_expiring_link(self, obj):
        expiration_time = obj.active_until
        if expiration_time:
            now = timezone.now()
            if now <= expiration_time:
                return self.context['request'].build_absolute_uri(obj.photo.url)
        return None
