
from django.db import models
from django.core.exceptions import ValidationError

from core.utils import MediaPath, validate_file_size


class WebSettings(models.Model):
    title = models.CharField(
        max_length=100,
        default='Site',
        verbose_name='Título do site',
    )
    subtitle = models.CharField(
        max_length=160,
        blank=True,
        null=True,
        verbose_name='Subtítulo',
        help_text='Exibido após o título nas meta tags de SEO (Limite de 160 caracteres)',
    )
    description = models.TextField(
        max_length=160,
        blank=True,
        null=True,
        verbose_name='Descrição',
        help_text='Usada como meta description de SEO (Limite de 160 caracteres)',
    )
    seo_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Palavras-chave SEO',
        help_text='Separadas por vírgula. Ex: revista, ebook, quadrinhos',
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
    start_message = models.TextField(
        blank=True,
        verbose_name='Mensagem de aviso',
        help_text='Exibida em um modal na página inicial. Deixe vazio para desativar.',
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


class Banner(models.Model):
    website = models.ForeignKey(
        WebSettings,
        on_delete=models.CASCADE,
        related_name='banners',
        verbose_name='Website',
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Título',
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Subtítulo',
    )
    image = models.ImageField(
        upload_to=MediaPath('website/banners'),
        validators=[validate_file_size],
        blank=True,
        null=True,
        verbose_name='Imagem (Desktop)',
        help_text='Obrigatório se não houver anúncio vinculado. Recomendado 1248×250 (5:1).',
    )
    image_mobile = models.ImageField(
        upload_to=MediaPath('website/banners/mobile'),
        validators=[validate_file_size],
        blank=True,
        null=True,
        verbose_name='Imagem (Mobile)',
        help_text='Opcional — 640×360 recomendado, usado em ≤768px. Se vazio, usa a imagem desktop.',
    )
    advertisement = models.ForeignKey(
        'advertisements.Advertisements',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='banners',
        verbose_name='Anúncio',
        help_text='Torna a imagem do banner clicável, redirecionando para o link. Apenas SmartLink.',
        limit_choices_to={'type': 'smart_link', 'is_active': True},
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Ordem',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo',
    )

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['order']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.advertisement and self.advertisement.type != 'smart_link':
            raise ValidationError({'advertisement': 'Banner só aceita anúncios do tipo SmartLink.'})

    def __str__(self):
        return self.title or f'Banner {self.pk}'
