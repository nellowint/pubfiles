import re

from django import forms
from django.contrib import admin
from django.core.validators import validate_image_file_extension
from django.template.loader import get_template
from modeltranslation.admin import TabbedTranslationAdmin

from core.utils import validate_file_size

from .models import WebSettings, Banner


def _natural_sort_key(file):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', file.name)]


class BannerInline(admin.StackedInline):
    model = Banner
    extra = 0
    fields = ('order', 'banner_thumbnail', 'title', 'subtitle', 'image', 'advertisement', 'is_active')
    readonly_fields = ('banner_thumbnail',)

    def banner_thumbnail(self, instance):
        if instance.image:
            tpl = get_template("admin/thumbnail.html")
            return tpl.render({"page": instance})
        return '-'
    banner_thumbnail.short_description = "Preview"


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

    def save_banners(self, web_settings):
        uploaded_files = self.files.getlist('batch_upload')
        if uploaded_files:
            uploaded_files.sort(key=_natural_sort_key)
            current_count = Banner.objects.filter(website=web_settings).count()

            for index, file in enumerate(uploaded_files, start=1):
                Banner.objects.create(
                    website=web_settings,
                    image=file,
                    order=current_count + index,
                    is_active=True
                )

@admin.register(WebSettings)
class WebSettingsAdmin(TabbedTranslationAdmin):
    form = WebSettingsAdminForm
    list_display = ['title', 'subtitle']
    list_filter = ['title']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['title']
    fieldsets = (
        ('Título', {'fields': ('title', 'subtitle', 'description', 'logo', 'batch_upload')}),
        ('Backgrounds', {'fields': ('background', 'background_mobile')}),
        ('Tema Claro', {'fields': ('light_theme_primary', 'light_theme_secondary')}),
        ('Tema Escuro', {'fields': ('dark_theme_primary', 'dark_theme_secondary')}),
        ('Termos', {'fields': ('privacy_policy', 'terms')}),
        ('Avisos', {'fields': ('start_message',)}),
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
        form.save_banners(form.instance)

    class Media:
        js = ('js/admin-clickable-rows.js',)
