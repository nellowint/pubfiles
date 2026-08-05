from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SubscriptionStatus(models.TextChoices):
    PENDING = 'pending', 'Pendente'
    ACTIVE = 'active', 'Ativa'
    TRIALING = 'trialing', 'Em teste'
    PAST_DUE = 'past_due', 'Atrasada'
    CANCELED = 'canceled', 'Cancelada'
    UNPAID = 'unpaid', 'Não paga'
    INCOMPLETE = 'incomplete', 'Incompleta'


class SubscriptionSettings(models.Model):
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Preço mensal',
        help_text='Valor cobrado mensalmente pela assinatura premium.',
    )
    currency = models.CharField(
        max_length=3,
        default='usd',
        verbose_name='Moeda',
        help_text='Código ISO 4217. Exemplo: usd, brl, eur.',
    )
    is_enabled = models.BooleanField(
        default=False,
        verbose_name='Habilitado',
        help_text='Habilita o checkout de assinatura para os usuários.',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em',
    )

    class Meta:
        verbose_name = 'Configuração de assinatura'
        verbose_name_plural = 'Configurações de assinatura'

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
        verbose_name='Usuário',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa',
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
        verbose_name='Status',
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='ID do cliente Stripe',
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='ID da assinatura Stripe',
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Iniciada em',
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira em',
        help_text='Deixe em branco para uma assinatura que não expira.',
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Cancelada em',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizada em',
    )

    objects = SubscriptionManager()

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

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
