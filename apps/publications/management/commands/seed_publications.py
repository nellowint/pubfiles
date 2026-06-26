import random
import time

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.categories.models import Category
from apps.publications.models import Page, Publication

PICSUM = 'https://picsum.photos/seed/{seed}/{w}/{h}'

FAKE_TITLES = [
    'Dragon Ball Saga', 'Naruto Shippuden Arc', 'Sakura Blossoms',
    'Hinata Legacy', 'Marvel Universe', 'Homem Aranha Chronicles',
    'DC Legends', 'HQ Fantasia Vol.1', 'HQ Fantasia Vol.2',
    'Dragon Ball Z', 'Naruto Special', 'Marvel Avengers',
    'DC Batman', 'Sakura Memories', 'Hinata Destiny',
    'Fantasia Quest', 'Homem Aranha 2', 'Dragon Ball Super',
    'Marvel X-Men', 'DC Justice League',
]


def fetch_image(width, height, seed):
    url = PICSUM.format(seed=seed, w=width, h=height)
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            return ContentFile(resp.content)
        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f'Failed to fetch {url}: {e}')
            time.sleep(2)


class Command(BaseCommand):
    help = 'Creates fake publications with generated covers and pages.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20)
        parser.add_argument('--pages', type=int, default=3)
        parser.add_argument('--reset', action='store_true',
                            help='Delete existing publications before seeding.')

    def handle(self, *args, **options):
        count = options['count']
        pages = options['pages']
        reset = options['reset']

        if reset:
            deleted, _ = Publication.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} objects.'))

        cats = list(Category.objects.all())
        if not cats:
            self.stdout.write(self.style.ERROR('No categories exist. Create some first.'))
            return

        leaf_cats = [c for c in cats if c.is_leaf_node()] or cats

        created = 0
        for i in range(count):
            title = FAKE_TITLES[i % len(FAKE_TITLES)]
            if i >= len(FAKE_TITLES):
                title = f'{title} #{i}'

            if Publication.objects.filter(title=title).exists():
                title = f'{title} {i}'

            cat = random.choice(leaf_cats)
            cover = fetch_image(400, 600, f'cover-{title.lower().replace(" ", "-")}')

            pub = Publication(
                title=title,
                description=f'Fake description for {title}. Generated for local testing.',
                category=cat,
                is_members_only=(i % 4 == 0),
                free_pages_count=max(1, (i % 3) + 1),
                views_count=random.randint(0, 5000),
            )
            pub.cover.save(f'{pub.slug or title}.jpg', cover, save=False)
            pub.save()

            for p in range(1, pages + 1):
                page_img = fetch_image(800, 1200, f'page-{pub.id}-{p}')
                page = Page(publication=pub, page_order=p)
                page.image.save(f'{pub.slug}-p{p}.jpg', page_img, save=False)
                page.save()

            created += 1
            self.stdout.write(f'  [{created}/{count}] {pub.title} (cat: {cat.name})')

        self.stdout.write(self.style.SUCCESS(f'Done. Created {created} publications.'))