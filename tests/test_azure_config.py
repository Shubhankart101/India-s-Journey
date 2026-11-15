import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEBAPP_DIR = REPO_ROOT / 'webapp'
if str(WEBAPP_DIR) not in sys.path:
    sys.path.insert(0, str(WEBAPP_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'journey.settings')


class TestAzureConfiguration(unittest.TestCase):
    def test_azure_host_and_csrf_support(self):
        """Verify that Azure hostnames and origins are dynamically trusted."""
        from journey import settings

        self.assertIn('.azurewebsites.net', settings.ALLOWED_HOSTS or [])
        self.assertIn('.azurecontainerapps.io', settings.ALLOWED_HOSTS or [])
        self.assertTrue(
            any('azurewebsites.net' in origin for origin in settings.CSRF_TRUSTED_ORIGINS),
            "Expected wildcard or Azure origin in CSRF_TRUSTED_ORIGINS"
        )

    def test_sqlite_wal_signal_registered(self):
        """Verify that SQLite connection signals are properly imported and ready."""
        from indicators.apps import enable_sqlite_wal
        self.assertTrue(callable(enable_sqlite_wal))

    def test_gunicorn_config_exists_and_parses(self):
        """Verify webapp/gunicorn.conf.py is valid python."""
        config_path = WEBAPP_DIR / 'gunicorn.conf.py'
        self.assertTrue(config_path.exists(), "gunicorn.conf.py must exist")
        namespace = {}
        with open(config_path, 'r', encoding='utf-8') as f:
            code = compile(f.read(), str(config_path), 'exec')
            exec(code, namespace)
        self.assertIn('bind', namespace)
        self.assertIn('workers', namespace)
        self.assertIn('worker_class', namespace)
        self.assertEqual(namespace['worker_class'], 'gthread')


if __name__ == '__main__':
    unittest.main()
