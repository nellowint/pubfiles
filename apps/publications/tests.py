import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.publications.models import Page, Publication
from apps.subscriptions.models import Subscription


def page_image(name='page.png'):
    img = Image.new('RGB', (10, 10), color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type='image/png')


class ReaderGatingTests(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title='Premium Magazine',
            cover=page_image('cover.png'),
            is_members_only=True,
            free_pages_count=2,
        )
        for i in range(1, 5):
            Page.objects.create(
                publication=self.publication,
                image=page_image(f'page-{i}.png'),
                page_order=i,
            )
        self.user = User.objects.create_user(email='reader@example.com', password='secret123')

    def _url(self, page_number):
        return reverse('publications:reader', args=[self.publication.slug, page_number])

    def test_free_page_readable_by_anonymous(self):
        resp = self.client.get(self._url(1))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'publications/reader.html')

    def test_premium_page_blocked_for_anonymous(self):
        resp = self.client.get(self._url(3))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'publications/premium.html')

    def test_premium_page_blocked_for_logged_in_without_subscription(self):
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self._url(3))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'publications/premium.html')

    def test_premium_page_unlocked_with_active_subscription(self):
        Subscription.objects.create(user=self.user)
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self._url(3))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'publications/reader.html')

    def test_premium_page_blocked_with_expired_subscription(self):
        from datetime import timedelta

        from django.utils import timezone
        Subscription.objects.create(
            user=self.user,
            expires_at=timezone.now() - timedelta(days=1),
        )
        self.client.login(email='reader@example.com', password='secret123')
        resp = self.client.get(self._url(3))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'publications/premium.html')
