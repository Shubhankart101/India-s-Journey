def backup_links(request):
    from django.conf import settings

    return {'backup_url': settings.BACKUP_SITE_URL, 'backup_status_url': settings.BACKUP_STATUS_URL}
