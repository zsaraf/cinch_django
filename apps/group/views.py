from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from apps.university.models import Course
from apps.student.models import Student
from apps.chatroom.models import Chatroom, Announcement, AnnouncementType
from apps.account.serializers import UserRegularInfoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from datetime import datetime
from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
from apps.chatroom.serializers import ChatroomActivitySerializer
import logging
import locale
locale.setlocale(locale.LC_ALL, '')
logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request):
        '''
        Begin a conversation
        '''
        from apps.account.models import User

        other_user = User.objects.get(pk=int(request.data.get('user_id')))
        user = request.user
        if other_user == user:
            return Response({"detail": "Cannot start a conversation with yourself."}, 405)

        name = "Chat"
        desc = "Private conversation between " + user.readable_name + " and " + other_user.readable_name
        chatroom = Chatroom.objects.create(name=name, description=desc)
        conversation = Conversation.objects.create(chatroom=chatroom)
        ConversationParticipant.objects.create(user=user, conversation=conversation)
        ConversationParticipant.objects.create(user=other_user, conversation=conversation)
        ChatroomMember.objects.create(user=user, chatroom=chatroom)
        ChatroomMember.objects.create(user=other_user, chatroom=chatroom)

        conversation.send_new_conversation_notification(user, request)

        return Response(ConversationSerializer(conversation, context={'request': request}).data)


