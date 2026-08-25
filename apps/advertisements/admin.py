from django.contrib import admin
from .models import Advertisements


@admin.register(Advertisements)
class AdvertisementsAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'position', 'is_active']
    list_filter = ['type', 'position', 'is_active']
    search_fields = ['title', 'link']
    readonly_fields = ['ratings_count']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # socialbar não depende de posição — torna opcional no form
        if 'position' in form.base_fields:
            form.base_fields['position'].required = False
        return form

    class Media:
        js = ('js/admin-clickable-rows.js', 'js/advertisements-admin.js')
