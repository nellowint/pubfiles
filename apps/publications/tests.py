import io

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.accounts.models import User
from apps.categories.models import Category
from apps.publications.models import Comment, Page, Publication, Rating
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


class ViewsCountTests(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title='Views Magazine',
            cover=page_image('cover.png'),
        )
        for i in range(1, 4):
            Page.objects.create(
                publication=self.publication,
                image=page_image(f'page-{i}.png'),
                page_order=i,
            )

    def test_detail_does_not_increment_views(self):
        detail_url = reverse('publications:detail', args=[self.publication.slug])
        self.client.get(detail_url)
        self.client.get(detail_url)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.views_count, 0)

    def test_reader_page_1_increments_views(self):
        reader_url = reverse('publications:reader', args=[self.publication.slug, 1])
        self.client.get(reader_url)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.views_count, 1)

    def test_reader_page_2_does_not_increment_views(self):
        reader_url = reverse('publications:reader', args=[self.publication.slug, 2])
        self.client.get(reader_url)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.views_count, 0)


class CommentTests(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title='Commented Magazine',
            cover=page_image('cover.png'),
        )
        self.owner = User.objects.create_user(email='owner@example.com', password='secret123')
        self.other = User.objects.create_user(email='other@example.com', password='secret123')

    def _add_url(self):
        return reverse('publications:add_comment', args=[self.publication.slug])

    def test_anonymous_cannot_comment(self):
        resp = self.client.post(self._add_url(), {'content': 'hi'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)
        self.assertEqual(Comment.objects.count(), 0)

    def test_logged_user_can_comment(self):
        self.client.login(email='owner@example.com', password='secret123')
        resp = self.client.post(self._add_url(), {'content': 'nice pub'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.endswith('#comentarios'))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'nice pub')

    def test_empty_comment_is_ignored(self):
        self.client.login(email='owner@example.com', password='secret123')
        self.client.post(self._add_url(), {'content': '   '})
        self.assertEqual(Comment.objects.count(), 0)

    def test_owner_can_edit_own_comment(self):
        comment = Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='original',
        )
        self.client.login(email='owner@example.com', password='secret123')
        url = reverse('publications:edit_comment', args=[comment.pk])
        resp = self.client.post(url, {'content': 'edited'})
        self.assertEqual(resp.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'edited')

    def test_non_owner_cannot_edit_comment(self):
        comment = Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='original',
        )
        self.client.login(email='other@example.com', password='secret123')
        url = reverse('publications:edit_comment', args=[comment.pk])
        resp = self.client.post(url, {'content': 'hacked'})
        self.assertEqual(resp.status_code, 404)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'original')

    def test_owner_can_delete_own_comment(self):
        comment = Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='bye',
        )
        self.client.login(email='owner@example.com', password='secret123')
        url = reverse('publications:delete_comment', args=[comment.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_non_owner_cannot_delete_comment(self):
        comment = Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='keep',
        )
        self.client.login(email='other@example.com', password='secret123')
        url = reverse('publications:delete_comment', args=[comment.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())

    def test_comments_visible_to_anonymous_on_detail(self):
        Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='visible to all',
        )
        url = reverse('publications:detail', args=[self.publication.slug])
        resp = self.client.get(url)
        self.assertContains(resp, 'visible to all')

    def test_email_not_exposed_in_comments(self):
        Comment.objects.create(
            publication=self.publication,
            user=self.owner,
            content='my comment',
        )
        url = reverse('publications:detail', args=[self.publication.slug])
        resp = self.client.get(url)
        self.assertContains(resp, 'owner')
        self.assertNotContains(resp, 'owner@example.com')


class RatingTests(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title='Rated Magazine',
            cover=page_image('cover.png'),
        )
        self.user = User.objects.create_user(email='rater@example.com', password='secret123')
        self.user2 = User.objects.create_user(email='rater2@example.com', password='secret123')

    def _rate_url(self):
        return reverse('publications:rate', args=[self.publication.slug])

    def test_anonymous_cannot_rate(self):
        resp = self.client.post(self._rate_url(), {'score': 4})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)
        self.assertEqual(Rating.objects.count(), 0)

    def test_logged_user_can_rate(self):
        self.client.login(email='rater@example.com', password='secret123')
        resp = self.client.post(self._rate_url(), {'score': 5})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['avg_rating'], 5.0)
        self.assertEqual(data['ratings_count'], 1)
        self.assertEqual(data['user_rating'], 5)

    def test_rating_update_replaces_previous(self):
        self.client.login(email='rater@example.com', password='secret123')
        self.client.post(self._rate_url(), {'score': 2})
        resp = self.client.post(self._rate_url(), {'score': 4})
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(resp.json()['avg_rating'], 4.0)

    def test_invalid_score_rejected(self):
        self.client.login(email='rater@example.com', password='secret123')
        resp = self.client.post(self._rate_url(), {'score': 10})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post(self._rate_url(), {'score': 0})
        self.assertEqual(resp.status_code, 400)

    def test_average_with_multiple_users(self):
        self.client.login(email='rater@example.com', password='secret123')
        self.client.post(self._rate_url(), {'score': 4})
        self.client.logout()
        self.client.login(email='rater2@example.com', password='secret123')
        resp = self.client.post(self._rate_url(), {'score': 2})
        self.assertEqual(resp.json()['avg_rating'], 3.0)
        self.assertEqual(resp.json()['ratings_count'], 2)

    def test_get_rating_not_allowed(self):
        self.client.login(email='rater@example.com', password='secret123')
        resp = self.client.get(self._rate_url())
        self.assertEqual(resp.status_code, 405)

    def test_rating_visible_on_catalog_card(self):
        Rating.objects.create(publication=self.publication, user=self.user, score=4)
        url = reverse('publications:home')
        resp = self.client.get(url)
        self.assertContains(resp, '4.0')
        self.assertContains(resp, '(1)')


class SimilarPublicationsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Comics')
        self.pub = Publication.objects.create(
            title='Batman Issue',
            cover=page_image('cover.png'),
            category=self.category,
        )

    def test_same_category_appears_as_similar(self):
        other = Publication.objects.create(
            title='Batman Returns',
            cover=page_image('cover2.png'),
            category=self.category,
        )
        url = reverse('publications:detail', args=[self.pub.slug])
        resp = self.client.get(url)
        self.assertContains(resp, other.title)

    def test_similar_excludes_self(self):
        url = reverse('publications:detail', args=[self.pub.slug])
        resp = self.client.get(url)
        similar = resp.context['similar_publications']
        self.assertNotIn(self.pub, similar)
        self.assertFalse(
            any(s.pk == self.pub.pk for s in similar)
        )

    def test_fallback_to_title_when_no_category(self):
        pub_no_cat = Publication.objects.create(
            title='Superman Adventures',
            cover=page_image('cover3.png'),
        )
        other = Publication.objects.create(
            title='Superman Returns',
            cover=page_image('cover4.png'),
        )
        url = reverse('publications:detail', args=[pub_no_cat.slug])
        resp = self.client.get(url)
        self.assertContains(resp, other.title)


class TranslationTests(TestCase):
    def setUp(self):
        self.publication = Publication.objects.create(
            title='Titulo em Portugues',
            cover=page_image('cover.png'),
        )

    @override_settings(MIDDLEWARE=[
        m for m in settings.MIDDLEWARE
        if m != 'django.middleware.locale.LocaleMiddleware'
    ])
    def test_falls_back_to_default_when_translation_missing(self):
        from django.utils import translation
        url = reverse('publications:detail', args=[self.publication.slug])
        with translation.override('en'):
            resp = self.client.get(url)
            content = resp.content.decode('utf-8')
        self.assertIn('Titulo em Portugues', content)

    @override_settings(MIDDLEWARE=[
        m for m in settings.MIDDLEWARE
        if m != 'django.middleware.locale.LocaleMiddleware'
    ])
    def test_shows_translated_title_when_available(self):
        self.publication.title_en = 'English Title'
        self.publication.save()
        from django.utils import translation
        url = reverse('publications:detail', args=[self.publication.slug])
        with translation.override('en'):
            resp = self.client.get(url)
            content = resp.content.decode('utf-8')
        self.assertIn('English Title', content)
        self.assertNotIn('Titulo em Portugues', content)
