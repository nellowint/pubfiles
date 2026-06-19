
from django.db import models
from django.core.exceptions import ValidationError


class WebSettings(models.Model):
    title = models.CharField(
        max_length=100,
        default='Site',
        verbose_name='Título do site'
    )
    logo = models.ImageField(
        upload_to='website/logo',
        verbose_name='Logo do site',
        blank=True,
        null=True
    )
    background = models.ImageField(
        upload_to='website/background',
        verbose_name='Background do site',
        blank=True,
        null=True
    )
    light_theme_primary = models.CharField(
        max_length=7,
        default="#FFFFFF",
        verbose_name="Cor Principal (Tema Claro)",
        help_text="Exemplo: #FFFFFF"
    )
    light_theme_secondary = models.CharField(
        max_length=7,
        default="#F8F9FA",
        verbose_name="Cor de Fundo (Tema Claro)"
    )
    dark_theme_primary = models.CharField(
        max_length=7,
        default="#121212",
        verbose_name="Cor Principal (Tema Escuro)",
        help_text="Exemplo: #121212"
    )
    dark_theme_secondary = models.CharField(
        max_length=7,
        default="#1A1A1A",
        verbose_name="Cor de Fundo (Tema Escuro)"
    )

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configuraçoes do Site"

    def __str__(self):
        return f"Configurações do Site: {self.title}"

    def clean(self):
        if WebSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Já existe uma configuração cadastrada. Edite o registro existente.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CarouselBanner(models.Model):
    web_settings = models.ForeignKey(
        WebSettings,
        on_delete=models.CASCADE,
        related_name='banners',
        verbose_name='Configuração do Site'
    )
    image = models.ImageField(
        upload_to='website/carousel/',
        verbose_name="Imagem do Banner"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo?"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Banner Carrossel do Site"
        verbose_name_plural = "Banners Carrossel do Site"

    def __str__(self):
        return f"Banner #{self.pk} - Ordem: {self.order}"
