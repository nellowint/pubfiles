from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Page, Publication


@receiver(pre_delete, sender=Publication)
def delete_publication_media(sender, instance, **kwargs):
    if instance.cover:
        instance.cover.delete(save=False)


@receiver(pre_delete, sender=Page)
def delete_page_media(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
