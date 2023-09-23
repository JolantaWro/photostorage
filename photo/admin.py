from django.contrib import admin
from .models import Photo


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', 'active_until', 'height_basic', 'height_premium')
    list_editable = ('height_basic', 'height_premium', 'active_until')


admin.site.register(Photo, PhotoAdmin)
