import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.publications.models import Page, Publication
from apps.website.models import WebSettings


class Command(BaseCommand):
    help = (
        "Remove arquivos de mídia órfãos (sem registro correspondente no banco). "
        "Use --delete para apagar; sem flag, apenas lista."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Lista os órfãos sem apagar (padrão).',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Apaga os arquivos órfãos do disco.',
        )

    def handle(self, *args, **options):
        delete = options['delete']
        if delete:
            self.stdout.write("Modo: DELETAR arquivos órfãos")
        else:
            self.stdout.write("Modo: DRY-RUN (nada será apagado)")

        if delete and options['dry_run']:
            self.stdout.write(self.style.WARNING('--dry-run ignorado porque --delete foi informado.'))

        valid_paths = set()
        valid_paths.update(
            Publication.objects.filter(cover__isnull=False).exclude(cover='')
            .values_list('cover', flat=True)
        )
        valid_paths.update(
            Page.objects.filter(image__isnull=False).exclude(image='')
            .values_list('image', flat=True)
        )

        settings_obj = WebSettings.objects.first()
        if settings_obj:
            for field in ('logo', 'background', 'background_mobile'):
                value = getattr(settings_obj, field, None)
                if value:
                    valid_paths.add(value)

        valid_paths.update(
            get_user_model().objects.filter(avatar__isnull=False).exclude(avatar='')
            .values_list('avatar', flat=True)
        )

        media_root = settings.MEDIA_ROOT
        if not os.path.isdir(media_root):
            self.stdout.write("Diretório de mídia não encontrado.")
            return

        deleted_count = 0
        kept_count = 0

        for root, dirs, files in os.walk(media_root):
            for filename in sorted(files):
                filepath = os.path.join(root, filename)
                relative = os.path.relpath(filepath, media_root)

                if relative in valid_paths:
                    kept_count += 1
                    continue

                if delete:
                    os.remove(filepath)
                    deleted_count += 1
                    self.stdout.write(f"  DELETED: {relative}")
                else:
                    deleted_count += 1
                    self.stdout.write(f"  ORPHAN: {relative}")

        status = (
            f"\nResultado: {deleted_count} órfãos "
            f"({'removidos' if delete else 'encontrados'}), {kept_count} mantidos"
        )
        self.stdout.write(self.style.SUCCESS(status))