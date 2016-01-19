from django.db import models
from apps.chatroom.models import ChatroomMember
from apps.notification.models import OpenNotification, NotificationType, PastNotification
import json


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey('Conversation')
    user = models.ForeignKey('account.User')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'conversation_participant'


class Conversation(models.Model):
    chatroom = models.ForeignKey('chatroom.Chatroom', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'conversation'

    def send_new_conversation_notification(self, user, request):
        '''
        Sends a notification to the other member that a new convo has started
        '''
        from serializers import ConversationSerializer

        convo_members = ConversationParticipant.objects.filter(conversation=self).exclude(user=user)
        merge_vars = {}
        notification_type = NotificationType.objects.get(identifier="CONVERSATION_CREATED")
        for cm in convo_members:
            data = {
                "conversation": ConversationSerializer(self, context={'request': request, 'context_user': cm.user}).data,
                'chatroom_id': self.chatroom.id
            }
            OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)


class CourseGroup(models.Model):
    professor_name = models.CharField(max_length=100)
    course = models.ForeignKey('university.Course')
    timestamp = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey('chatroom.Chatroom')
    is_past = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'course_group'

    def send_new_member_notification(self, user, request):
        '''
        Sends a notification to the chatroom members that the group has a new member
        '''
        from apps.chatroom.serializers import ChatroomMemberSerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=user)
        merge_vars = {
            "NEW_USER_NAME": user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        notification_type = NotificationType.objects.get(identifier="NEW_GROUP_MEMBER_COURSE_GROUP")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                data = {
                    "chatroom_member": ChatroomMemberSerializer(cm, context={'request': request}).data,
                    'chatroom_id': self.chatroom.id
                }
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_study_group_notification(self, user, chatroom_activity, request):
        '''
        Sends a notification to the chatroom members that the group has a new member
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=user)
        merge_vars = {
            "CREATOR_NAME": user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }

        data = chatroom_activity.get_pn_data(request)

        notification_type = NotificationType.objects.get(identifier="STUDY_GROUP_CREATED")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)


class CourseGroupMember(models.Model):
    student = models.ForeignKey('student.Student')
    course_group = models.ForeignKey('group.CourseGroup')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_past = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'course_group_member'


class StudyGroup(models.Model):
    course_group = models.ForeignKey(CourseGroup)
    timestamp = models.DateTimeField(auto_now_add=True)
    chatroom = models.ForeignKey('chatroom.Chatroom')
    user = models.ForeignKey('account.User', db_column='creator_user_id')
    is_past = models.BooleanField(default=False)
    topic = models.CharField(max_length=500)
    location = models.CharField(max_length=250)
    num_people = models.IntegerField()
    time = models.DateTimeField()
    is_full = models.BooleanField(default=False)

    def send_owner_changed_notification(self, request):
        '''
        Sends a notification to the chatroom members that the group has a new leader
        '''
        from apps.chatroom.serializers import ChatroomMemberSerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=self.user)
        merge_vars = {
            "NEW_CREATOR_NAME": self.user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        notification_type = NotificationType.objects.get(identifier="NEW_GROUP_OWNER")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                data = {
                    "chatroom_member": ChatroomMemberSerializer(cm, context={'request': request}).data,
                    'chatroom_id': self.chatroom.id
                }
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_group_edited_notification(self, request):
        '''
        Sends a notification to the chatroom members that the group has ended
        '''

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=self.user)
        merge_vars = {
            "CREATOR_NAME": self.user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = {
            'chatroom_id': self.chatroom.id
        }
        notification_type = NotificationType.objects.get(identifier="STUDY_GROUP_EDITED")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_group_ended_notification(self):
        '''
        Sends a notification to the chatroom members that the group has ended
        '''
        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=self.user)
        merge_vars = {
            "CREATOR_NAME": self.user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }
        data = {
        }
        notification_type = NotificationType.objects.get(identifier="STUDY_GROUP_ENDED")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                OpenNotification.clear_by_user_and_chatroom(cm.user, self.chatroom)
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    def send_new_member_notification(self, new_user, request):
        '''
        Sends a notification to the chatroom members that a new member joined
        '''
        from apps.chatroom.serializers import ChatroomMemberSerializer

        chatroom_members = ChatroomMember.objects.filter(chatroom=self.chatroom, is_past=False).exclude(user=new_user)
        merge_vars = {
            "NEW_USER_NAME": new_user.readable_name,
            "CHATROOM_NAME": self.chatroom.name
        }

        notification_type = NotificationType.objects.get(identifier="NEW_GROUP_MEMBER_STUDY_GROUP")
        for cm in chatroom_members:
            if cm.notifications_enabled:
                data = {
                    "chatroom_member": ChatroomMemberSerializer(cm, context={'request': request}).data,
                    'chatroom_id': self.chatroom.id
                }
                OpenNotification.objects.create(cm.user, notification_type, data, merge_vars, None)

    class Meta:
        managed = False
        db_table = 'study_group'


class StudyGroupMember(models.Model):
    user = models.ForeignKey('account.User')
    study_group = models.ForeignKey('group.StudyGroup')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_past = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'study_group_member'
