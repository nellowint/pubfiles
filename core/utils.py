import os
import uuid

from django.core.exceptions import ValidationError
from django.utils import timezone


FILE_SIZE_LIMIT_MB = 1


def validate_file_size(value):
    limit = FILE_SIZE_LIMIT_MB * 1024 * 1024
    if value.size > limit:
        raise ValidationError(
            f'Arquivo muito grande. Tamanho máximo permitido: {FILE_SIZE_LIMIT_MB} MB.'
        )


class MediaPath:
    def __init__(self, base):
        self.base = base

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1].lower()
        date_path = timezone.now().strftime('%Y/%m')
        return os.path.join(self.base, date_path, f'{uuid.uuid4().hex}.{ext}')

    def __eq__(self, other):
        return isinstance(other, MediaPath) and self.base == other.base

    def deconstruct(self):
        return ('core.utils.MediaPath', [self.base], {})