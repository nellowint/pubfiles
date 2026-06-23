from django import forms
from django.contrib import admin
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
class WebSettingsAdmin(admin.ModelAdmin):
    form = WebSettingsAdminForm

    def has_add_permission(self, request):
        if WebSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
