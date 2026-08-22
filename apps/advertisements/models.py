from django.db import models


class AdvertisementsType(models.TextChoices):
    POPUNDER = 'pop_under', 'Popunder é um anúncio em tela cheia que abre em uma aba separada, com cobrança por CPM/CPA e frequência/cliques ajustáveis.'
    SOCIALBAR = 'social_bar', 'Social Bar é um anúncio interativo e personalizável, ideal para sites com boa UX, usuários iOS e contorno de bloqueadores de anúncios.   '
    SMARTLINK = 'smart_link', 'Smartlink direciona cada usuário para a melhor oferta automaticamente, com base em seus dados, sendo ideal para redes sociais e sites com pouco espaço para anúncios.'
    NATIVEBANNER = 'native_banner', 'Banner nativo é um anúncio que se integra ao conteúdo do site, sendo responsivo e ideal para sites e blogs com conteúdo destacado.'


class AdvertisementsPositions(models.TextChoices):
    BANNER = 'banner', 'Carrossel de banners'
    CARD = 'card', 'Card de publicações'
    LEFT = 'left', 'Lateral esquerda'
    RIGHT = 'right', 'Lateral direita'
    PREVIEW = 'preview', 'Reader preview'


class Advertisements(models.Model):
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
