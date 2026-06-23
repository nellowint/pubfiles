from .models import SubscriptionSettings


def subscription_settings(request):
    return {
        'subscription_settings': SubscriptionSettings.objects.first(),
    }
