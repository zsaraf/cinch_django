from django.db import models
from .models import OpenNotification


class OpenNotificationManager(models.Manager):

    def create(self, to_user,  data, merge_vars, send_time):
        