from django.db import models


class AdvertisementsType(models.TextChoices):
    POPUNDER = 'pop_under', 'Popunder: Anúncio em tela cheia aberto em outra aba'
    SOCIALBAR = 'social_bar', 'SocialBar: Anúncio interativo e personalizável'
    SMARTLINK = 'smart_link', 'Smartlink: Direciona o usuário à melhor oferta'
    NATIVEBANNER = 'native_banner', 'Nativo: Anúncio integrado ao conteúdo do site'


class AdvertisementsPositions(models.TextChoices):
    BANNER = 'banner', 'Carrossel de banners'
    CARD = 'card', 'Card de publicações'
    LEFT = 'left', 'Lateral esquerda'
    RIGHT = 'right', 'Lateral direita'
    PREVIEW = 'preview', 'Reader preview'
    FOOTER = 'footer', 'Acima do footer'


class Advertisements(models.Model):
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Título',
        help_text='Título exibido no card de anúncio'
    )
    link = models.TextField(
        verbose_name='Link/Script',
        help_text='Cole o script HTML completo ou uma URL. Se começar com "<script", será renderizado como script; caso contrário, será tratado como link.'
    )
    type = models.CharField(
        max_length=20,
        choices=AdvertisementsType.choices,
        verbose_name='Tipo de anúncio'
    )
    position = models.CharField(
        max_length=20,
        choices=AdvertisementsPositions.choices,
        verbose_name='Posição'
    )
    ratings_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Cliques',
        help_text='Quantidade de cliques no anúncio'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Anúncio'
        verbose_name_plural = 'Anúncios'

    def __str__(self):
        return f'{self.get_position_display()} - {self.get_type_display()}'

    @property
    def is_script(self):
        return self.link.strip().startswith('<script')
