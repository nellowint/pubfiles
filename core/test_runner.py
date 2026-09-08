import shutil
import tempfile

from django.conf import settings
from django.core.files.storage import default_storage
from django.test.runner import DiscoverRunner


class PubfilesTestRunner(DiscoverRunner):
    # Isola MEDIA_ROOT em um diretório temporário durante os testes para não
    # deixar arquivos órfãos na pasta media/ real (uploads de teste são apagados).
    def setup_test_environment(self, **kwargs):
        self._orig_media_root = settings.MEDIA_ROOT
        self._tmp_media_root = tempfile.mkdtemp(prefix='pubfiles_test_media_')
        settings.MEDIA_ROOT = self._tmp_media_root
        default_storage.location = self._tmp_media_root
        super().setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        super().teardown_test_environment(**kwargs)
        settings.MEDIA_ROOT = self._orig_media_root
        default_storage.location = self._orig_media_root
        shutil.rmtree(self._tmp_media_root, ignore_errors=True)
