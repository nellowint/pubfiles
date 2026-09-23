from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts import recaptcha as recaptcha_mod
from apps.accounts.models import User
from apps.accounts.tokens import account_verification_token
from core import email as email_mod


PASSWORD = 'StrongPass123!'


class RegisterTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_register_creates_unverified_user_and_sends_email(self):
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })
        self.assertRedirects(response, reverse('verification_sent'))
        user = User.objects.get(email='new@example.com')
        self.assertFalse(user.email_verified)
        email_mod.flush_email_queue()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Confirm your email address')
        self.assertEqual(mail.outbox[0].to, ['new@example.com'])

    def test_register_invalid_passwords_creates_no_user(self):
        response = self.client.post(reverse('register'), {
            'email': 'bad@example.com',
            'password1': PASSWORD,
            'password2': 'Different123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='bad@example.com').exists())

    def test_register_rate_limited_after_three_attempts(self):
        for i in range(3):
            self.client.post(reverse('register'), {
                'email': f'user{i}@example.com',
                'password1': PASSWORD,
                'password2': PASSWORD,
            })
        email_mod.flush_email_queue()
        response = self.client.post(reverse('register'), {
            'email': 'blocked@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['rate_limited'])
        self.assertFalse(User.objects.filter(email='blocked@example.com').exists())

    def test_verification_sent_view_renders(self):
        response = self.client.get(reverse('verification_sent'))
        self.assertEqual(response.status_code, 200)


class ConfirmEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='confirm@example.com', password=PASSWORD)

    def confirm_url(self, user=None, token=None):
        user = user or self.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token if token is not None else account_verification_token.make_token(user)
        return reverse('confirm_email', kwargs={'uidb64': uid, 'token': token})

    def test_valid_token_verifies_email(self):
        response = self.client.get(self.confirm_url())
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_invalid_token_keeps_unverified(self):
        response = self.client.get(self.confirm_url(token='invalid-token'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['invalid_token'])
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)

    def test_unknown_user_shows_invalid(self):
        uid = urlsafe_base64_encode(force_bytes(99999))
        url = reverse('confirm_email', kwargs={'uidb64': uid, 'token': 'any-token'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['invalid_token'])


class LoginTests(TestCase):
    def setUp(self):
        self.verified = User.objects.create_user(email='verified@example.com', password=PASSWORD)
        self.verified.email_verified = True
        self.verified.save(update_fields=['email_verified'])
        self.unverified = User.objects.create_user(email='unverified@example.com', password=PASSWORD)

    def test_unverified_user_cannot_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'unverified@example.com',
            'password': PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_verified_user_can_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'verified@example.com',
            'password': PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.verified.pk)

    def test_remember_me_keeps_session(self):
        self.client.post(reverse('login'), {
            'username': 'verified@example.com',
            'password': PASSWORD,
            'remember_me': 'on',
        })
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_without_remember_me_session_expires_on_browser_close(self):
        self.client.post(reverse('login'), {
            'username': 'verified@example.com',
            'password': PASSWORD,
        })
        self.assertTrue(self.client.session.get_expire_at_browser_close())


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='reset@example.com', password=PASSWORD)

    def test_reset_sends_email_for_known_address(self):
        response = self.client.post(reverse('password_reset'), {'email': 'reset@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        email_mod.flush_email_queue()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['reset@example.com'])

    def test_reset_unknown_address_sends_nothing_but_redirects(self):
        response = self.client.post(reverse('password_reset'), {'email': 'nobody@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        email_mod.flush_email_queue()
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_email_contains_valid_token_link(self):
        self.client.post(reverse('password_reset'), {'email': 'reset@example.com'})
        email_mod.flush_email_queue()
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn('/password-reset/confirm/', body)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='profile@example.com', password=PASSWORD)
        self.client.force_login(self.user)

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_profile_renders_for_logged_user(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_change_password_with_correct_old_password(self):
        response = self.client.post(reverse('profile'), {
            'old_password': PASSWORD,
            'new_password1': 'NewStrongPass456!',
            'new_password2': 'NewStrongPass456!',
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass456!'))

    def test_change_password_with_wrong_old_password_fails(self):
        response = self.client.post(reverse('profile'), {
            'old_password': 'WrongPass!',
            'new_password1': 'NewStrongPass456!',
            'new_password2': 'NewStrongPass456!',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_delete_account_with_correct_password(self):
        response = self.client.post(reverse('profile'), {
            'action': 'delete_account',
            'password': PASSWORD,
        })
        self.assertRedirects(response, reverse('publications:home'))
        self.assertFalse(User.objects.filter(email='profile@example.com').exists())

    def test_delete_account_with_wrong_password_keeps_user(self):
        response = self.client.post(reverse('profile'), {
            'action': 'delete_account',
            'password': 'WrongPass!',
        })
        # senha errada adiciona messages.error e o ProfileForm vazio redireciona, mas o usuário é mantido
        self.assertRedirects(response, reverse('profile'))
        self.assertTrue(User.objects.filter(email='profile@example.com').exists())

    def test_remove_avatar_without_avatar_redirects(self):
        response = self.client.post(reverse('profile'), {'action': 'remove_avatar'})
        self.assertRedirects(response, reverse('profile'))


class SendMailAsyncTests(TestCase):
    def test_returns_future_and_sends_email(self):
        future = email_mod.send_mail_async('subject', 'body', ['to@example.com'])
        self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertTrue(future.done())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'subject')

    def test_invalid_recipients_are_ignored(self):
        future = email_mod.send_mail_async('s', 'b', ['not-an-email', ''])
        self.assertFalse(future.result(timeout=10))
        self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertEqual(len(mail.outbox), 0)

    def test_retries_on_transient_failure(self):
        calls = {'n': 0}

        def flaky(*args, **kwargs):
            calls['n'] += 1
            if calls['n'] < 3:
                raise ConnectionError('smtp down')
            return 1

        with patch('django.core.mail.send_mail', side_effect=flaky):
            with patch.object(email_mod.time, 'sleep', return_value=None):
                future = email_mod.send_mail_async('s', 'b', ['x@y.com'])
                self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertEqual(calls['n'], 3)
        self.assertTrue(future.done())

    def test_total_failure_logs_masked_email_without_raising(self):
        with patch('django.core.mail.send_mail', side_effect=ConnectionError('down')):
            with patch.object(email_mod.time, 'sleep', return_value=None):
                with self.assertLogs('core.email', level='ERROR') as logs:
                    future = email_mod.send_mail_async('s', 'b', ['x@y.com'])
                    self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertTrue(future.done())
        output = '\n'.join(logs.output)
        self.assertIn('x***@y.com', output)
        self.assertNotIn('x@y.com', output)

    def test_success_callback_called(self):
        received = {}
        future = email_mod.send_mail_async(
            's', 'b', ['x@y.com'],
            on_success=lambda ok: received.setdefault('ok', ok),
        )
        self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertTrue(future.done())
        self.assertTrue(received.get('ok'))

    def test_error_callback_called_on_total_failure(self):
        received = {}
        with patch('django.core.mail.send_mail', side_effect=ConnectionError('down')):
            with patch.object(email_mod.time, 'sleep', return_value=None):
                future = email_mod.send_mail_async(
                    's', 'b', ['x@y.com'],
                    on_error=lambda ok: received.setdefault('ok', ok),
                )
                self.assertTrue(email_mod.flush_email_queue(timeout=10))
        self.assertTrue(future.done())
        self.assertFalse(received.get('ok'))


class FakeRecaptchaResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def recaptcha_success():
    return FakeRecaptchaResponse({'success': True})


@override_settings(RECAPTCHA_SITE_KEY='test-site', RECAPTCHA_SECRET_KEY='test-secret')
class RecaptchaHelperTests(TestCase):
    def test_valid_token_returns_true(self):
        with patch('apps.accounts.recaptcha.requests.post', return_value=recaptcha_success()):
            self.assertTrue(recaptcha_mod.verify_recaptcha_token('token'))

    def test_invalid_token_returns_false(self):
        with patch('apps.accounts.recaptcha.requests.post',
                   return_value=FakeRecaptchaResponse({'success': False})):
            self.assertFalse(recaptcha_mod.verify_recaptcha_token('token'))

    def test_network_error_returns_false(self):
        with patch('apps.accounts.recaptcha.requests.post', side_effect=ConnectionError('down')):
            self.assertFalse(recaptcha_mod.verify_recaptcha_token('token'))

    def test_empty_token_returns_false(self):
        self.assertFalse(recaptcha_mod.verify_recaptcha_token(''))

    @override_settings(RECAPTCHA_SITE_KEY='', RECAPTCHA_SECRET_KEY='')
    def test_unconfigured_returns_true(self):
        self.assertTrue(recaptcha_mod.verify_recaptcha_token(''))


@override_settings(RECAPTCHA_SITE_KEY='test-site', RECAPTCHA_SECRET_KEY='test-secret')
class RecaptchaFormsTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_register_blocked_on_recaptcha_failure(self):
        with patch('apps.accounts.recaptcha.requests.post',
                   return_value=FakeRecaptchaResponse({'success': False})):
            response = self.client.post(reverse('register'), {
                'email': 'blocked@example.com',
                'password1': PASSWORD,
                'password2': PASSWORD,
                'g-recaptcha-response': 'token',
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['recaptcha_failed'])
        self.assertFalse(User.objects.filter(email='blocked@example.com').exists())

    def test_register_allowed_on_recaptcha_success(self):
        with patch('apps.accounts.recaptcha.requests.post', return_value=recaptcha_success()):
            response = self.client.post(reverse('register'), {
                'email': 'ok@example.com',
                'password1': PASSWORD,
                'password2': PASSWORD,
                'g-recaptcha-response': 'token',
            })
        self.assertRedirects(response, reverse('verification_sent'))
        self.assertTrue(User.objects.filter(email='ok@example.com').exists())
        email_mod.flush_email_queue()

    def test_login_blocked_on_recaptcha_failure(self):
        user = User.objects.create_user(email='captcha@example.com', password=PASSWORD)
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        with patch('apps.accounts.recaptcha.requests.post',
                   return_value=FakeRecaptchaResponse({'success': False})):
            response = self.client.post(reverse('login'), {
                'username': 'captcha@example.com',
                'password': PASSWORD,
                'g-recaptcha-response': 'token',
            })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_allowed_on_recaptcha_success(self):
        user = User.objects.create_user(email='login-ok@example.com', password=PASSWORD)
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        with patch('apps.accounts.recaptcha.requests.post', return_value=recaptcha_success()):
            response = self.client.post(reverse('login'), {
                'username': 'login-ok@example.com',
                'password': PASSWORD,
                'g-recaptcha-response': 'token',
            })
        self.assertRedirects(response, reverse('publications:home'))

    def test_password_reset_blocked_on_recaptcha_failure(self):
        User.objects.create_user(email='reset-captcha@example.com', password=PASSWORD)
        with patch('apps.accounts.recaptcha.requests.post',
                   return_value=FakeRecaptchaResponse({'success': False})):
            response = self.client.post(reverse('password_reset'), {'email': 'reset-captcha@example.com', 'g-recaptcha-response': 'token'})
        self.assertEqual(response.status_code, 200)
        email_mod.flush_email_queue()
        self.assertEqual(len(mail.outbox), 0)

    def test_forms_render_recaptcha_widget(self):
        for url_name in ('login', 'register', 'password_reset'):
            response = self.client.get(reverse(url_name))
            self.assertContains(response, 'class="g-recaptcha"')
            self.assertContains(response, 'https://www.google.com/recaptcha/api.js')
