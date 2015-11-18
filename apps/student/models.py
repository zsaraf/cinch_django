from django.db import models

class Favorite(models.Model):
    student_id = models.IntegerField(blank=True, null=True)
    tutor_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'favorites'

class Student(models.Model):
    user = models.OneToOneField('account.User')
    credits = models.DecimalField(max_digits=19, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'students'
        
class StudentCourse(models.Model):
    student = models.ForeignKey(Student)
    course_group = models.ForeignKey('group.CourseGroup')
    timestamp = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'student_courses'