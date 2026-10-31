import shutil
import subprocess
import sys

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

COLLECTORS = [
    'scripts/collect_substack.py',
    'scripts/collect_indian_matrix.py',
    'scripts/collect_us_campaign_finance.py',
    'scripts/generate_public_charts.py',
]


class Command(BaseCommand):
    help = 'Runs the public-data pipelines, re-exports the catalogue and imports it (used by the scheduled cron job).'

    def add_arguments(self, parser):
        parser.add_argument('--skip-collect', action='store_true', help='Skip the Python data collectors.')
        parser.add_argument('--skip-export', action='store_true', help='Skip the Node catalogue export.')
        parser.add_argument('--strict', action='store_true', help='Fail when any collector fails.')

    def _run(self, command):
        self.stdout.write(f'$ {" ".join(command)}')
        return subprocess.run(command, cwd=settings.REPO_ROOT, check=False).returncode

    def handle(self, *args, **options):
        failures = []
        if not options['skip_collect']:
            for script in COLLECTORS:
                if self._run([sys.executable, script]) != 0:
                    failures.append(script)
        if failures and options['strict']:
            raise CommandError(f'Collectors failed: {", ".join(failures)}')
        if not options['skip_export']:
            node = shutil.which('node')
            if not node:
                raise CommandError('Node.js is required to export the catalogue.')
            if self._run([node, 'scripts/export_catalog.mjs']) != 0:
                raise CommandError('Catalogue export failed.')
        call_command('import_catalog', stdout=self.stdout)
        if failures:
            self.stdout.write(self.style.WARNING(f'Some collectors failed and kept their previous data: {", ".join(failures)}'))
