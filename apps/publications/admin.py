import re

from django import forms
from django.contrib import admin
from django.core.validators import validate_image_file_extension
from django.template.loader import get_template
from modeltranslation.admin import TabbedTranslationAdmin

from core.utils import validate_file_size

from .models import Comment, Page, Publication, Rating


def _natural_sort_key(file):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', file.name)]


class PublicationAdminForm(forms.ModelForm):
    batch_upload = forms.FileField(
        label="Upload em lote",
        help_text="Selecione todas as imagens da publicação de uma vez.",
        required=False,
        validators=[validate_file_size],
    )

    class Meta:
        model = Publication
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch_upload'].widget.attrs.update({'multiple': True})

    def clean_batch_upload(self):
        for upload in self.files.getlist('batch_upload'):
            validate_image_file_extension(upload)
            validate_file_size(upload)
        return self.cleaned_data.get('batch_upload')

    def save_pages(self, publication):
        uploaded_files = self.files.getlist('batch_upload')
        if uploaded_files:
            uploaded_files.sort(key=_natural_sort_key)
            current_page_count = Page.objects.filter(publication=publication).count()

            for index, file in enumerate(uploaded_files, start=1):
                Page.objects.create(
                    publication=publication,
                    image=file,
                    page_order=current_page_count + index
                )

class PageInline(admin.TabularInline):
    model = Page
    fields = ('page_order', 'page_thumbnail')
    readonly_fields = ('page_thumbnail',)
    ordering = ['page_order']
    max_num = 0
    can_delete = True

    def page_thumbnail(self, instance):
        tpl = get_template("admin/thumbnail.html")
        return tpl.render({"page": instance})

    page_thumbnail.short_description = "Miniatura"

@admin.register(Publication)
class PublicationAdmin(TabbedTranslationAdmin):
    form = PublicationAdminForm
    autocomplete_fields = ['category']
    list_display = ['title', 'display_categories', 'is_members_only', 'free_pages_count', 'views_count', 'published_at']
    list_filter = ['is_members_only', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title_pt_br',)}
    readonly_fields = ['views_count', 'published_at', 'updated_at']

    inlines = [PageInline]

    @admin.display(description='Categorias')
    def display_categories(self, obj):
        return ', '.join(c.name for c in obj.ordered_categories)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.save_pages(form.instance)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'publication', 'created_at', 'updated_at']
    list_filter = ['publication']
    search_fields = ['content', 'user__email', 'publication__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'publication', 'score', 'updated_at']
    list_filter = ['score', 'publication']
    search_fields = ['user__email', 'publication__title']
    readonly_fields = ['created_at', 'updated_at']
