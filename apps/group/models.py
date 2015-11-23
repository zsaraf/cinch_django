from django.db import models


# Create your models here.
class CourseGroup(models.Model):
    professor_name = models.CharField(max_length=100)
    course = models.ForeignKey('university.Course')
    timestamp = models.DateTimeField()
    chatroom = models.ForeignKey('chatroom.Chatroom')

    class Meta:
        managed = False
        db_table = 'course_group'


class CourseGroupMember(models.Model):
    student = models.ForeignKey('student.Student')
    course_group = models.ForeignKey('group.CourseGroup')
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course_group_member'


class StudyGroup(models.Model):
    course = models.ForeignKey(CourseGroup)
    timestamp = models.DateTimeField()
    chatroom = models.ForeignKey('chatroom.Chatroom')

    class Meta:
        managed = False
        db_table = 'study_group'


class StudyGroupMember(models.Model):
    user = models.ForeignKey('account.User')
    study_group = models.ForeignKey('group.StudyGroup')
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'study_group_member'
