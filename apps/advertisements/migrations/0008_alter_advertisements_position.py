from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advertisements', '0007_alter_advertisements_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisements',
            name='position',
            field=models.CharField(blank=True, choices=[('banner', 'Carrossel de banners'), ('card', 'Card de publicações'), ('left', 'Lateral esquerda (Desktop)'), ('right', 'Lateral direita (Desktop)'), ('preview', 'Reader preview (Desktop)'), ('mobile', 'Reader preview (Mobile)'), ('footer', 'Acima do footer (Desktop)'), ('footer_mobile', 'Acima do footer (Mobile)')], help_text='Não necessário para SocialBar e SmartLink', max_length=20, verbose_name='Posição'),
        ),
    ]
