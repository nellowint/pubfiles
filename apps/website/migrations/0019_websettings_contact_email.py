from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0018_remove_websettings_twitter_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='websettings',
            name='contact_email',
            field=models.EmailField(blank=True, help_text='Exibido na página de contato', max_length=254, verbose_name='E-mail de contato'),
        ),
    ]
