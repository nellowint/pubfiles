from .models import Subscription, SubscriptionSettings


def subscription_settings(request):
    user_subscription = None
    if getattr(request, 'user', None) and request.user.is_authenticated:
        user_subscription = Subscription.objects.active_for(request.user).first()
    return {
        'subscription_settings': SubscriptionSettings.objects.first(),
        'user_subscription': user_subscription,
    }
