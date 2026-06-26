
from django.db import models
from django.core.exceptions import ValidationError

from core.utils import MediaPath


class WebSettings(models.Model):
    title = models.CharField(
        max_length=100,
        default='Site',
        verbose_name='Website title'
    )
    logo = models.ImageField(
        upload_to=MediaPath('website/logo'),
        verbose_name='Website logo',
        blank=True,
        null=True
    )
    background = models.ImageField(
        upload_to=MediaPath('website/background'),
        verbose_name='Website background',
        blank=True,
        null=True
    )
    background_mobile = models.ImageField(
        upload_to=MediaPath('website/background'),
        verbose_name='Website background (mobile)',
        help_text='Background used only on mobile devices. Falls back to the main background if empty.',
        blank=True,
        null=True
    )
    light_theme_primary = models.CharField(
        max_length=7,
        default="#FFFFFF",
        verbose_name="Primary Background Color (Light Theme)",
        help_text="Example: #FFFFFF"
    )
    light_theme_secondary = models.CharField(
        max_length=7,
        default="#F8F9FA",
        verbose_name="Secondary Background Color (Light Theme)",
        help_text='Example: #F8F9FA'
    )
    dark_theme_primary = models.CharField(
        max_length=7,
        default="#121212",
        verbose_name="Primary Background Color (Dark Theme)",
        help_text="Example: #121212"
    )
    dark_theme_secondary = models.CharField(
        max_length=7,
        default="#1A1A1A",
        verbose_name="Secondary Background Color (Dark Theme)",
        help_text='Example: #1A1A1A'
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return f"Site Settings: {self.title}"

    def clean(self):
        if WebSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("A configuration already exists. Edit the existing record.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
