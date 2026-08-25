from apps.subscriptions.utils import has_premium_access

from .models import Advertisements, AdvertisementsType


def ads_context(request):
    # assinantes premium, Administrador e superuser não veem anúncios
    if has_premium_access(request.user):
        return {
            'ads_cards': [],
            'ads_preview': [],
            'ads_mobile': [],
            'ads_left': Advertisements.objects.none(),
            'ads_right': Advertisements.objects.none(),
            'ads_footer': None,
            'ads_footer_mobile': None,
            'ads_socialbar': [],
        }
    return {
        'ads_cards': list(Advertisements.objects.filter(position='card', is_active=True)),
        'ads_preview': list(Advertisements.objects.filter(position='preview', is_active=True)),
        'ads_mobile': list(Advertisements.objects.filter(position='mobile', is_active=True)),
        'ads_left': Advertisements.objects.filter(position='left', is_active=True),
        'ads_right': Advertisements.objects.filter(position='right', is_active=True),
        'ads_footer': Advertisements.objects.filter(position='footer', is_active=True).first(),
        'ads_footer_mobile': Advertisements.objects.filter(position='footer_mobile', is_active=True).first(),
        'ads_socialbar': list(Advertisements.objects.filter(type=AdvertisementsType.SOCIALBAR, is_active=True)),
    }
