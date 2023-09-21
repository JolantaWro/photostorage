from django.contrib import admin
from .models import Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'height_basic', 'height_premium', 'active_until')


admin.site.register(Photo, PhotoAdmin)
