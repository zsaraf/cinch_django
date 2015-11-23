from django.db import models
from datetime import datetime
from json import dumps


class OpenNotificationManager(models.Manager):

    def create(self, to_user, notification_type, data, merge_vars, send_time):

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
