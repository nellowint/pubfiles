import django.db.models.deletion
from django.db import migrations, models


def migrate_twitter_url(apps, schema_editor):
    WebSettings = apps.get_model('website', 'WebSettings')
    SocialMedia = apps.get_model('website', 'SocialMedia')
    for ws in WebSettings.objects.all():
        if getattr(ws, 'twitter_url', ''):
            url = ws.twitter_url.strip()
            if url and not SocialMedia.objects.filter(website=ws, url=url).exists():
                SocialMedia.objects.create(website=ws, platform='x', url=url, order=0, is_active=True)


def reverse_migrate_twitter_url(apps, schema_editor):
    SocialMedia = apps.get_model('website', 'SocialMedia')
    SocialMedia.objects.filter(platform='x').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0016_websettings_twitter_url_alter_banner_advertisement'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('x', 'X / Twitter'), ('instagram', 'Instagram'), ('facebook', 'Facebook'), ('tiktok', 'TikTok'), ('youtube', 'YouTube')], max_length=20, verbose_name='Plataforma')),
                ('url', models.URLField(help_text='URL completa do perfil', verbose_name='URL')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Ordem')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_media', to='website.websettings', verbose_name='Website')),
            ],
            options={
                'verbose_name': 'Rede social',
                'verbose_name_plural': 'Redes sociais',
                'ordering': ['order'],
            },
        ),
        migrations.RunPython(migrate_twitter_url, reverse_migrate_twitter_url),
    ]
