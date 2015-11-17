from django.db import models

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

class PendingTutorClass(models.Model):
    class_id = models.IntegerField()
    pending_tutor_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'pending_tutor_classes'

class PendingTutor(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    school_id = models.IntegerField()
    ready_to_publish = models.IntegerField()
    major = models.CharField(max_length=100)
    class_year = models.CharField(max_length=25)
    verification_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'pending_tutors'

class TutorClass(models.Model):
    tutor_id = models.IntegerField()
    class_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_classes'

class TutorDepartment(models.Model):
    tutor_id = models.IntegerField()
    department_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tutor_departments'
        
class Tutor(models.Model):
    user_id = models.IntegerField()
    enabled = models.IntegerField()
    num_seshes = models.IntegerField()
    ave_rating_1 = models.FloatField()
    ave_rating_2 = models.FloatField()
    ave_rating_3 = models.FloatField()
    credits = models.DecimalField(max_digits=19, decimal_places=4)
    did_accept_terms = models.IntegerField()
    bonus_points = models.FloatField()

    class Meta:
        managed = False
        db_table = 'tutors'
        
class TutorSignup(models.Model):
    email = models.CharField(max_length=100)
    school_id = models.IntegerField()
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

