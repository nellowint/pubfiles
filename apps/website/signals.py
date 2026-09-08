from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from .models import Banner, WebSettings

# Campos de imagem de WebSettings e Banner — substituição/apagamento removem do disco
WEBSETTINGS_IMAGE_FIELDS = ('logo', 'background', 'background_mobile')
BANNER_IMAGE_FIELDS = ('image', 'image_mobile')


def _old_media_paths(instance, fields):
    # captura os arquivos atuais no banco antes do save (para remover os substituídos)
    if not instance.pk:
        return {}
    try:
        old = type(instance).objects.filter(pk=instance.pk).values(*fields).first()
    except Exception:
        return {}
    return old or {}


def _cleanup_replaced_media(instance, fields):
    previous = getattr(instance, '_old_media_paths', {})
    if not previous:
        return
    for field in fields:
        old_name = previous.get(field)
        if not old_name:
            continue
        current = getattr(instance, field)
        current_name = getattr(current, 'name', '') if current else ''
        if old_name and old_name != current_name:
            storage = instance._meta.get_field(field).storage
            try:
                if storage.exists(old_name):
                    storage.delete(old_name)
            except Exception:
                pass


@receiver(pre_delete, sender=Banner)
def delete_banner_media(sender, instance, **kwargs):
    for field in BANNER_IMAGE_FIELDS:
        media = getattr(instance, field, None)
        if media:
            media.delete(save=False)


@receiver(pre_save, sender=WebSettings)
def store_old_websettings_media(sender, instance, **kwargs):
    instance._old_media_paths = _old_media_paths(instance, WEBSETTINGS_IMAGE_FIELDS)


@receiver(post_save, sender=WebSettings)
def cleanup_websettings_media(sender, instance, **kwargs):
    _cleanup_replaced_media(instance, WEBSETTINGS_IMAGE_FIELDS)
    instance._old_media_paths = {}


@receiver(pre_save, sender=Banner)
def store_old_banner_media(sender, instance, **kwargs):
    instance._old_media_paths = _old_media_paths(instance, BANNER_IMAGE_FIELDS)


@receiver(post_save, sender=Banner)
def cleanup_banner_media(sender, instance, **kwargs):
    _cleanup_replaced_media(instance, BANNER_IMAGE_FIELDS)
    instance._old_media_paths = {}
