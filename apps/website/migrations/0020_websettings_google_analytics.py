from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0019_websettings_contact_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='websettings',
            name='google_analytics',
            field=models.TextField(blank=True, help_text='Cole o script completo do Google Analytics (gtag.js). Deixe vazio para desativar.', verbose_name='Google Analytics'),
        ),
    ]
