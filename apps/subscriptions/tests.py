from datetime import timedelta
from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.subscriptions.models import (Subscription, SubscriptionSettings,
                                       SubscriptionStatus)


class SubscriptionManagerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')

    def test_no_subscription_means_inactive(self):
        self.assertFalse(Subscription.objects.is_active_for(self.user))

    def test_active_open_ended_subscription(self):
        Subscription.objects.create(user=self.user)
        self.assertTrue(Subscription.objects.is_active_for(self.user))

    def test_inactive_flag_blocks_access(self):
        Subscription.objects.create(user=self.user, is_active=False)
        self.assertFalse(Subscription.objects.is_active_for(self.user))

    def test_expired_subscription_blocks_access(self):
        Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(Subscription.objects.is_active_for(self.user))

    def test_future_expiry_grants_access(self):
        Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.assertTrue(Subscription.objects.is_active_for(self.user))

    def test_anonymous_user_has_no_access(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(Subscription.objects.is_active_for(AnonymousUser()))

    def test_is_valid_property_matches_manager(self):
        active = Subscription.objects.create(user=self.user)
        expired = Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        self.assertTrue(active.is_valid)
        self.assertFalse(expired.is_valid)


class SubscriptionSettingsTests(TestCase):
    def test_single_row_constraint(self):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd')
        second = SubscriptionSettings(monthly_price='14.99', currency='usd')
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            second.full_clean()

    def test_only_one_row_allowed(self):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd')
        self.assertEqual(SubscriptionSettings.objects.count(), 1)


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')
        self.url = reverse('subscriptions:checkout')

    def test_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_unavailable_when_no_settings(self):
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 503)
        self.assertTemplateUsed(resp, 'subscriptions/unavailable.html')

    def test_unavailable_when_disabled(self):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=False)
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 503)

    def test_redirects_home_when_already_active(self):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=True)
        Subscription.objects.create(user=self.user)
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('publications:home'))

    @patch('apps.subscriptions.views.stripe.checkout.Session.create')
    @patch('apps.subscriptions.views.stripe.Customer.create')
    def test_creates_checkout_session_and_redirects(self, mock_customer, mock_session):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=True)
        mock_customer.return_value = {'id': 'cus_test_123'}
        mock_session.return_value = {'url': 'https://checkout.stripe.com/s/pay/cs_test'}

        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'https://checkout.stripe.com/s/pay/cs_test')
        mock_customer.assert_called_once()
        args, kwargs = mock_session.call_args
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertEqual(kwargs['line_items'][0]['price_data']['unit_amount'], 999)
        self.assertEqual(kwargs['line_items'][0]['price_data']['currency'], 'usd')
        self.assertEqual(kwargs['line_items'][0]['price_data']['recurring']['interval'], 'month')

        sub = Subscription.objects.filter(user=self.user, stripe_customer_id='cus_test_123').first()
        self.assertIsNotNone(sub)
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.PENDING)


class WebhookViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')
        self.url = reverse('subscriptions:webhook')

    def _post_event(self, event):
        with patch('apps.subscriptions.views.stripe.Webhook.construct_event', return_value=event):
            return self.client.post(
                self.url,
                data='payload',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=1,v1=sign',
            )

    def test_invalid_signature_returns_400(self):
        with patch(
            'apps.subscriptions.views.stripe.Webhook.construct_event',
            side_effect=ValueError,
        ):
            resp = self.client.post(
                self.url,
                data='payload',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='bad',
            )
        self.assertEqual(resp.status_code, 400)

    def test_checkout_completed_activates_subscription(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'customer': 'cus_test_123', 'subscription': 'sub_test_456'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(sub.stripe_subscription_id, 'sub_test_456')

    def test_subscription_updated_sets_expiry(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_subscription_id='sub_test_456',
            is_active=True,
            status=SubscriptionStatus.ACTIVE,
        )
        future_ts = int((timezone.now() + timedelta(days=30)).timestamp())
        event = {
            'type': 'customer.subscription.updated',
            'data': {'object': {
                'id': 'sub_test_456',
                'customer': 'cus_test_123',
                'status': 'active',
                'current_period_end': future_ts,
            }},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
        self.assertIsNotNone(sub.expires_at)

    def test_subscription_deleted_cancels(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_subscription_id='sub_test_456',
            is_active=True,
            status=SubscriptionStatus.ACTIVE,
        )
        event = {
            'type': 'customer.subscription.deleted',
            'data': {'object': {'id': 'sub_test_456', 'status': 'canceled'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.CANCELED)
        self.assertIsNotNone(sub.cancelled_at)
