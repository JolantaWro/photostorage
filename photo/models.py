import os
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def upload_to(instance, filename):
    user_id = instance.user.id
    _, extension = os.path.splitext(filename)
    return f'user_{user_id}/{filename}'


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=None,
                              height_field=None,
                              blank=True,
                              null=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])])
    photo_basic = models.ImageField(upload_to=None,
                                    height_field='height_basic',
                                    blank=True,
                                    null=True,
                                    validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])])
    photo_premium = models.ImageField(upload_to=None,
                                      height_field='height_premium',
                                      blank=True, null=True,
                                      validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])])
    active_until = models.DateTimeField(null=True, blank=True)
    height_basic = models.IntegerField(default=200, blank=True, null=True)
    height_premium = models.IntegerField(default=400, blank=True, null=True)
    time_active = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.active_until and self.active_until < timezone.now():
            self.time_active = None
        super().save(*args, **kwargs)
