from django.db import models
from django.utils.text import slugify

from apps.categories.models import Category


class Publication(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Title',
        help_text='Name of the magazine, comic book...'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='url',
        help_text='Automatically generated url'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Description',
        help_text='Optional field'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Category'
    )
    cover = models.ImageField(
        upload_to='covers/',
        verbose_name='Cover'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Views'
    )
    is_members_only = models.BooleanField(
        default=False,
        verbose_name='Exclusive content?',
        help_text='Exclusive content for subscribers'
    )
    free_pages_count = models.PositiveIntegerField(
        default=1,
        verbose_name='Free pages',
        help_text='How many pages can a non-paying user read before being blocked? Default: 1.'
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Published in'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Edited in'
    )

    class Meta:
        ordering = ['-views_count', '-published_at']
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            temp_slug = slugify(self.title)
            slug = temp_slug
            counter = 1

            while Publication.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{temp_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Page(models.Model):
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='pages',
        verbose_name='Publication'
    )
    image = models.ImageField(
        upload_to='pages/',
        verbose_name='Page Content'
    )
    page_order = models.PositiveIntegerField(
        verbose_name='Page Order'
    )

    class Meta:
        ordering=['page_order']
        verbose_name='Page'
        verbose_name_plural='Pages'

    def __str__(self):
        return f"{self.publication.title} - {self.page_order}"
