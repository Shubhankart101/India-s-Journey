from django.apps import AppConfig
from django.db.backends.signals import connection_created


def enable_sqlite_wal(sender, connection, **kwargs):
    if connection.vendor == 'sqlite3' or connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA journal_mode = WAL;')
            cursor.execute('PRAGMA busy_timeout = 5000;')
            cursor.execute('PRAGMA synchronous = NORMAL;')


class IndicatorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'indicators'
    verbose_name = 'Indicators and articles'

    def ready(self):
        connection_created.connect(enable_sqlite_wal)
