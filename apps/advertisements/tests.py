from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.advertisements.models import Advertisements, AdvertisementsType

SCRIPT = '<script src="https://example.com/p.js"></script>'


class PopunderTests(TestCase):
    def test_clean_popunder_without_position(self):
        ad = Advertisements(type=AdvertisementsType.POPUNDER, link=SCRIPT)
        ad.full_clean()
        self.assertEqual(ad.position, '')

    def test_clean_native_banner_requires_position(self):
        ad = Advertisements(type=AdvertisementsType.NATIVEBANNER, link='https://example.com/')
        with self.assertRaises(ValidationError):
            ad.full_clean()

    def test_str_popunder_without_position(self):
        ad = Advertisements(
            type=AdvertisementsType.POPUNDER, title='Pop', link=SCRIPT
        )
        self.assertIn('Popunder', str(ad))

    def test_home_renders_active_script_popunder(self):
        Advertisements.objects.create(type=AdvertisementsType.POPUNDER, link=SCRIPT)
        response = self.client.get('/')
        self.assertEqual(response.context['ads_popunder'].link, SCRIPT)
        self.assertContains(response, 'https://example.com/p.js')

    def test_first_active_script_popunder_wins(self):
        Advertisements.objects.create(type=AdvertisementsType.POPUNDER, link=SCRIPT)
        Advertisements.objects.create(
            type=AdvertisementsType.POPUNDER,
            link='<script src="https://example.com/second.js"></script>',
        )
        response = self.client.get('/')
        self.assertContains(response, 'https://example.com/p.js')
        self.assertNotContains(response, 'https://example.com/second.js')

    def test_url_popunder_ignored_in_global_slot(self):
        Advertisements.objects.create(
            type=AdvertisementsType.POPUNDER, link='https://example.com/offer'
        )
        response = self.client.get('/')
        self.assertIsNone(response.context['ads_popunder'])

    def test_inactive_popunder_not_rendered(self):
        Advertisements.objects.create(
            type=AdvertisementsType.POPUNDER, link=SCRIPT, is_active=False
        )
        response = self.client.get('/')
        self.assertIsNone(response.context['ads_popunder'])
        self.assertNotContains(response, 'https://example.com/p.js')

    def test_premium_sees_no_popunder(self):
        Advertisements.objects.create(type=AdvertisementsType.POPUNDER, link=SCRIPT)
        admin = User.objects.create_superuser(email='admin@example.com', password='StrongPass123!')
        self.client.force_login(admin)
        response = self.client.get('/')
        self.assertIsNone(response.context['ads_popunder'])
        self.assertNotContains(response, 'https://example.com/p.js')
