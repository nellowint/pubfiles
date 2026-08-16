
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Nome',
        help_text='Nome da categoria',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='URL',
        help_text='URL gerada automaticamente a partir do nome',
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Categoria pai',
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        ordering = ['name']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        indexes = [
            models.Index(fields=['slug'], name='category_slug_idx'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            temp_slug = slugify(self.name)
            slug = temp_slug
            counter = 1

            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{temp_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
