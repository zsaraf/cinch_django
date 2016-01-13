from django.db import models
import locale
from sesh.mandrill_utils import EmailManager
locale.setlocale(locale.LC_ALL, '')


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
    amount_payed = models.DecimalField(default=0, max_digits=19, decimal_places=4)
    resolved = models.BooleanField(default=False)
    code = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'outstanding_charges'

    def email_user(self, message):
        # notify user of new outstanding charge
        merge_vars = {
            'FULL_LEGAL_NAME': self.user.full_name,
            'CHARGE': locale.currency(self.amount_owed),
            'CONTENT': message
        }
        EmailManager.send_email(EmailManager.PAYMENT_FAILED, merge_vars, self.user.email, self.user.first_name, None, None)
