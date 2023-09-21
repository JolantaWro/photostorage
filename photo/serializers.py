from rest_framework import serializers
from .models import Photo


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('__all__')
        read_only_fields = ('user', 'photo_basic', 'photo_premium', 'photo_active', 'date_added', 'active_until',
                            'height_basic', 'height_premium', 'time_active')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
