from django.contrib import admin
from .models import Advertisements


@admin.register(Advertisements)
class AdvertisementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'position', 'ratings_count', 'is_active']
    list_filter = ['type', 'position', 'is_active']
    search_fields = ['title', 'link']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('link', 'type', 'position', 'is_active')
        }),
        ('Card (opcional)', {
            'fields': ('title',),
            'description': 'Estes campos são usados apenas quando o anúncio é exibido como card na home.'
        }),
    )

    class Media:
        js = ('js/admin-clickable-rows.js',)
