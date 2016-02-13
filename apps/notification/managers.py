from django.db import models
from datetime import datetime
import json


class OpenNotificationManager(models.Manager):

    def clear_by_user_chatroom_and_type(self, user, chatroom, types):
        from apps.notification.models import PastNotification
        notifications = self.model.objects.filter(user=user, notification_type__in=types)
        for n in notifications:
            try:
                json_arr = json.loads(n.data)
                chatroom_id = json_arr.get('chatroom_id')
                if chatroom_id == chatroom.pk:
                    PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
                    self.model.objects.get(pk=n.pk).delete()
            except:
                continue

        self.send_refresh(user)

    def clear_by_user_and_chatroom(self, user, chatroom):
        from apps.notification.models import PastNotification
        notifications = self.model.objects.filter(user=user)
        for n in notifications:
            try:
                json_arr = json.loads(n.data)
                chatroom_id = json_arr.get('chatroom_id')
                if chatroom_id == chatroom.pk:
                    PastNotification.objects.create(data=n.data, user_id=n.user.pk, notification_type=n.notification_type, notification_vars=n.notification_vars, has_sent=n.has_sent, send_time=n.send_time)
                    self.model.objects.get(pk=n.pk).delete()
            except:
                continue

        self.send_refresh(user)

    def send_badge_update(self, user):
        from apps.notification.models import NotificationType
        badge_type = NotificationType.objects.get(identifier="UPDATE_BADGE_NUMBER")
        self.model.objects.filter(notification_type=badge_type, user=user).delete()
        self.model.objects.create(user, badge_type, None, None, None)

    def send_refresh(self, user):
        from apps.notification.models import NotificationType
        refresh_type = NotificationType.objects.get(identifier="REFRESH_NOTIFICATIONS")
        self.model.objects.filter(notification_type=refresh_type, user=user).delete()
        self.model.objects.create(user, refresh_type, None, None, None)

    def create(self, to_user, notification_type, data, merge_vars, send_time, notifications_enabled=True, has_sent=False):

        if not send_time:
            send_time = datetime.now()

        muted = not notifications_enabled

        new_notification = self.model(
            user=to_user,
            data=json.dumps(data),
            notification_type=notification_type,
            notification_vars=json.dumps(merge_vars),
            has_sent=has_sent,
            send_time=send_time,
            muted=muted
        )
        new_notification.save()
        return new_notification
