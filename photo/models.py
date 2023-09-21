import os

from django.db import models
from django.contrib.auth.models import User


def upload_to(instance, filename):
    user_id = instance.user.id
    _, extension = os.path.splitext(filename)
    return f'user_{user_id}/{filename}'


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=None, height_field=None, blank=True, null=True)
    photo_basic = models.ImageField(upload_to=None, height_field='height_basic', blank=True, null=True)
    photo_premium = models.ImageField(upload_to=None, height_field='height_premium', blank=True, null=True)
    photo_active = models.ImageField(upload_to=None, height_field=None, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    active_until = models.DateTimeField(null=True, blank=True)
    height_basic = models.IntegerField(default=200)
    height_premium = models.IntegerField(default=400)
    time_active = models.IntegerField(default=0)
