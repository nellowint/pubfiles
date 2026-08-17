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
    @patch('apps.subscriptions.views.stripe.Price.create')
    @patch('apps.subscriptions.views.stripe.Product.create')
    def test_creates_checkout_session_and_redirects(self, mock_product, mock_price, mock_customer, mock_session):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=True)
        mock_product.return_value = {'id': 'prod_test_123'}
        mock_price.return_value = {'id': 'price_test_123'}
        mock_customer.return_value = {'id': 'cus_test_123'}
        mock_session.return_value = {'url': 'https://checkout.stripe.com/s/pay/cs_test', 'id': 'cs_test_123'}

        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'https://checkout.stripe.com/s/pay/cs_test')
        mock_customer.assert_called_once()
        args, kwargs = mock_session.call_args
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertEqual(kwargs['line_items'][0]['price'], 'price_test_123')
        self.assertIn('session_id={CHECKOUT_SESSION_ID}', kwargs['success_url'])

        sub = Subscription.objects.filter(user=self.user, stripe_customer_id='cus_test_123').first()
        self.assertIsNotNone(sub)
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.PENDING)
        self.assertEqual(sub.stripe_session_id, 'cs_test_123')

        settings_obj = SubscriptionSettings.objects.get()
        self.assertEqual(settings_obj.stripe_product_id, 'prod_test_123')
        self.assertEqual(settings_obj.stripe_price_id, 'price_test_123')

    @patch('apps.subscriptions.views.stripe.checkout.Session.retrieve')
    @patch('apps.subscriptions.views.stripe.checkout.Session.create')
    @patch('apps.subscriptions.views.stripe.Customer.create')
    @patch('apps.subscriptions.views.stripe.Price.create')
    @patch('apps.subscriptions.views.stripe.Product.create')
    def test_reuses_open_session_to_avoid_loop(self, mock_product, mock_price, mock_customer, mock_session, mock_retrieve):
        """Se já existe uma sessão aberta, reutiliza em vez de criar outra."""
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=True)
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_session_id='cs_open_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        mock_retrieve.return_value = {'status': 'open', 'url': 'https://checkout.stripe.com/s/pay/cs_open'}

        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, 'https://checkout.stripe.com/s/pay/cs_open')
        mock_session.assert_not_called()

    @patch('apps.subscriptions.views.stripe.checkout.Session.create')
    @patch('apps.subscriptions.views.stripe.Customer.create')
    @patch('apps.subscriptions.views.stripe.Price.retrieve')
    @patch('apps.subscriptions.views.stripe.Product.retrieve')
    @patch('apps.subscriptions.views.stripe.Price.create')
    @patch('apps.subscriptions.views.stripe.Product.create')
    def test_existing_price_is_reused_without_recreating(self, mock_product, mock_price, mock_prod_retrieve, mock_price_retrieve, mock_customer, mock_session):
        """Alterações no admin NÃO devem criar novo product/price no Stripe."""
        SubscriptionSettings.objects.create(
            monthly_price='14.99',  # valor alterado desde a criação original
            currency='usd',
            is_enabled=True,
            stripe_product_id='prod_existing_1',
            stripe_price_id='price_existing_1',
        )
        mock_price_retrieve.return_value = {'id': 'price_existing_1'}
        mock_prod_retrieve.return_value = {'id': 'prod_existing_1'}
        mock_customer.return_value = {'id': 'cus_test_123'}
        mock_session.return_value = {'url': 'https://checkout.stripe.com/s/pay/cs_test', 'id': 'cs_test_123'}

        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url)

        self.assertEqual(resp.status_code, 302)
        mock_product.assert_not_called()
        mock_price.assert_not_called()
        args, kwargs = mock_session.call_args
        self.assertEqual(kwargs['line_items'][0]['price'], 'price_existing_1')

    def test_redirects_to_next_when_already_active(self):
        SubscriptionSettings.objects.create(monthly_price='9.99', currency='usd', is_enabled=True)
        Subscription.objects.create(user=self.user)
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url, {'next': '/publication/foo/read/page/4/'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/publication/foo/read/page/4/')


class CheckoutSuccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')
        self.url = reverse('subscriptions:success')
        self.client.login(email='reader@example.com', password='secret123')

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_no_active_subscription_shows_pending(self):
        resp = self.client.get(self.url, {'session_id': 'cs_test_1', 'next': '/publication/foo/read/page/4/'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'subscriptions/success.html')
        self.assertTrue(resp.context['pending'])
        self.assertEqual(resp.context['next_url'], '/publication/foo/read/page/4/')

    @patch('apps.subscriptions.views.stripe.checkout.Session.retrieve')
    def test_paid_session_activates_and_redirects_to_next(self, mock_retrieve):
        Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        mock_retrieve.return_value = {
            'customer': 'cus_test_123',
            'subscription': 'sub_test_456',
            'payment_status': 'paid',
        }

        with patch('apps.subscriptions.views.stripe.Subscription.retrieve') as mock_sub_retrieve:
            mock_sub_retrieve.return_value = {'current_period_end': int((timezone.now() + timedelta(days=30)).timestamp())}
            resp = self.client.get(self.url, {'session_id': 'cs_test_1', 'next': '/publication/foo/read/page/4/'})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/publication/foo/read/page/4/')
        sub = Subscription.objects.get(user=self.user, stripe_customer_id='cus_test_123')
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(sub.stripe_subscription_id, 'sub_test_456')
        self.assertIsNotNone(sub.expires_at)

    @patch('apps.subscriptions.views.stripe.checkout.Session.retrieve')
    def test_unpaid_session_does_not_activate(self, mock_retrieve):
        Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        mock_retrieve.return_value = {
            'customer': 'cus_test_123',
            'subscription': 'sub_test_456',
            'payment_status': 'unpaid',
        }
        resp = self.client.get(self.url, {'session_id': 'cs_test_1', 'next': '/publication/foo/read/page/4/'})
        self.assertEqual(resp.status_code, 200)
        sub = Subscription.objects.get(user=self.user, stripe_customer_id='cus_test_123')
        self.assertFalse(sub.is_active)


class CheckoutCancelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')
        self.url = reverse('subscriptions:cancel')

    def test_cancel_renders_and_keeps_next(self):
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self.url, {'next': '/publication/foo/read/page/4/'})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'subscriptions/cancel.html')
        self.assertContains(resp, '/publication/foo/read/page/4/')


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
            'id': 'evt_completed_1',
            'data': {'object': {
                'customer': 'cus_test_123',
                'subscription': 'sub_test_456',
                'payment_status': 'paid',
            }},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(sub.stripe_subscription_id, 'sub_test_456')

    def test_checkout_completed_unpaid_does_not_activate(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        event = {
            'type': 'checkout.session.completed',
            'id': 'evt_unpaid_1',
            'data': {'object': {
                'customer': 'cus_test_123',
                'subscription': 'sub_test_456',
                'payment_status': 'unpaid',
            }},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.PENDING)

    def test_checkout_completed_is_idempotent(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        event = {
            'type': 'checkout.session.completed',
            'id': 'evt_same_1',
            'data': {'object': {
                'customer': 'cus_test_123',
                'subscription': 'sub_test_456',
                'payment_status': 'paid',
            }},
        }
        self._post_event(event)
        sub.refresh_from_db()
        self.assertEqual(sub.last_event_id, 'evt_same_1')
        sub.stripe_subscription_id = 'changed_manually'
        sub.save()
        self._post_event(event)
        sub.refresh_from_db()
        # Evento repetido não deve sobrescrever o estado atualizado.
        self.assertEqual(sub.stripe_subscription_id, 'changed_manually')

    def test_checkout_session_expired_marks_incomplete(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_session_id='cs_expired_1',
            is_active=False,
            status=SubscriptionStatus.PENDING,
        )
        event = {
            'type': 'checkout.session.expired',
            'id': 'evt_expired_1',
            'data': {'object': {'id': 'cs_expired_1'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.status, SubscriptionStatus.INCOMPLETE)
        self.assertFalse(sub.is_active)

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
            'id': 'evt_updated_1',
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
            'id': 'evt_deleted_1',
            'data': {'object': {'id': 'sub_test_456', 'status': 'canceled'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertFalse(sub.is_active)
        self.assertEqual(sub.status, SubscriptionStatus.CANCELED)
        self.assertIsNotNone(sub.cancelled_at)

    def test_invoice_payment_failed_marks_past_due(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_subscription_id='sub_test_456',
            is_active=True,
            status=SubscriptionStatus.ACTIVE,
        )
        event = {
            'type': 'invoice.payment_failed',
            'id': 'evt_payment_failed_1',
            'data': {'object': {'subscription': 'sub_test_456'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.status, SubscriptionStatus.PAST_DUE)

    def test_invoice_paid_reactivates(self):
        sub = Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_subscription_id='sub_test_456',
            is_active=False,
            status=SubscriptionStatus.PAST_DUE,
        )
        event = {
            'type': 'invoice.paid',
            'id': 'evt_invoice_paid_1',
            'data': {'object': {'subscription': 'sub_test_456'}},
        }
        resp = self._post_event(event)
        self.assertEqual(resp.status_code, 200)
        sub.refresh_from_db()
        self.assertEqual(sub.status, SubscriptionStatus.ACTIVE)
        self.assertTrue(sub.is_active)


class SubscriptionDeleteSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')

    @patch('apps.subscriptions.signals.stripe.Subscription.cancel')
    @patch('apps.subscriptions.signals.stripe.Customer.delete')
    def test_user_delete_cancels_subscription_and_customer(self, mock_customer_delete, mock_sub_cancel):
        Subscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test_123',
            stripe_subscription_id='sub_test_456',
            is_active=True,
            status=SubscriptionStatus.ACTIVE,
        )

        self.user.delete()

        mock_sub_cancel.assert_called_once_with('sub_test_456')
        mock_customer_delete.assert_called_once_with('cus_test_123')

    @patch('apps.subscriptions.signals.stripe.Subscription.cancel')
    @patch('apps.subscriptions.signals.stripe.Customer.delete')
    def test_user_delete_skips_stripe_without_ids(self, mock_customer_delete, mock_sub_cancel):
        Subscription.objects.create(user=self.user)

        self.user.delete()

        mock_sub_cancel.assert_not_called()
        mock_customer_delete.assert_not_called()
