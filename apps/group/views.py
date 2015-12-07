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
import json
from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomActivityTypeManager


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
        ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=new_study_group.pk)

        course_group.send_study_group_notification(user)

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
        addJsonArr = json.loads(request.data.get('course_group_additions'))
        deleteJsonArr = json.loads(request.data.get('course_group_deletions'))
        user = request.user
        all_course_group_memberships = []

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
            if not course_group_id:
                # must create a group to join
                try:
                    course = Course.objects.get(pk=course_id)
                except Course.DoesNotExist:
                    raise exceptions.NotFound("Course could not be found")
                chatroom = Chatroom.objects.create(name=course.get_readable_name(), description=course.name)
                chatroom.save()
                course_group = CourseGroup.objects.create(course=course, professor_name=professor_name, chatroom=chatroom)
                course_group.save()
            else:
                try:
                    course_group = CourseGroup.objects.get(pk=course_group_id)
                except CourseGroup.DoesNotExist:
                    raise exceptions.NotFound("Course Group could not be found")
                if (len(CourseGroupMember.objects.filter(course_group=course_group, student=user.student)) > 0 | course_group.is_past):
                    continue

            # now add them to the group
            new_group_member = CourseGroupMember.objects.create(course_group=course_group, student=user.student)
            all_course_group_memberships.append(new_group_member)

            # add them to the group's chatroom
            ChatroomMember.objects.create(chatroom=course_group.chatroom, user=user)

            # announce to the group that a new member has joined
            message = user.readable_name + " has joined"
            announcement = Announcement.objects.create(chatroom=course_group.chatroom, message=message)

            activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.ANNOUNCEMENT)
            chatroom_activity = ChatroomActivity.objects.create(chatroom=course_group.chatroom, chatroom_activity_type=activity_type, activity_id=announcement.pk)

            course_group.send_new_member_notification(user, chatroom_activity)

        serializer = CourseGroupMemberSerializer(all_course_group_memberships, many=True)
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
    def leave(self, request, pk=None):
        """
        Leave a study_group (if creator, delete group)
        """
        user = request.user
        study_group = self.get_object()
        if (study_group.is_past):
            return Response("This study group has ended", 200)

        if (user == study_group.user):
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
            except StudyGroupMember.DoesNotExist:
                return Response("You are not a member of this group", 200)

        return Response()

    @detail_route(methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a study_group
        """
        user = request.user
        study_group = self.get_object()

        if (study_group.is_past):
            return Response("This study group has ended", 200)

        if (len(StudyGroupMember.objects.filter(study_group=study_group, user=user)) > 0):
            return Response()

        # add user to both study group and chatroom
        new_group_member = StudyGroupMember.objects.create(study_group=study_group, user=user)
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
