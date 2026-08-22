from django.contrib import admin

from .models import Subscription, SubscriptionSettings


@admin.register(SubscriptionSettings)
class SubscriptionSettingsAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'monthly_price', 'currency', 'is_enabled', 'updated_at')
    readonly_fields = ('updated_at', 'stripe_product_id', 'stripe_price_id')
    fieldsets = (
        (None, {'fields': ('is_enabled',)}),
        ('Produto', {'fields': ('product_name', 'product_description', 'product_image')}),
        ('Precificação', {'fields': ('monthly_price', 'currency')}),
        ('Stripe', {'fields': ('stripe_product_id', 'stripe_price_id')}),
        ('Metadados', {'fields': ('updated_at',)}),
    )

    def has_add_permission(self, request):
        return not SubscriptionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        js = ('js/admin-clickable-rows.js',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'status',
        'is_active',
        'is_valid',
        'started_at',
        'expires_at',
        'cancelled_at',
    )
    list_filter = ('status', 'is_active')
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'stripe_customer_id',
        'stripe_subscription_id',
    )
    readonly_fields = (
        'started_at',
        'updated_at',
        'is_valid',
        'stripe_customer_id',
        'stripe_subscription_id',
        'stripe_session_id',
        'last_event_id',
    )
    ordering = ('-started_at',)

    fieldsets = (
        (None, {'fields': ('user', 'status', 'is_active')}),
        ('Stripe', {'fields': ('stripe_customer_id', 'stripe_subscription_id', 'stripe_session_id', 'last_event_id')}),
        ('Período', {'fields': ('started_at', 'expires_at', 'cancelled_at')}),
        ('Metadados', {'fields': ('updated_at', 'is_valid')}),
    )

    def is_valid(self, obj):
        return obj.is_valid
    is_valid.boolean = True
    is_valid.short_description = 'Válida agora?'

    class Media:
        js = ('js/admin-clickable-rows.js',)
