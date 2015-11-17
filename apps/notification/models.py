from django.db import models

class NotificationType(models.Model):
    identifier = models.CharField(max_length=25)
    title = models.CharField(max_length=250, blank=True, null=True)
    message = models.CharField(max_length=250, blank=True, null=True)
    pn_message = models.CharField(max_length=250, blank=True, null=True)
    is_silent = models.IntegerField()
    priority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'notification_types'

class OpenNotification(models.Model):
    user_id = models.IntegerField()
    data = models.TextField(blank=True, null=True)
    notification_type_id = models.IntegerField()
    notification_vars = models.TextField(blank=True, null=True)
    has_sent = models.IntegerField()
    send_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'open_notifications'
        
class PastNotification(models.Model):
    user_id = models.IntegerField()
    data = models.TextField(blank=True, null=True)
    notification_type_id = models.IntegerField()
    notification_vars = models.TextField(blank=True, null=True)
    has_sent = models.IntegerField()
    send_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_notifications'
