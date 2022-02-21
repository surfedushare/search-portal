import pymsteams

from django.conf import settings


def send_admin_notification(text, admin_path=None, build_only=False):
    if not settings.SEND_ADMIN_NOTIFICATIONS:
        return
    notification = pymsteams.connectorcard(settings.TEAMS_HARVESTER_WEBHOOK)
    notification.text(text)
    if admin_path:
        admin_url = f"{settings.PROTOCOL}://{settings.DOMAIN}" + admin_path
        notification.addLinkButton("go to admin", admin_url)
    if not build_only:
        notification.send()
    return notification
