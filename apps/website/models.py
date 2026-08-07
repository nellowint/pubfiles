
from django.db import models
from django.core.exceptions import ValidationError

from core.utils import MediaPath, validate_file_size


class WebSettings(models.Model):
    title = models.CharField(
        max_length=100,
        default='Site',
        verbose_name='Título do site',
    )
    logo = models.ImageField(
        upload_to=MediaPath('website/logo'),
        verbose_name='Logo do site',
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    background = models.ImageField(
        upload_to=MediaPath('website/background'),
        verbose_name='Fundo do site',
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    background_mobile = models.ImageField(
        upload_to=MediaPath('website/background'),
        verbose_name='Fundo do site (mobile)',
        help_text='Fundo usado apenas em dispositivos móveis. Usa o fundo principal se vazio.',
        blank=True,
        null=True,
        validators=[validate_file_size],
    )
    light_theme_primary = models.CharField(
        max_length=7,
        default='#FFFFFF',
        verbose_name='Cor primária (tema claro)',
        help_text='Exemplo: #FFFFFF',
    )
    light_theme_secondary = models.CharField(
        max_length=7,
        default='#F8F9FA',
        verbose_name='Cor secundária (tema claro)',
        help_text='Exemplo: #F8F9FA',
    )
    dark_theme_primary = models.CharField(
        max_length=7,
        default='#121212',
        verbose_name='Cor primária (tema escuro)',
        help_text='Exemplo: #121212',
    )
    dark_theme_secondary = models.CharField(
        max_length=7,
        default='#1A1A1A',
        verbose_name='Cor secundária (tema escuro)',
        help_text='Exemplo: #1A1A1A',
    )

    privacy_policy = models.TextField(
        blank=True,
        verbose_name='Política de Privacidade',
    )
    terms = models.TextField(
        blank=True,
        verbose_name='Termos de Uso',
    )

    class Meta:
        verbose_name = 'Configuração do site'
        verbose_name_plural = 'Configurações do site'

    def __str__(self):
        return f'Site Settings: {self.title}'

    def clean(self):
        if WebSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError('A configuration already exists. Edit the existing record.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
