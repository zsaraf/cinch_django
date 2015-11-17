from django.db import models

# Create your models here.
class OpenBid(models.Model):
    request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()
    tutor_latitude = models.FloatField(blank=True, null=True)
    tutor_longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_bids'

class OpenRequest(models.Model):
    student_id = models.IntegerField()
    school_id = models.IntegerField()
    class_id = models.IntegerField()
    description = models.CharField(max_length=100)
    processing = models.IntegerField()
    timestamp = models.DateTimeField()
    est_time = models.IntegerField()
    num_people = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    expiration_time = models.DateTimeField()
    is_instant = models.IntegerField()
    available_blocks = models.TextField()
    location_notes = models.CharField(max_length=32)
    discount_id = models.IntegerField(blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'open_requests'

class OpenSesh(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()
    start_time = models.DateTimeField(blank=True, null=True)
    has_started = models.IntegerField()
    student_id = models.IntegerField()
    tutor_longitude = models.FloatField(blank=True, null=True)
    tutor_latitude = models.FloatField(blank=True, null=True)
    set_time = models.DateTimeField(blank=True, null=True)
    is_instant = models.IntegerField()
    location_notes = models.CharField(max_length=32)
    has_received_start_time_approaching_reminder = models.IntegerField(blank=True, null=True)
    has_received_set_start_time_initial_reminder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_seshes'
        
class PastBid(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'past_bids'

class PastRequest(models.Model):
    student_id = models.IntegerField()
    class_id = models.IntegerField()
    school_id = models.IntegerField()
    description = models.CharField(max_length=100)
    time = models.DateTimeField()
    num_people = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    est_time = models.IntegerField()
    status = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=19, decimal_places=4)
    available_blocks = models.TextField()
    is_instant = models.IntegerField()
    expiration_time = models.DateTimeField()
    has_seen = models.IntegerField()
    discount_id = models.IntegerField(blank=True, null=True)
    cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
    sesh_comp = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'past_requests'

class PastSesh(models.Model):
    past_request_id = models.IntegerField()
    tutor_id = models.IntegerField()
    student_id = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField()
    student_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    tutor_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    sesh_credits_applied = models.DecimalField(max_digits=19, decimal_places=4)
    rating_1 = models.IntegerField()
    rating_2 = models.IntegerField()
    rating_3 = models.IntegerField()
    charge_id = models.CharField(max_length=100)
    tutor_percentage = models.FloatField()
    tutor_earnings = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    student_cancelled = models.IntegerField()
    tutor_cancelled = models.IntegerField()
    was_cancelled = models.IntegerField()
    cancellation_reason = models.CharField(max_length=30, blank=True, null=True)
    cancellation_charge = models.IntegerField()
    set_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'past_seshes'
        
class ReportedProblem(models.Model):
    past_sesh_id = models.IntegerField(blank=True, null=True)
    content = models.CharField(max_length=512, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reported_problems'