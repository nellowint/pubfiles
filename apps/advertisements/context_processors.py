from .models import Advertisements


def ads_context(request):
    return {
        'ads_cards': list(Advertisements.objects.filter(position='card', is_active=True)),
        'ads_preview': list(Advertisements.objects.filter(position='preview', is_active=True)),
        'ads_mobile': list(Advertisements.objects.filter(position='mobile', is_active=True)),
        'ads_left': Advertisements.objects.filter(position='left', is_active=True),
        'ads_right': Advertisements.objects.filter(position='right', is_active=True),
        'ads_footer': Advertisements.objects.filter(position='footer', is_active=True).first(),
        'ads_footer_mobile': Advertisements.objects.filter(position='footer_mobile', is_active=True).first(),
    }
