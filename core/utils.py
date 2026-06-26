import os
import uuid

from django.utils import timezone


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