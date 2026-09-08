from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_category_slug'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['tree_id', 'lft'], name='categories_category_tree_i79f7'),
        ),
    ]
