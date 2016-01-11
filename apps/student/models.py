from django.db import models
from .managers import StudentManager


class Favorite(models.Model):
    student = models.ForeignKey('student.Student', blank=True, null=True)
    tutor = models.ForeignKey('tutor.Tutor', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'favorites'


class Student(models.Model):
    user = models.OneToOneField('account.User')
    credits = models.DecimalField(max_digits=19, decimal_places=4)
    objects = StudentManager()

    class Meta:
        managed = False
        db_table = 'students'

    @property
    def stats(self):
        # Get total hours learned
        hours_learned = 0.0
        for past_sesh in self.pastsesh_set.all():
            hours_learned += past_sesh.duration()

        # Create stats dict
        stats = {}
        stats['hours_learned'] = hours_learned
        stats['credits'] = self.credits

        return stats
