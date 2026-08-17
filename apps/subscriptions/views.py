import logging
from datetime import datetime
from datetime import timezone as dt_timezone

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import User

from .models import Subscription, SubscriptionSettings, SubscriptionStatus

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def _safe_next(request, default=None):
    """Valida o parâmetro next, aceitando apenas URLs internas do site."""
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return next_url
    return default or '/'


def _ensure_stripe_price(sub_settings, request=None):
    """Reutiliza o produto e preço fixo já existentes no Stripe.

    Nunca cria um novo Price/Product quando o SubscriptionSettings já possui
    IDs salvos — alterações no admin não devem duplicar objetos no Stripe.
    Apenas cria quando não existem (primeiro uso) ou quando os IDs salvos não
    são mais válidos no Stripe.
    """
    product_id = sub_settings.stripe_product_id
    price_id = sub_settings.stripe_price_id

    if product_id and price_id:
        try:
            stripe.Price.retrieve(price_id)
            stripe.Product.retrieve(product_id)
            return product_id, price_id
        except stripe.error.StripeError:
            # IDs órfãos/inválidos — recria a partir do zero.
            product_id = ''
            price_id = ''

    amount = int(sub_settings.monthly_price * 100)
    product_data = {
        'name': sub_settings.product_name or 'Premium Subscription',
    }
    if sub_settings.product_description:
        product_data['description'] = sub_settings.product_description
    if sub_settings.product_image and request:
        product_data['images'] = [
            request.build_absolute_uri(sub_settings.product_image.url)
        ]

    if not product_id:
        product = stripe.Product.create(**product_data)
        product_id = product['id']

    if not price_id:
        price = stripe.Price.create(
            currency=sub_settings.currency,
            unit_amount=amount,
            recurring={'interval': 'month'},
            product=product_id,
        )
        price_id = price['id']

    return product_id, price_id


@login_required
def create_checkout(request):
    sub_settings = SubscriptionSettings.objects.first()
    if not sub_settings or not sub_settings.is_enabled:
        return render(request, 'subscriptions/unavailable.html', status=503)

    if Subscription.objects.is_active_for(request.user):
        return redirect(_safe_next(request, default=reverse('publications:home')))

    next_url = _safe_next(request, default=reverse('publications:home'))
    success_url = request.build_absolute_uri(
        reverse('subscriptions:success')
    ) + '?session_id={CHECKOUT_SESSION_ID}&next=' + next_url
    cancel_url = request.build_absolute_uri(
        reverse('subscriptions:cancel')
    ) + '?next=' + next_url

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

    # Anti-loop: se já existe uma sessão de checkout aberta, reutiliza em vez de criar outra.
    if existing and existing.stripe_session_id:
        try:
            session = stripe.checkout.Session.retrieve(existing.stripe_session_id)
            if session['status'] == 'open':
                return redirect(session['url'])
        except stripe.error.StripeError:
            pass

    product_id, price_id = _ensure_stripe_price(sub_settings, request=request)

    sub_settings.stripe_product_id = product_id
    sub_settings.stripe_price_id = price_id
    sub_settings.save(update_fields=['stripe_product_id', 'stripe_price_id'])

    sub, _ = Subscription.objects.update_or_create(
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
            'price': price_id,
            'quantity': 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'user_id': request.user.pk},
    )

    sub.stripe_session_id = session['id']
    sub.save(update_fields=['stripe_session_id'])

    return redirect(session['url'])


@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    next_url = _safe_next(request, default=reverse('publications:home'))

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session['payment_status'] == 'paid':
                _activate_subscription_from_session(request.user, session)
        except stripe.error.StripeError:
            session = None

    # Aguarda o webhook caso ele ainda não tenha processado o pagamento.
    if not Subscription.objects.is_active_for(request.user):
        return render(request, 'subscriptions/success.html', {
            'pending': True,
            'next_url': next_url,
        })

    return redirect(next_url)


def _stripe_field(obj, name):
    """Lê um campo de objeto do Stripe com segurança (StripeObject não tem .get())."""
    try:
        value = obj[name]
    except (KeyError, AttributeError, TypeError):
        return ''
    if value is None:
        return ''
    return value


def _activate_subscription_from_session(user, session):
    """Ativa a Subscription localmente usando dados da sessão do Stripe."""
    customer_id = _stripe_field(session, 'customer')
    subscription_id = _stripe_field(session, 'subscription')

    sub = (
        Subscription.objects
        .filter(user=user, stripe_customer_id=customer_id)
        .order_by('-started_at')
        .first()
    )

    if not sub:
        sub, _ = Subscription.objects.get_or_create(
            user=user,
            stripe_customer_id=customer_id,
            defaults={
                'is_active': False,
                'status': SubscriptionStatus.PENDING,
            },
        )

    expires_at = None
    if subscription_id:
        try:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            current_period_end = _stripe_field(stripe_sub, 'current_period_end')
            if current_period_end:
                expires_at = datetime.fromtimestamp(
                    current_period_end, tz=dt_timezone.utc
                )
        except stripe.error.StripeError:
            pass

    sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
    sub.is_active = True
    sub.status = SubscriptionStatus.ACTIVE
    sub.expires_at = expires_at or sub.expires_at
    sub.cancelled_at = None
    sub.save()


