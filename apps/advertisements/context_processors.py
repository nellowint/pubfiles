from .models import Advertisements


def ads_context(request):
    return {
        'ads_card': Advertisements.objects.filter(position='card', is_active=True).first(),
        'ads_preview': list(Advertisements.objects.filter(position='preview', is_active=True)),
        'ads_left': Advertisements.objects.filter(position='left', is_active=True),
        'ads_right': Advertisements.objects.filter(position='right', is_active=True),
    }
