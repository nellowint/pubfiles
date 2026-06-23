from django import forms
from django.contrib import admin
from django.core.validators import validate_image_file_extension
from django.template.loader import get_template
from .models import Publication, Page

class PublicationAdminForm(forms.ModelForm):
    batch_upload = forms.FileField(
        label="Batch page upload",
        help_text="Select all images from the post at once.",
        required=False
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
        return self.cleaned_data.get('batch_upload')

    def save_pages(self, publication):
        uploaded_files = self.files.getlist('batch_upload')
        if uploaded_files:
            uploaded_files.sort(key=lambda x: x.name)
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

    page_thumbnail.short_description = "Thumbnail"

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    form = PublicationAdminForm
    list_display = ['title', 'category', 'is_members_only', 'free_pages_count', 'views_count', 'published_at']
    list_filter = ['is_members_only', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'published_at', 'updated_at']

    inlines = [PageInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.save_pages(form.instance)
