from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('checkout/', views.create_checkout, name='checkout'),
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
