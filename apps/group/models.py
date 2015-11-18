from django.db import models
from apps.university.models import Course


# Create your models here.
class CourseGroup(models.Model):
    professor_name = models.CharField(max_length=100)
    course = models.ForeignKey(Course)
    timestamp = models.DateTimeField()
    open_chatroom = models.ForeignKey('chatroom.OpenChatroom')

    class Meta:
        managed = False
        db_table = 'course_groups'
