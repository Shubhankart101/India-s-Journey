"""The local .env loader that supplies OAuth credentials when the app runs on a developer machine."""
import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from journey.settings import load_env_file


class LoadEnvFileTests(TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile('w', suffix='.env', delete=False, encoding='utf-8')
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_reads_keys_and_strips_quotes_comments_and_export(self):
        path = self.write(
            '# comment\n\nGOOGLE_CLIENT_ID=abc.apps.googleusercontent.com\n'
            'export MICROSOFT_CLIENT_SECRET="s3cr=et"\nMICROSOFT_TENANT=\'consumers\'\nnot a pair\n'
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            load_env_file(path)
            self.assertEqual(os.environ['GOOGLE_CLIENT_ID'], 'abc.apps.googleusercontent.com')
            self.assertEqual(os.environ['MICROSOFT_CLIENT_SECRET'], 's3cr=et')
            self.assertEqual(os.environ['MICROSOFT_TENANT'], 'consumers')
            self.assertNotIn('not a pair', os.environ)

    def test_real_environment_variables_take_precedence(self):
        path = self.write('GOOGLE_CLIENT_ID=from-file\n')
        with mock.patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'from-env'}, clear=True):
            load_env_file(path)
            self.assertEqual(os.environ['GOOGLE_CLIENT_ID'], 'from-env')

    def test_missing_file_is_ignored(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            load_env_file(Path(tempfile.gettempdir()) / 'does-not-exist.env')
            self.assertEqual(dict(os.environ), {})

    def test_byte_order_mark_from_windows_editors_is_ignored(self):
        path = self.write('\ufeffGOOGLE_CLIENT_ID=bom-safe\n')
        with mock.patch.dict(os.environ, {}, clear=True):
            load_env_file(path)
            self.assertEqual(os.environ['GOOGLE_CLIENT_ID'], 'bom-safe')
