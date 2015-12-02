from django.db import models
from apps.chatroom.models import ChatroomMember
from apps.notification.models import OpenNotification, NotificationType


# Create your models here.
class CourseGroup(models.Model):
    professor_name = models.CharField(max_length=100)
    course = models.ForeignKey('university.Course')
    timestamp = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey('chatroom.Chatroom')

    def send_study_group_notification(self, creator):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=creator)
        data = {
            "CREATOR_NAME": creator.readable_name,
            "CLASS_NAME": self.course.get_readable_name()
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "study_group_id": self.id
        }
        notification_type = NotificationType.objects.get(identifier="STUDY_GROUP_CREATED")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_new_member_notification(self, new_user):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=new_user)
        data = {
            "NEW_USER_NAME": new_user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "new_user_id": new_user.id
        }
        notification_type = NotificationType.objects.get(identifier="NEW_GROUP_MEMBER")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'course_group'


class CourseGroupMember(models.Model):
    student = models.ForeignKey('student.Student')
    course_group = models.ForeignKey('group.CourseGroup')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'course_group_member'


class StudyGroup(models.Model):
    course_group = models.ForeignKey(CourseGroup)
    timestamp = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey('chatroom.Chatroom')
    user = models.ForeignKey('account.User', db_column='creator_user_id')

    def send_new_member_notification(self, new_user):
        '''
        Sends a notification to the chatroom members
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom).exclude(user=new_user)
        data = {
            "NEW_USER_NAME": new_user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        merge_vars = {
            "chatroom_id": self.chatroom.id,
            "new_user_id": new_user.id
        }
        notification_type = NotificationType.objects.get(identifier="NEW_GROUP_MEMBER")
        for cm in chatroom_members:
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'study_group'


class StudyGroupMember(models.Model):
    user = models.ForeignKey('account.User')
    study_group = models.ForeignKey('group.StudyGroup')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'study_group_member'
