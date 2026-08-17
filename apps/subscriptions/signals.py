import logging

import stripe
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Subscription

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Subscription)
def cancel_stripe_on_subscription_delete(sender, instance, **kwargs):
    sub_id = instance.stripe_subscription_id
    cust_id = instance.stripe_customer_id

    if sub_id:
        try:
            stripe.Subscription.cancel(sub_id)
        except stripe.error.StripeError:
            logger.exception('Erro ao cancelar assinatura Stripe %s', sub_id)

    if cust_id:
        try:
            stripe.Customer.delete(cust_id)
        except stripe.error.StripeError:
            logger.exception('Erro ao excluir cliente Stripe %s', cust_id)
