from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_socialmedia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='websettings',
            name='twitter_url',
        ),
    ]