class ConversationParticipantViewSet(viewsets.ModelViewSet):
    queryset = ConversationParticipant.objects.all()
    serializer_class = ConversationParticipantSerializer


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupRegularSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def create_study_group(self, request, pk=None):
        """
        Create a study_group
        """
        course_group = self.get_object()
        user = request.user

        try:
            CourseGroupMember.objects.get(course_group=course_group, user=user)
        except CourseGroupMember.DoesNotExist:
            return Response({"detail": "You are not a member of the course"}, 405)

        str_time = request.data.get('time')
        topic = request.data.get('topic')
        location = request.data.get('location')
        num_people = request.data.get('num_people')

        time = datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")

        name = course_group.course.get_readable_name() + " Study Group"
        desc = "Study group for " + course_group.course.get_readable_name() + ", created by " + user.readable_name
        chatroom = Chatroom.objects.create(name=name, description=desc)

        new_study_group = StudyGroup(user=user, chatroom=chatroom, course_group=course_group, time=time, location=location, topic=topic, num_people=num_people)
        new_study_group.save()

        # add creator to the study group and associated chatroom
        StudyGroupMember.objects.create(study_group=new_study_group, user=user)
        ChatroomMember.objects.create(chatroom=new_study_group.chatroom, user=user)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.STUDY_GROUP)
        chatroom_activity = ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=new_study_group.pk)

        course_group.send_study_group_notification(user, chatroom_activity, request)

        obj = StudyGroupSerializer(new_study_group, context={'request': request})
        return Response(obj.data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def get_students(self, request, pk=None):
        """
        Get basic info for student members of a course_group
        """
        user = request.user
        course_group = self.get_object()

        try:
            CourseGroupMember.objects.get(user=user, course_group=course_group)
        except CourseGroupMember.DoesNotExist:
            return Response({"detail": "You are not a member of this course"}, 405)

        all_members = CourseGroupMember.objects.filter(course_group=course_group, is_past=False)
        all_users = [m.student.user for m in all_members]
        obj = UserRegularInfoSerializer(all_users, many=True)
        return Response(obj.data)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated])
    def edit(self, request):
        """
        Add or remove course_groups
        """
        from apps.account.models import SharePromo, PromoType

        addJsonArr = request.data['course_group_additions']
        deleteJsonArr = request.data['course_group_deletions']
        user = request.user

        if not deleteJsonArr:
            deleteJsonArr = []

        if not addJsonArr:
            addJsonArr = []

        for obj in deleteJsonArr:
            course_group_id = obj.get('course_group_id', '')
            try:
                course_group = CourseGroup.objects.get(pk=course_group_id)
                course_member = CourseGroupMember.objects.get(student=user.student, course_group=course_group)
                course_member.is_past = True
                course_member.save()
                chat_member = ChatroomMember.objects.get(user=user, chatroom=course_group.chatroom)
                chat_member.is_past = True
                chat_member.save()
            except CourseGroup.DoesNotExist:
                return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
            except Student.DoesNotExist:
                return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
            except CourseGroupMember.DoesNotExist:
                return Response({"detail": "You are not a member of the class"}, 405)
            except ChatroomMember.DoesNotExist:
                return Response({"detail": "You are not a member of the chatroom"}, 405)

        for obj in addJsonArr:

            course_group_id = obj.get('course_group_id', '')
            course_id = obj.get('course_id', '')
            professor_name = obj.get('professor_name', '')
            if not course_group_id or course_group_id == -1:
                # must create a group to join
                try:
                    course = Course.objects.get(pk=course_id)
                except Course.DoesNotExist:
                    return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
                # first search to see if there's another group with same professor name
                try:
                    course_group = CourseGroup.objects.get(course=course, professor_name=professor_name)
                except CourseGroup.DoesNotExist:
                    # no such group, create a new one
                    chatroom = Chatroom.objects.create(name=course.get_readable_name(), description=course.name)
                    course_group = CourseGroup.objects.create(course=course, professor_name=professor_name, chatroom=chatroom)
            else:
                try:
                    course_group = CourseGroup.objects.get(pk=int(course_group_id))
                    if course_group.is_past:
                        return Response({"detail": "The class has ended"}, 405)
                    member = CourseGroupMember.objects.get(course_group=course_group, student=user.student)
                    if not member.is_past:
                        return Response({"detail": "You are already a member of the class"}, 405)
                    else:
                        member.is_past = False
                        member.save()
                        # should also be a member of the chatroom, make them not_past
                        chat_member = ChatroomMember.objects.get(chatroom=course_group.chatroom, user=user)
                        chat_member.is_past = False
                        chat_member.save()
                        # announce to the group that a new member has joined
                        announcement_type = AnnouncementType.objects.get(identifier="USER_JOINED_GROUP")
                        announcement = Announcement.objects.create(chatroom=course_group.chatroom, announcement_type=announcement_type, user=user)

                        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
                        chatroom_activity = ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
                        course_group.send_new_member_notification(user, chatroom_activity, request)
                        continue
                except CourseGroup.DoesNotExist:
                    return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
                except ChatroomMember.DoesNotExist:
                    return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
                except CourseGroupMember.DoesNotExist:
                    # pass on exception, this just means they hadn't been a member previously
                    pass

            # now add them to the group
            CourseGroupMember.objects.create(course_group=course_group, student=user.student)

            # add them to the group's chatroom
            ChatroomMember.objects.create(chatroom=course_group.chatroom, user=user)

            # announce to the group that a new member has joined
            announcement_type = AnnouncementType.objects.get(identifier="USER_JOINED_GROUP")
            announcement = Announcement.objects.create(chatroom=course_group.chatroom, announcement_type=announcement_type, user=user)

            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
            chatroom_activity = ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
            course_group.send_new_member_notification(user, chatroom_activity, request)

        try:
            # check for completion of user_to_user_share promos
            promo_type = PromoType.objects.get(identifier='user_to_user_share')
            promo = SharePromo.objects.get(promo_type=promo_type, new_user=user, is_past=False)
            promo.old_user.tutor.credits += promo.amount
            promo.old_user.tutor.save()
            promo.is_past = True
            promo.save()

            # notify old user that they got a promo
            merge_vars = {
                "AMOUNT": locale.currency(promo.amount),
                "NEW_USER_NAME": user.first_name
            }
            notification_type = NotificationType.objects.get(identifier="RECEIVED_SHARE_PROMO")
            OpenNotification.objects.create(promo.old_user, notification_type, None, merge_vars, None)

        except SharePromo.DoesNotExist:
            # this is fine, just means they weren't involved in a promo
            pass

        memberships = CourseGroupMember.objects.filter(student=user.student, is_past=False)
        serializer = CourseGroupFullSerializer(CourseGroup.objects.filter(id__in=memberships.values('course_group_id')), many=True, context={'request': request})
        return Response(serializer.data)


class CourseGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = CourseGroupMember.objects.all()
    serializer_class = CourseGroupMemberSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def edit(self, request, pk=None):
        """
        Edit the details of a study group
        """
        user = request.user
        study_group = self.get_object()
        if (user != study_group.user):
            # non-owner cannot edit
            return Response({"detail": "Only the group leader can edit the group details"}, 405)
        if (study_group.is_past):
            return Response({"detail": "This study group has ended"}, 405)
        
        #FUTURE are all of these parameters always updated? If not then this won't work as some parameters will be absent or have bad values

        time = request.POST.get('time')
        topic = request.POST.get('topic')
        location = request.POST.get('location')
        num_people = request.POST.get('num_people')
        if (num_people > study_group.num_people):
            study_group.is_full = False

        study_group.time = time
        study_group.topic = topic
        study_group.location = location
        study_group.num_people = num_people
        study_group.save()

        # notify other members of change
        announcement_type = AnnouncementType.objects.get(identifier="USER_EDITED_GROUP")
        announcement = Announcement.objects.create(chatroom=study_group.chatroom, user=user, announcement_type=announcement_type)
        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        study_group.send_group_edited_notification(activity, request)

        return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def transfer_ownership(self, request, pk=None):
        """
        Transfer ownership of a study group to a different user
        """
        from apps.account.models import User
        user = request.user
        new_owner_id = int(request.data.get('new_owner_id'))
        study_group = self.get_object()
        if (study_group.is_past):
            return Response({"detail": "Only the group leader can edit the group details"}, 405)

        if (user == study_group.user):
            try:
                new_user = User.objects.get(pk=new_owner_id)
                StudyGroupMember.objects.get(user=new_user, study_group=study_group, is_past=False)
                study_group.user = new_user
                study_group.save()
                announcement_type = AnnouncementType.objects.get(identifier="NEW_GROUP_LEADER")
                announcement = Announcement.objects.create(chatroom=study_group.chatroom, user=new_user, announcement_type=announcement_type)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
                activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
                study_group.send_owner_changed_notification(activity, request)
                return Response(ChatroomActivitySerializer(activity, context={'request': request}).data)
            except User.DoesNotExist:
                return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
            except StudyGroupMember.DoesNotExist:
                return Response({"detail": "You are not a member of the study group"}, 405)

        else:
            return Response("Only owner can alter study group", 200)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        """
        Leave a study_group (if creator, delete group)
        """
        user = request.user
        study_group = self.get_object()
        if study_group.is_past:
            return Response("This study group has ended")

        if user == study_group.user:
            # user is creator of group -> archive group and notify users
            study_group.is_past = True
            study_group.save()
            study_group.clear_notifications(request)
            study_group.send_group_ended_notification()
        else:
            try:
                member = StudyGroupMember.objects.get(user=user, study_group=study_group, is_past=False)
                member.is_past = True
                member.save()
                chat_member = ChatroomMember.objects.get(user=user, chatroom=study_group.chatroom, is_past=False)
                chat_member.is_past = True
                chat_member.save()
                # announce to the group that a member has left
                announcement_type = AnnouncementType.objects.get(identifier="USER_LEFT_GROUP")
                announcement = Announcement.objects.create(chatroom=study_group.chatroom, announcement_type=announcement_type, user=user)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
                ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
                if study_group.is_full:
                    study_group.is_full = False
                    study_group.save()
            except StudyGroupMember.DoesNotExist:
                return Response({"detail": "You are not a member of the study group"}, 405)
            except ChatroomMember.DoesNotExist:
                return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a study_group
        """
        user = request.user
        study_group = self.get_object()

        if study_group.is_past:
            return Response({"detail": "The study group has ended"}, 405)

        if study_group.is_full:
            return Response({"detail": "Sorry, the study group is already full"}, 405)

        # check if there is an existing member for this user
        try:
            curr_member = StudyGroupMember.objects.get(study_group=study_group, user=user)
            if not curr_member.is_past:
                return Response({"detail": "You are already a member of the group"}, 405)
            else:
                curr_member.is_past = False
                curr_member.save()
                chat_member = ChatroomMember.objects.get(chatroom=study_group.chatroom, user=user)
                chat_member.is_past = False
                chat_member.save()
                return Response(StudyGroupMemberSerializer(curr_member).data)
        except ChatroomMember.DoesNotExist:
            return Response({"detail": "Sorry, something's wrong with the network. Be back soon!"}, 405)
        except StudyGroupMember.DoesNotExist:

            # add user to both study group and chatroom
            new_group_member = StudyGroupMember.objects.create(study_group=study_group, user=user)

            num_members = StudyGroupMember.objects.filter(study_group=study_group).count()
            if num_members == study_group.num_people:
                study_group.is_full = True
                study_group.save()

            ChatroomMember.objects.create(chatroom=study_group.chatroom, user=user)

            # announce to the group that a new member has joined
            announcement_type = AnnouncementType.objects.get(identifier="USER_JOINED_GROUP")
            announcement = Announcement.objects.create(chatroom=study_group.chatroom, announcement_type=announcement_type, user=user)

            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
            chatroom_activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

            study_group.send_new_member_notification(user, chatroom_activity, request)

            obj = StudyGroupMemberSerializer(new_group_member, context={'request': request})
            return Response(obj.data)


class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = StudyGroupMember.objects.all()
    serializer_class = StudyGroupMemberSerializer
