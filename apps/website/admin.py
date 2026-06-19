from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import WebSettings, CarouselBanner

class WebSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = WebSettings
        fields = '__all__'
        widgets = {
            'light_theme_primary': forms.TextInput(attrs={'type': 'color'}),
            'light_theme_secondary': forms.TextInput(attrs={'type': 'color'}),
            'dark_theme_primary': forms.TextInput(attrs={'type': 'color'}),
            'dark_theme_secondary': forms.TextInput(attrs={'type': 'color'}),
        }

class CarouselBannerInline(admin.TabularInline):
    model = CarouselBanner
    fields = ('image', 'banner_preview', 'order', 'is_active')
    readonly_fields = ('banner_preview',)
    ordering = ['order']
    extra = 1

    def banner_preview(self, obj):
        if obj.id and obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 45px; border-radius: 4px;" />')
        return "Sem imagem"

    banner_preview.short_description = "Visualização"


@admin.register(WebSettings)
class WebSettingsAdmin(admin.ModelAdmin):
    form = WebSettingsAdminForm

    inlines = [CarouselBannerInline]

    def has_add_permission(self, request):
        if WebSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
