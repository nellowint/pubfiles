import re

from django import forms
from django.contrib import admin
from django.core.validators import validate_image_file_extension
from modeltranslation.admin import TabbedTranslationAdmin

from core.utils import validate_file_size

from .models import WebSettings, Banner


def _natural_sort_key(file):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', file.name)]


class BannerInline(admin.TabularInline):
    model = Banner
    extra = 0
    fields = ('order', 'title', 'subtitle', 'image', 'advertisement', 'is_active')


class WebSettingsAdminForm(forms.ModelForm):
    batch_upload = forms.FileField(
        label="Upload em lote de banners",
        help_text="Selecione todas as imagens dos banners de uma vez.",
        required=False,
        validators=[validate_file_size],
    )

    class Meta:
        model = WebSettings
        fields = '__all__'
        widgets = {
            'light_theme_primary': forms.TextInput(attrs={'type': 'color'}),
            'light_theme_secondary': forms.TextInput(attrs={'type': 'color'}),
            'dark_theme_primary': forms.TextInput(attrs={'type': 'color'}),
            'dark_theme_secondary': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch_upload'].widget.attrs.update({'multiple': True})

    def clean_batch_upload(self):
        for upload in self.files.getlist('batch_upload'):
            validate_image_file_extension(upload)
            validate_file_size(upload)
        return self.cleaned_data.get('batch_upload')

@admin.register(WebSettings)
class WebSettingsAdmin(TabbedTranslationAdmin):
    form = WebSettingsAdminForm
    fieldsets = (
        ('Título', {'fields': ('title', 'subtitle', 'description', 'logo')}),
        ('Backgrounds', {'fields': ('background', 'background_mobile')}),
        ('Tema Claro', {'fields': ('light_theme_primary', 'light_theme_secondary')}),
        ('Tema Escuro', {'fields': ('dark_theme_primary', 'dark_theme_secondary')}),
        ('Termos', {'fields': ('privacy_policy', 'terms')}),
        ('Avisos', {'fields': ('start_message',)}),
        ('Banners', {'fields': ('batch_upload',), 'description': 'Upload em lote de imagens para o carrossel de banners.'}),
    )
    inlines = [BannerInline]

    def has_add_permission(self, request):
        if WebSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        # Processa batch_upload do form principal
        batch_files = form.files.getlist('batch_upload')
        if batch_files:
            batch_files.sort(key=_natural_sort_key)
            current_count = Banner.objects.filter(website=form.instance).count()

            for index, file in enumerate(batch_files, start=1):
                Banner.objects.create(
                    website=form.instance,
                    image=file,
                    order=current_count + index,
                    is_active=True
                )
