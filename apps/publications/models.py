from django.db import models
from django.utils.text import slugify

from apps.categories.models import Category


class Publication(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Título',
        help_text='Nome da revista, HQ, etc...'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='url',
        help_text='Url gerada automaticamente'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Descrição',
        help_text='Campo opcional'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Categoria'
    )
    cover = models.ImageField(
        upload_to='covers/',
        verbose_name='Capa'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Visualizações'
    )
    is_members_only = models.BooleanField(
        default=False,
        verbose_name='Conteúdo exclusivo?',
        help_text='Conteúdo exclusivo para assinantes'
    )
    free_pages_count = models.PositiveIntegerField(
        default=1,
        verbose_name='Páginas gratuitas',
        help_text='Quantas páginas um usuário não pagante pode ler antes de ser bloqueado. Padrão: 1.'
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publicado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Editado em'
    )

    class Meta:
        ordering = ['-views_count', '-published_at']
        verbose_name = 'Publicação'
        verbose_name_plural = 'Publicações'

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
        verbose_name='Publicação'
    )
    image = models.ImageField(
        upload_to='pages/',
        verbose_name='Conteúdo das Páginas'
    )
    page_order = models.PositiveIntegerField(
        verbose_name='Ordem da Página'
    )

    class Meta:
        ordering=['page_order']
        verbose_name='Página'
        verbose_name_plural='Páginas'

    def __str__(self):
        return f"{self.publication.title} - {self.page_order}"
