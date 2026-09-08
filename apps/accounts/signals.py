from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import User


@receiver(pre_delete, sender=User)
def delete_user_avatar(sender, instance, **kwargs):
    # Remove o avatar do disco ao excluir a conta
    if instance.avatar:
        instance.avatar.delete(save=False)
