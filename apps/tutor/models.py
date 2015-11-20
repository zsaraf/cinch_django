from django.db import models
from apps.account.models import User
from rest_framework import exceptions
from datetime import datetime


class OpenTutorPromo(models.Model):
    old_user_id = models.IntegerField()
    tutor_email = models.CharField(max_length=100)
    old_user_award = models.DecimalField(max_digits=19, decimal_places=4)
    new_tutor_award = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()
    tutor_added_classes = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_tutor_promos'


class PastTutorPromo(models.Model):
    old_user_id = models.IntegerField()
    tutor_user_id = models.IntegerField()
    old_user_award = models.DecimalField(max_digits=19, decimal_places=4)
    new_tutor_award = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_tutor_promos'


class PendingTutor(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    school = models.ForeignKey('university.School')
    ready_to_publish = models.IntegerField()
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25)
    verification_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    def make_real_tutor(self):
        try:
            user = User.objects.get(email=self.email)
        except User.NotFound:
            raise exceptions.NotFound("User couldn't be found for the pending tutor.")

        # Update the user to reflect tutor information
        user.major = self.major
        user.class_year = self.class_year
        user.tutor.enabled = True
        user.save()
        user.tutor.save()

        # Update the pending tutor classes
        qs = PendingTutorClass.objects.filter(pending_tutor=self)

        for ptc in qs:
            tc = TutorCourse.objects.create(tutor=user.tutor, course=ptc.course)
            tc.save()
            ptc.delete()

        self.delete()

    class Meta:
        managed = False
        db_table = 'pending_tutors'


class PendingTutorClass(models.Model):
    course = models.ForeignKey('university.Course', db_column='class_id')
    pending_tutor = models.ForeignKey(PendingTutor)

    class Meta:
        managed = False
        db_table = 'pending_tutor_classes'


class TutorDepartment(models.Model):
    tutor = models.ForeignKey('tutor.Tutor')
    department = models.ForeignKey('university.Department')
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_departments'


class Tutor(models.Model):
    user = models.OneToOneField('account.User')
    enabled = models.IntegerField()
    num_seshes = models.IntegerField()
    ave_rating_1 = models.FloatField()
    ave_rating_2 = models.FloatField()
    ave_rating_3 = models.FloatField()
    credits = models.DecimalField(max_digits=19, decimal_places=4)
    did_accept_terms = models.IntegerField()
    bonus_points = models.FloatField()

    def check_if_pending(self):
        # Check if the tutor is already enabled
        if self.enabled:
            # Delete any pending tutors if there are any
            PendingTutor.objects.filter(email=self.user.email).delete()
            return

        # See if the tutor has any pending tutor rows
        qs = PendingTutor.objects.filter(email=self.user.email)
        if not qs.exists():
            return

        # Get the actual pending tutor
        pt = qs[0]
        if pt.ready_to_publish:
            pt.make_real_tutor()

    class Meta:
        managed = False
        db_table = 'tutors'


class TutorCourse(models.Model):
    tutor = models.ForeignKey(Tutor)
    course = models.ForeignKey('university.Course', db_column='class_id')
    timestamp = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        managed = False
        db_table = 'tutor_classes'


class TutorSignup(models.Model):
    email = models.CharField(max_length=100)
    school = models.ForeignKey('university.School')
    timestamp = models.DateTimeField()
    recruiter = models.CharField(max_length=250, blank=True, null=True)
    reason = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_signups'


class TutorTier(models.Model):
    identifier = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    sesh_prereq = models.IntegerField()
    bonus_amount = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tutor_tiers'
