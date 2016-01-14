from rest_framework import serializers
from rest_framework import exceptions
from models import *
import logging
logger = logging.getLogger(__name__)


class ChatroomActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatroomActivityType


class PNAnnouncementSerializer(serializers.ModelSerializer):

    message = serializers.SerializerMethodField()
    chatroom_member = serializers.SerializerMethodField()

    class Meta:
        model = Announcement

    def get_chatroom_member(self, obj):
        return ChatroomMemberBasicSerializer(ChatroomMember.objects.get(chatroom=obj.chatroom, user=obj.user)).data

    def get_message(self, obj):
        # No second-person in push notifications
        text = obj.announcement_type.third_person_text
        return text.replace("|*NAME*|", obj.user.readable_name)


class AnnouncementSerializer(serializers.ModelSerializer):

    message = serializers.SerializerMethodField()

    class Meta:
        model = Announcement

    def get_message(self, obj):
        request = self.context.get('request', None)
        if request.user == obj.user:
            # user second person text
            return obj.announcement_type.second_person_text
        else:
            text = obj.announcement_type.third_person_text
            return text.replace("|*NAME*|", obj.user.readable_name)


class InteractionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interaction
        exclude = ['timestamp']


class PNChatroomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    chatroom_activity_type = ChatroomActivityTypeSerializer()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomActivity

    def get_user_has_liked(self, obj):
        request = self.context.get('request', None)
        try:
            interaction = Interaction.objects.get(user=request.user, chatroom_activity=obj)
            return interaction.has_liked
        except Interaction.DoesNotExist:
            return False

    def get_activity(self, obj):
        if obj.chatroom_activity_type.is_message():
            return BasicMessageSerializer(Message.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_announcement():
            return PNAnnouncementSerializer(Announcement.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_upload():
            return UploadSerializer(Upload.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_study_group():
            from apps.group.serializers import StudyGroupBasicSerializer
            from apps.group.models import StudyGroup
            return StudyGroupBasicSerializer(StudyGroup.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        else:
            return []


class WelcomeMessageChatroomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    chatroom_activity_type = ChatroomActivityTypeSerializer()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomActivity

    def get_user_has_liked(self, obj):
        return False

    def get_activity(self, obj):
        return BasicMessageSerializer(Message.objects.get(pk=obj.activity_id)).data


class ChatroomActivitySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    chatroom_activity_type = ChatroomActivityTypeSerializer()
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomActivity

    def get_user_has_liked(self, obj):
        request = self.context.get('request', None)
        try:
            interaction = Interaction.objects.get(user=request.user, chatroom_activity=obj)
            return interaction.has_liked
        except Interaction.DoesNotExist:
            return False

    def get_activity(self, obj):
        if obj.chatroom_activity_type.is_message():
            return BasicMessageSerializer(Message.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_announcement():
            return AnnouncementSerializer(Announcement.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_upload():
            return UploadSerializer(Upload.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        elif obj.chatroom_activity_type.is_study_group():
            from apps.group.serializers import StudyGroupBasicSerializer
            from apps.group.models import StudyGroup
            return StudyGroupBasicSerializer(StudyGroup.objects.get(pk=obj.activity_id), context={'request': self.context['request']}).data
        else:
            return []


class ChatroomMemberBasicSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomMember
        fields = ['id', 'user', 'chatroom']

    def get_user(self, obj):
        from apps.account.serializers import UserSlimInfoSerializer
        return UserSlimInfoSerializer(obj.user).data


class ChatroomMemberSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ChatroomMember

    def get_user(self, obj):
        from apps.account.serializers import UserSlimInfoSerializer
        return UserSlimInfoSerializer(obj.user).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']


class ChatroomSerializer(serializers.ModelSerializer):
    chatroom_activities = serializers.SerializerMethodField()
    # in the future tags would likely be chatroom-specific so including tags here
    tags = serializers.SerializerMethodField()
    unread_activity_count = serializers.SerializerMethodField()
    first_activity_id = serializers.SerializerMethodField()
    additional_uploads = serializers.SerializerMethodField()
    notifications_enabled = serializers.SerializerMethodField()

    class Meta:
        model = Chatroom

    def get_notifications_enabled(self, obj):
        user = self.context['request'].user
        membership = ChatroomMember.objects.get(chatroom=obj, user=user)
        return membership.notifications_enabled

    def get_first_activity_id(self, obj):
        l = list(ChatroomActivity.objects.filter(chatroom=obj)[:1])
        if l:
            return l[0].pk
        return None

    def get_additional_uploads(self, obj):
        upload_type = ChatroomActivityType.objects.get(identifier='upload')
        activities = list(reversed(obj.get_chatroom_activities()))
        if len(activities) > 0:
            uploads = ChatroomActivity.objects.filter(id__lt=activities[0].pk, chatroom=obj, chatroom_activity_type=upload_type).order_by('-id')[:20]
            return ChatroomActivitySerializer(uploads, many=True, context={'request': self.context['request']}).data
        return []

    def get_unread_activity_count(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            try:
                member = ChatroomMember.objects.get(user=request.user, chatroom=obj)
                return member.unread_activity_count
            except ChatroomMember.DoesNotExist:
                raise exceptions.NotFound("Chatroom " + str(obj.pk) + " member " + str(request.user.pk) + " not found")
        raise exceptions.NotFound("Request not found")

    def get_tags(self, obj):
        return TagSerializer(Tag.objects.all(), many=True).data

    def get_chatroom_activities(self, obj):
        '''
        Limits the number of messages to 50 (editable in Chatroom model)
        '''
        return ChatroomActivitySerializer(obj.get_chatroom_activities(), many=True, context={'request': self.context['request']}).data


class UploadSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    tag = TagSerializer()
    chatroom_member = ChatroomMemberBasicSerializer()

    class Meta:
        model = Upload

    def get_files(self, obj):
        return FileSerializer(File.objects.filter(upload=obj), many=True).data


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File


class BasicMessageSerializer(serializers.ModelSerializer):
    chatroom_member = ChatroomMemberBasicSerializer()

    class Meta:
        model = Message
        fields = ('message', 'chatroom_member', 'id')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