@login_required
def checkout_cancel(request):
    next_url = _safe_next(request, default=reverse('publications:home'))
    return render(request, 'subscriptions/cancel.html', {
        'next_url': next_url,
    })


@login_required
def cancel_subscription(request):
    subscription = Subscription.objects.active_for(request.user).first()

    if not subscription:
        return redirect('publications:home')

    if request.method == 'POST':
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
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

    try:
        if event_type == 'checkout.session.completed':
            _handle_checkout_completed(data, event['id'])
        elif event_type == 'checkout.session.expired':
            _handle_checkout_expired(data)
        elif event_type in ('customer.subscription.created', 'customer.subscription.updated'):
            _handle_subscription_updated(data, event['id'])
        elif event_type == 'customer.subscription.deleted':
            _handle_subscription_deleted(data, event['id'])
        elif event_type == 'invoice.payment_failed':
            _handle_invoice_payment_failed(data, event['id'])
        elif event_type == 'invoice.paid':
            _handle_invoice_paid(data, event['id'])
    except Exception:
        logger.exception('Erro ao processar webhook do Stripe: %s', event_type)
        return HttpResponse(status=500)

    return HttpResponse(status=200)


def _handle_checkout_completed(data, event_id):
    customer_id = _stripe_field(data, 'customer')
    subscription_id = _stripe_field(data, 'subscription')
    if not customer_id:
        return

    # Só ativa quando o pagamento foi de fato confirmado pelo Stripe.
    if _stripe_field(data, 'payment_status') != 'paid':
        return

    sub = (
        Subscription.objects
        .filter(stripe_customer_id=customer_id)
        .order_by('-started_at')
        .first()
    )

    if not sub:
        metadata = _stripe_field(data, 'metadata')
        user_id = _stripe_field(metadata, 'user_id') if metadata else ''
        user = User.objects.filter(pk=user_id).first() if user_id else None
        if not user:
            return
        sub = Subscription.objects.create(
            user=user,
            stripe_customer_id=customer_id,
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )

    if sub.last_event_id == event_id:
        return

    sub.stripe_subscription_id = subscription_id or sub.stripe_subscription_id
    sub.is_active = True
    sub.status = SubscriptionStatus.ACTIVE
    sub.cancelled_at = None
    sub.last_event_id = event_id
    sub.save()


def _handle_checkout_expired(data):
    """Sessão de checkout expirou sem pagamento — mantém a assinatura sem acesso."""
    session_id = _stripe_field(data, 'id')
    if not session_id:
        return
    sub = Subscription.objects.filter(stripe_session_id=session_id).first()
    if not sub:
        return
    sub.status = SubscriptionStatus.INCOMPLETE
    sub.is_active = False
    sub.save(update_fields=['status', 'is_active'])


def _handle_subscription_updated(data, event_id):
    subscription_id = _stripe_field(data, 'id')
    if not subscription_id:
        return

    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        sub = (
            Subscription.objects
            .filter(stripe_customer_id=_stripe_field(data, 'customer'))
            .order_by('-started_at')
            .first()
        )
    if not sub:
        return

    if sub.last_event_id == event_id:
        return

    status = _stripe_field(data, 'status') or 'active'
    sub.stripe_subscription_id = subscription_id
    sub.status = status
    sub.is_active = status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING)

    current_period_end = _stripe_field(data, 'current_period_end')
    if current_period_end:
        sub.expires_at = datetime.fromtimestamp(
            current_period_end, tz=dt_timezone.utc
        )

    sub.last_event_id = event_id
    sub.save()


def _handle_subscription_deleted(data, event_id):
    subscription_id = _stripe_field(data, 'id')
    if not subscription_id:
        return

    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        return

    if sub.last_event_id == event_id:
        return

    sub.is_active = False
    sub.status = SubscriptionStatus.CANCELED
    sub.cancelled_at = timezone.now()
    sub.last_event_id = event_id
    sub.save()


def _handle_invoice_payment_failed(data, event_id):
    subscription_id = _stripe_field(data, 'subscription')
    if not subscription_id:
        return
    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        return
    if sub.last_event_id == event_id:
        return
    sub.status = SubscriptionStatus.PAST_DUE
    sub.last_event_id = event_id
    sub.save(update_fields=['status', 'last_event_id'])


def _handle_invoice_paid(data, event_id):
    subscription_id = _stripe_field(data, 'subscription')
    if not subscription_id:
        return
    sub = Subscription.objects.filter(stripe_subscription_id=subscription_id).first()
    if not sub:
        return
    if sub.last_event_id == event_id:
        return
    sub.status = SubscriptionStatus.ACTIVE
    sub.is_active = True
    sub.last_event_id = event_id
    sub.save(update_fields=['status', 'is_active', 'last_event_id'])
