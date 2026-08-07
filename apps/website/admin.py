from django import forms
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import WebSettings

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

@admin.register(WebSettings)
class WebSettingsAdmin(TabbedTranslationAdmin):
    form = WebSettingsAdminForm
    fieldsets = (
        ('Título', {'fields': ('title', 'logo')}),
        ('Backgrounds', {'fields': ('background', 'background_mobile')}),
        ('Tema Claro', {'fields': ('light_theme_primary', 'light_theme_secondary')}),
        ('Tema Escuro', {'fields': ('dark_theme_primary', 'dark_theme_secondary')}),
        ('Termos', {'fields': ('privacy_policy', 'terms')}),
    )

    def has_add_permission(self, request):
        if WebSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
