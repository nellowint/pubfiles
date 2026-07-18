from datetime import datetime
from datetime import timezone as dt_timezone

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import User

from .models import Subscription, SubscriptionSettings, SubscriptionStatus

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout(request):
    sub_settings = SubscriptionSettings.objects.first()
    if not sub_settings or not sub_settings.is_enabled:
        return render(request, 'subscriptions/unavailable.html', status=503)

    if Subscription.objects.is_active_for(request.user):
        return redirect('publications:home')

    existing = (
        Subscription.objects
        .filter(user=request.user)
        .exclude(stripe_customer_id='')
        .order_by('-started_at')
        .first()
    )

    if existing:
        customer_id = existing.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=request.user.email,
            metadata={'user_id': request.user.pk},
        )
        customer_id = customer['id']

    Subscription.objects.update_or_create(
        user=request.user,
        stripe_customer_id=customer_id,
        defaults={
            'is_active': False,
            'status': SubscriptionStatus.PENDING,
        },
    )

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode='subscription',
        line_items=[{
            'price_data': {
                'currency': sub_settings.currency,
                'product_data': {'name': 'Premium Subscription'},
                'recurring': {'interval': 'month'},
                'unit_amount': int(sub_settings.monthly_price * 100),
            },
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri(reverse('subscriptions:success')),
        cancel_url=request.build_absolute_uri(reverse('subscriptions:cancel')),
        metadata={'user_id': request.user.pk},
    )

    return redirect(session['url'])


@login_required
def checkout_success(request):
    return render(request, 'subscriptions/success.html')


@login_required
def checkout_cancel(request):
    return render(request, 'subscriptions/cancel.html')


@login_required
def cancel_subscription(request):
    subscription = Subscription.objects.active_for(request.user).first()

    if not subscription:
        return redirect('publications:home')

    if request.method == 'POST':
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.cancel(subscription.stripe_subscription_id)
            except stripe.error.StripeError:
                pass

        subscription.is_active = False
        subscription.status = SubscriptionStatus.CANCELED
        subscription.cancelled_at = timezone.now()
        subscription.save()

        return render(request, 'subscriptions/cancel_subscription.html', {
            'cancelled': True,
        })

    return render(request, 'subscriptions/cancel_subscription.html', {
        'subscription': subscription,
    })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    data = event['data']['object']
    event_type = event['type']

    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(data)
    elif event_type in ('customer.subscription.created', 'customer.subscription.updated'):
        _handle_subscription_updated(data)
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_deleted(data)

    return HttpResponse(status=200)


def _handle_checkout_completed(data):
    customer_id = data.get('customer', '')
    subscription_id = data.get('subscription', '')
    if not customer_id:
        return

    sub = (
        Subscription.objects
        .filter(stripe_customer_id=customer_id)
        .order_by('-started_at')
        .first()
    )

    if not sub:
        user_id = data.get('metadata', {}).get('user_id')
        user = User.objects.filter(pk=user_id).first() if user_id else None
        if not user:
            return
        sub = Subscription.objects.create(
            user=user,
            stripe_customer_id=customer_id,
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )

    sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
    sub.is_active = True
    sub.status = SubscriptionStatus.ACTIVE
    sub.cancelled_at = None
    sub.save()


def _handle_subscription_updated(data):
    subscription_id = data.get('id', '')
    if not subscription_id:
        return

    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        sub = (
            Subscription.objects
            .filter(stripe_customer_id=data.get('customer', ''))
            .order_by('-started_at')
            .first()
        )
    if not sub:
        return

    status = data.get('status', 'active')
    sub.stripe_subscription_id = subscription_id
    sub.status = status
    sub.is_active = status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    current_period_end = data.get('current_period_end')
    if current_period_end:
        sub.expires_at = datetime.fromtimestamp(
            current_period_end, tz=dt_timezone.utc
        )

    sub.save()


def _handle_subscription_deleted(data):
    subscription_id = data.get('id', '')
    if not subscription_id:
        return

    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        return

    sub.is_active = False
    sub.status = SubscriptionStatus.CANCELED
    sub.cancelled_at = timezone.now()
    sub.save()
