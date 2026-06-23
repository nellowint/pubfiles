from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SubscriptionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACTIVE = 'active', 'Active'
    TRIALING = 'trialing', 'Trialing'
    PAST_DUE = 'past_due', 'Past due'
    CANCELED = 'canceled', 'Canceled'
    UNPAID = 'unpaid', 'Unpaid'
    INCOMPLETE = 'incomplete', 'Incomplete'


class SubscriptionSettings(models.Model):
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Monthly price',
        help_text='Value charged monthly for the premium subscription.'
    )
    currency = models.CharField(
        max_length=3,
        default='usd',
        verbose_name='Currency',
        help_text='ISO 4217 code. Example: usd, brl, eur.'
    )
    is_enabled = models.BooleanField(
        default=False,
        verbose_name='Enabled',
        help_text='Enable the subscription checkout for users.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta:
        verbose_name = 'Subscription Settings'
        verbose_name_plural = 'Subscription Settings'

    def __str__(self):
        return f'Subscription Settings - {self.currency.upper()} {self.monthly_price}/mo'

    def clean(self):
        if SubscriptionSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError('A configuration already exists. Edit the existing record.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class SubscriptionManager(models.Manager):
    def active_for(self, user):
        if not user or not user.is_authenticated:
            return self.none()
        now = timezone.now()
        return self.filter(
            user=user,
            is_active=True,
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )

    def is_active_for(self, user):
        return self.active_for(user).exists()


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='User'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        verbose_name='Status'
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Stripe Customer ID'
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Stripe Subscription ID'
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Started at'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expires at',
        help_text='Leave blank for a subscription that does not expire.'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelled at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    objects = SubscriptionManager()

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        status = 'Active' if self.is_valid else 'Inactive'
        return f'{self.user.email} - {status}'

    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        return True
