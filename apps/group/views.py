from .models import *
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from apps.university.models import Course
from apps.student.models import Student
from apps.chatroom.models import Chatroom, Announcement
from apps.account.serializers import UserBasicInfoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from datetime import datetime
from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager
import logging
logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


class ConversationParticipantViewSet(viewsets.ModelViewSet):
    queryset = ConversationParticipant.objects.all()
    serializer_class = ConversationParticipantSerializer


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def create_study_group(self, request, pk=None):
        """
        Create a study_group
        """
        course_group = self.get_object()
        user = request.user

        str_time = request.POST.get('time')
        topic = request.POST.get('topic')
        location = request.POST.get('location')
        num_people = request.POST.get('num_people')

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

        course_group.send_study_group_notification(user, chatroom_activity)

        obj = StudyGroupSerializer(new_study_group)
        return Response(obj.data)

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def get_students(self, request, pk=None):
        """
        Get basic info for student members of a course_group
        """
        course_group = self.get_object()
        all_members = CourseGroupMember.objects.filter(course_group=course_group)
        all_users = [m.student.user for m in all_members]
        obj = UserBasicInfoSerializer(all_users, many=True)
        return Response(obj.data)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated])
    def edit(self, request):
        """
        Add or remove course_groups
        """
        addJsonArr = request.data['course_group_additions']
        deleteJsonArr = request.data['course_group_deletions']
        user = request.user

        for obj in deleteJsonArr:
            course_group_id = obj.get('course_group_id', '')
            try:
                course_group = CourseGroup.objects.get(pk=course_group_id)
                student = Student.objects.get(user=user)
                CourseGroupMember.objects.get(student=student, course_group=course_group).delete()
            except CourseGroup.DoesNotExist:
                raise exceptions.NotFound("Course Group could not be found")
            except Student.DoesNotExist:
                raise exceptions.NotFound("Couldn't find a record of this student")
            except CourseGroupMember.DoesNotExist:
                raise exceptions.NotFound("Couldn't find a member of the course group for this user")

        for obj in addJsonArr:

            course_group_id = obj.get('course_group_id', '')
            course_id = obj.get('course_id', '')
            professor_name = obj.get('professor_name', '')
            if course_group_id == -1:
                # must create a group to join
                try:
                    course = Course.objects.get(pk=course_id)
                except Course.DoesNotExist:
                    raise exceptions.NotFound("Course could not be found")
                chatroom = Chatroom.objects.create(name=course.get_readable_name(), description=course.name)
                course_group = CourseGroup.objects.create(course=course, professor_name=professor_name, chatroom=chatroom)
            else:
                try:
                    course_group = CourseGroup.objects.get(pk=course_group_id)
                except CourseGroup.DoesNotExist:
                    raise exceptions.NotFound("Course Group could not be found")
                if (len(CourseGroupMember.objects.filter(course_group=course_group, student=user.student)) > 0 | course_group.is_past):
                    continue

            # now add them to the group
            CourseGroupMember.objects.create(course_group=course_group, student=user.student)

            # add them to the group's chatroom
            ChatroomMember.objects.create(chatroom=course_group.chatroom, user=user)

            # announce to the group that a new member has joined
            message = user.readable_name + " has joined"
            announcement = Announcement.objects.create(chatroom=course_group.chatroom, message=message)

            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
            chatroom_activity = ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
            course_group.send_new_member_notification(user, chatroom_activity)

        memberships = CourseGroupMember.objects.filter(student=user.student)
        serializer = CourseGroupSerializer(CourseGroup.objects.filter(id__in=memberships.values('course_group_id')), many=True)
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
            return Response("You do not own this study group", 200)
        if (study_group.is_past):
            return Response("This study group has ended", 200)

        time = request.POST.get('time')
        topic = request.POST.get('topic')
        location = request.POST.get('location')
        num_people = request.POST.get('num_people')

        study_group.time = time
        study_group.topic = topic
        study_group.location = location
        study_group.num_people = num_people
        study_group.save()

        # notify other members of change
        message = user.readable_name + " has edited the group details"
        announcement = Announcement.objects.create(chatroom=study_group.chatroom, message=message)
        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        study_group.send_group_edited_notification(activity)

        return Response()

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
            return Response("This study group has ended", 200)

        if (user == study_group.user):
            try:
                new_user = User.objects.get(pk=new_owner_id)
                StudyGroupMember.objects.get(user=new_user, study_group=study_group)
                study_group.user = new_user
                study_group.save()
                message = new_user.readable_name + " is now leading the group"
                announcement = Announcement.objects.create(chatroom=study_group.chatroom, message=message)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
                activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
                study_group.send_owner_changed_notification(activity)
                return Response(StudyGroupSerializer(study_group).data)
            except User.DoesNotExist:
                raise exceptions.NotFound("User not found")
            except StudyGroupMember.DoesNotExist:
                raise exceptions.NotFound("User is not part of the study group")

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
            study_group.send_group_ended_notification()
        else:
            try:
                StudyGroupMember.objects.get(user=user, study_group=study_group).delete()
                # announce to the group that a member has left
                message = user.readable_name + " has left the group"
                announcement = Announcement.objects.create(chatroom=study_group.chatroom, message=message)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
                ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)
                if study_group.is_full:
                    study_group.is_full = False
                    study_group.save()
            except StudyGroupMember.DoesNotExist:
                return Response("You are not a member of this group")

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a study_group
        """
        user = request.user
        study_group = self.get_object()

        if study_group.is_past:
            return Response("This study group has ended")

        if len(StudyGroupMember.objects.filter(study_group=study_group, user=user)) > 0:
            return Response()

        if study_group.is_full:
            return Response("This study group is full")

        # add user to both study group and chatroom
        new_group_member = StudyGroupMember.objects.create(study_group=study_group, user=user)

        num_members = StudyGroupMember.objects.filter(study_group=study_group).count()
        if num_members == study_group.num_people:
            study_group.is_full = True
            study_group.save()

        ChatroomMember.objects.create(chatroom=study_group.chatroom, user=user)

        # announce to the group that a new member has joined
        message = user.readable_name + " has joined"
        announcement = Announcement.objects.create(chatroom=study_group.chatroom, message=message)

        activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
        chatroom_activity = ChatroomActivity.objects.create(chatroom=study_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

        study_group.send_new_member_notification(user, chatroom_activity)

        obj = StudyGroupMemberSerializer(new_group_member)
        return Response(obj.data)


class StudyGroupMemberViewSet(viewsets.ModelViewSet):
    queryset = StudyGroupMember.objects.all()
    serializer_class = StudyGroupMemberSerializer
