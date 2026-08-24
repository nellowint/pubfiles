from django.contrib import admin
from .models import Advertisements


@admin.register(Advertisements)
class AdvertisementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'position', 'is_active']
    list_filter = ['type', 'position', 'is_active']
    search_fields = ['title', 'link']
    readonly_fields = ['ratings_count']

    class Media:
        js = ('js/admin-clickable-rows.js',)
