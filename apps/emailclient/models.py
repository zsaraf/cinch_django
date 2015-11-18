from django.db import models


class PendingEmail(models.Model):
    user = models.ForeignKey('account.User')
    category = models.IntegerField()
    tag = models.CharField(max_length=75)
    template_name = models.CharField(max_length=75)
    merge_vars = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_emails'
