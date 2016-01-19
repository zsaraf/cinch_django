from django.db import models
from datetime import datetime
from json import dumps


class OpenNotificationManager(models.Manager):

    def send_refresh(self, user):
        from apps.notification.models import NotificationType
        refresh_type = NotificationType.objects.get(identifier="REFRESH_NOTIFICATIONS")
        self.model.objects.filter(notification_type=refresh_type, user=user).delete()
        self.model.objects.create(user, refresh_type, None, None, None)

    def create(self, to_user, notification_type, data, merge_vars, send_time):

        if not to_user.notifications_enabled:
            return None

        if not send_time:
            send_time = datetime.now()

        new_notification = self.model(
            user=to_user,
            data=dumps(data),
            notification_type=notification_type,
            notification_vars=dumps(merge_vars),
            has_sent=False,
            send_time=send_time
        )
        new_notification.save()
        return new_notification
