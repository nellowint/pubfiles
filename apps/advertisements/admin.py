from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Advertisements


@admin.register(Advertisements)
class AdvertisementsAdmin(admin.ModelAdmin):
    list_display = ['link_preview', 'type', 'position', 'is_active']
    list_display_links = ['link_preview']
    list_filter = ['type', 'position', 'is_active']
    search_fields = ['link']

    class Media:
        js = ('js/admin-clickable-rows.js',)

    def link_preview(self, obj):
        if obj.is_script:
            return mark_safe('<span style="color: #28a745;">Script</span>')
        return format_html('<a href="{}" target="_blank" rel="noopener">Link</a>', obj.link)
    link_preview.short_description = 'Conteúdo'
