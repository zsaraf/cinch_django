from django.db import models


class CashOutAttempt(models.Model):
    user = models.ForeignKey('account.User')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    successful = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cash_out_attempts'


class AddedOnlineCredit(models.Model):
    user = models.ForeignKey('account.User')
    from_email = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'added_online_credit'


class OutstandingCharge(models.Model):
    past_sesh = models.ForeignKey('tutoring.PastSesh')
    user = models.ForeignKey('account.User')
    amount_owed = models.DecimalField(max_digits=19, decimal_places=4)
    amount_payed = models.DecimalField(max_digits=19, decimal_places=4)
    resolved = models.IntegerField()
    code = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'outstanding_charges'
