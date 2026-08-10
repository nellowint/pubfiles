from django.test import TestCase, override_settings

from apps.website.models import WebSettings


class WebSettingsStartMessageTests(TestCase):
    def test_start_message_default_blank(self):
        settings = WebSettings.objects.create()
        self.assertEqual(settings.start_message, '')

    def test_start_message_translatable(self):
        settings = WebSettings.objects.create(start_message='Aviso em pt')
        settings.start_message_en = 'Notice in English'
        settings.save()

        from django.utils import translation
        restored = WebSettings.objects.get(pk=settings.pk)

        with translation.override('en'):
            self.assertEqual(restored.start_message, 'Notice in English')

        with translation.override('pt-br'):
            self.assertEqual(restored.start_message, 'Aviso em pt')

    def test_modal_renders_on_home_when_message_exists(self):
        WebSettings.objects.create(start_message='Boas-vindas do site')
        with override_settings(MIDDLEWARE=[
            m for m in __import__('django').conf.settings.MIDDLEWARE
            if m != 'django.middleware.locale.LocaleMiddleware'
        ]):
            resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Boas-vindas do site')
        self.assertContains(resp, 'startModal')

    def test_modal_not_rendered_when_message_blank(self):
        WebSettings.objects.create()
        resp = self.client.get('/')
        self.assertNotContains(resp, 'startModal')