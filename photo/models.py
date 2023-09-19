from django.db import models
from django.conf import settings
from datetime import date

from django.contrib.auth.models import User



class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo_field = models.ImageField(upload_to=None, height_field=None)
    date_added = models.DateTimeField(auto_now_add=True)
