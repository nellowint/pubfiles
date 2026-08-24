from django.contrib import admin
from .models import Advertisements


@admin.register(Advertisements)
class AdvertisementsAdmin(admin.ModelAdmin):
    list_display = ['type', 'position', 'is_active']
    list_filter = ['type', 'position', 'is_active']

    class Media:
        js = ('js/admin-clickable-rows.js',)
