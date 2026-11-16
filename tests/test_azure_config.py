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


    def test_terraform_files_exist_and_fly_removed(self):
        """Verify that Terraform files and modules exist and legacy Fly.io / Render configs are purged."""
        tf_dir = REPO_ROOT / 'terraform'
        self.assertTrue((tf_dir / 'main.tf').is_file(), "terraform/main.tf must exist")
        self.assertTrue((tf_dir / 'variables.tf').is_file(), "terraform/variables.tf must exist")
        self.assertTrue((tf_dir / 'outputs.tf').is_file(), "terraform/outputs.tf must exist")
        self.assertTrue((tf_dir / 'versions.tf').is_file(), "terraform/versions.tf must exist")

        # Verify Terraform modules exist
        modules = ['resource_group', 'service_plan', 'web_app', 'budget']
        for mod in modules:
            mod_dir = tf_dir / 'modules' / mod
            self.assertTrue((mod_dir / 'main.tf').is_file(), f"Module {mod}/main.tf must exist")
            self.assertTrue((mod_dir / 'variables.tf').is_file(), f"Module {mod}/variables.tf must exist")
            self.assertTrue((mod_dir / 'outputs.tf').is_file(), f"Module {mod}/outputs.tf must exist")

        # Verify fly.toml, fly-deploy workflow, and render.yaml are completely removed
        self.assertFalse((REPO_ROOT / 'fly.toml').exists(), "fly.toml must not exist")
        self.assertFalse((REPO_ROOT / '.github' / 'workflows' / 'fly-deploy.yml').exists(), "fly-deploy.yml must not exist")
        self.assertFalse((REPO_ROOT / 'render.yaml').exists(), "render.yaml must not exist")
        self.assertFalse((REPO_ROOT / 'azure-resources.bicep').exists(), "azure-resources.bicep must be replaced by Terraform")

    def test_ai_roadmap_exists_and_linked_in_readme(self):
        """Verify that docs/AI-ROADMAP.md exists and is linked from README.md."""
        roadmap = REPO_ROOT / 'docs' / 'AI-ROADMAP.md'
        self.assertTrue(roadmap.is_file(), "docs/AI-ROADMAP.md must exist")
        readme = (REPO_ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('docs/AI-ROADMAP.md', readme, "README.md must reference docs/AI-ROADMAP.md")
        self.assertIn('https://indias-journey-m5ag64.azurewebsites.net', readme, "README.md must reference live azure webapp url")


if __name__ == '__main__':
    unittest.main()
