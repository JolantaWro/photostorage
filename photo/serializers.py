from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Photo


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']



class ImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = ('__all__')
        read_only_fields = ('user',)

    def create(self, validated_data):
        # Przypisz zalogowanego użytkownika jako autora zdjęcia
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)