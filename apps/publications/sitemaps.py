from django.contrib.sitemaps import Sitemap

from apps.publications.models import Publication


class PublicationSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Publication.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class StaticSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 1.0

    def items(self):
        return ['/']

    def location(self, item):
        return item