import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0008_alter_advertisements_position'),
        ('website', '0015_websettings_seo_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='websettings',
            name='twitter_url',
            field=models.URLField(blank=True, help_text='URL completa do perfil. Ex: https://x.com/seuperfil ou https://twitter.com/seuperfil', verbose_name='Twitter / X'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='advertisement',
            field=models.ForeignKey(blank=True, help_text='Torna a imagem do banner clicável, redirecionando para o link. Apenas SmartLink.', limit_choices_to={'is_active': True, 'type': 'smart_link'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banners', to='advertisements.advertisements', verbose_name='Anúncio'),
        ),
    ]
