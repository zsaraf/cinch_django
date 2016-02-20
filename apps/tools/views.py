from django.views.generic.base import TemplateView
from django.db.models import Count
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from rest_framework import exceptions


class CourseGroupDash(TemplateView):
    template_name = 'course_group_dashboard.html'

    def get_context_data(self, **kwargs):
        from forms import FilterForm
        from apps.group.models import CourseGroup

        context = super(CourseGroupDash, self).get_context_data(**kwargs)

        course_group_count = CourseGroup.objects.all().count()
        course_groups_lonely = CourseGroup.objects.raw("SELECT * FROM (SELECT cg.id, cg.professor_name, COUNT(*) as count FROM course_group cg INNER JOIN course_group_member cgm ON cg.id=cgm.course_group_id GROUP BY cg.id) as temp WHERE count=1")
        lonely_count = len(list(course_groups_lonely))

        context['filter_form'] = self.kwargs.get('filter_form', FilterForm())
        context['course_groups'] = self.kwargs.get('course_groups', None)
        context['num_groups'] = course_group_count
        context['num_lonely_groups'] = lonely_count

        return context

    def post(self, request, *args, **kwargs):
        from apps.group.models import CourseGroup, CourseGroupMember
        from apps.chatroom.models import Message, Upload
        from forms import FilterForm

        if 'update_filter' in request.POST:

            form = FilterForm(request.POST)
            self.kwargs['filter_form'] = form
            if form.is_valid():
                data = form.cleaned_data
                filter_type = data['filter_type']

                course_groups = CourseGroup.objects.all()
                context_course_groups = []
                for group in course_groups:
                    course_group = {}
                    course_group['id'] = group.id
                    course_group['num_uploads'] = Upload.objects.filter(chatroom=group.chatroom).count()
                    course_group['num_messages'] = Message.objects.filter(chatroom=group.chatroom).count()
                    course_group['num_students'] = CourseGroupMember.objects.filter(course_group=group).count()
                    course_group['course_name'] = group.course.get_readable_name()
                    course_group['professor_name'] = group.professor_name
                    course_group['school_name'] = group.course.school.name
                    course_group['timestamp'] = group.timestamp
                    context_course_groups.append(course_group)

                if filter_type == 'descending_enrollment':
                    context_course_groups = sorted(context_course_groups, reverse=True, key=lambda k: k['num_students'])
                elif filter_type == 'descending_activity':
                    context_course_groups = sorted(context_course_groups, reverse=True, key=lambda k: k['num_messages'])
                elif filter_type == 'ascending_enrollment':
                    context_course_groups = sorted(context_course_groups, key=lambda k: k['num_students'])
                elif filter_type == 'ascending_activity':
                    context_course_groups = sorted(context_course_groups, key=lambda k: k['num_messages'])

                self.kwargs['course_groups'] = context_course_groups

                return super(CourseGroupDash, self).get(request, args, **kwargs)


class Leaderboard(TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        from apps.chatroom.models import File, Upload
        from apps.account.models import ContestShare, SharePromo

        context = super(Leaderboard, self).get_context_data(**kwargs)

        referral_leaders = ContestShare.objects.values('contest_code_id', 'contest_code__identifier').annotate(count=Count('contest_code_id')).order_by('-count')
        uploads = File.objects.values('upload_id').annotate(count=Count('upload_id')).order_by('count')
        upload_leaders = {}
        for u in uploads:
            try:
                upload = Upload.objects.get(pk=u['upload_id'])
                share = ContestShare.objects.get(user=upload.chatroom_member.user)
                if share.contest_code.identifier in upload_leaders:
                    upload_leaders[share.contest_code.identifier] += int(u['count'])
                else:
                    upload_leaders[share.contest_code.identifier] = int(u['count'])
            except ContestShare.DoesNotExist:
                pass

        today = datetime.now().date()
        num_days = today.weekday()
        min_date = today - timedelta(days=num_days)

        individual_referrals = SharePromo.objects.filter(is_past=True, timestamp__gt=min_date).values('old_user', 'old_user__email').annotate(count=Count('old_user')).order_by('-count')

        individual_uploads = File.objects.filter(timestamp__gt=min_date).values('upload__chatroom_member__user__email').annotate(count=Count('upload__chatroom_member__user__email')).order_by('-count')

        context = {'referral_leaders': referral_leaders, 'upload_leaders':upload_leaders, 'individual_referrals': individual_referrals, 'individual_uploads': individual_uploads}
        return context


class TeamChat(TemplateView):
    template_name = 'team_chat.html'

    def get_context_data(self, **kwargs):
        from apps.account.models import User
        from apps.account.forms import UserForm, MessageForm

        context = super(TeamChat, self).get_context_data(**kwargs)
        team_user = User.objects.get(email='team@seshtutoring.com')
        user_form = self.kwargs.get('user_form', UserForm())
        message_form = self.kwargs.get('message_form', MessageForm())
        user_obj = self.kwargs.get('user_obj', None)
        recent_messages = self.kwargs.get('recent_messages', None)
        message_form = self.kwargs.get('message_form', None)

        if user_obj is not None:
            context['user_obj'] = user_obj
        if recent_messages is not None:
            context['recent_messages'] = recent_messages
        if message_form is not None:
            context['message_form'] = message_form

        context['team_user'] = team_user
        context['user_form'] = user_form
        return context

    def post(self, request, *args, **kwargs):
        from apps.account.forms import MessageForm, UserForm
        from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomMember, Message, ChatroomActivityTypeManager
        from apps.chatroom.serializers import WelcomeMessageChatroomActivitySerializer
        from apps.notification.models import NotificationType, OpenNotification
        from apps.account.models import User

        team_user = User.objects.get(email='team@seshtutoring.com')

        if 'send_message' in request.POST:

            form = MessageForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                text = data['message_text']
                user = User.objects.get(pk=data['user_id'])
                name = "The Sesh Team"
                desc = "We're so happy you're here! Any questions?"
                user_member = ChatroomMember.objects.get(user=user, chatroom__name=name, chatroom__description=desc)
                chatroom = user_member.chatroom
                team_member = ChatroomMember.objects.get(user=team_user, chatroom=chatroom)

                message = Message.objects.create(message=text, chatroom=chatroom, chatroom_member=team_member)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
                activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)

                merge_vars = {
                    "NAME": team_user.full_name,
                    "CHATROOM_NAME": chatroom.name,
                    "MESSAGE": text
                }
                data = {
                    "chatroom_activity": WelcomeMessageChatroomActivitySerializer(activity).data,
                }
                notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
                OpenNotification.objects.create(user, notification_type, data, merge_vars, None)

                self.kwargs['user_form'] = UserForm(initial={'user_identifier': user.pk})

            return super(TeamChat, self).get(request, args, **kwargs)

        elif 'user_lookup' in request.POST:

            form = UserForm(request.POST)
            self.kwargs['user_form'] = form
            if form.is_valid():
                user = form.get_user()
                name = "The Sesh Team"
                desc = "We're so happy you're here! Any questions?"
                user_member = ChatroomMember.objects.get(user=user, chatroom__name=name, chatroom__description=desc)
                chatroom = user_member.chatroom

                recent_messages = Message.objects.filter(chatroom=chatroom).order_by('-id')[:5][::-1]
                message_form = MessageForm(initial={'user_id': user.pk})

                self.kwargs['user_obj'] = user
                self.kwargs['recent_messages'] = recent_messages
                self.kwargs['message_form'] = message_form

            return super(TeamChat, self).get(request, args, **kwargs)

class MergeCourseGroups(TemplateView):
    template_name = 'merge_course_groups.html'

    def get_context_data(self, **kwargs):
        from apps.account.models import User
        from apps.group.forms import MergeGroupsForm

        context = super(MergeCourseGroups, self).get_context_data(**kwargs)
        team_user = User.objects.get(email='team@seshtutoring.com')
        form = MergeGroupsForm()
        context = {'team_user': team_user, 'form': form}
        return context

    def post(self, request, *args, **kwargs):
        from apps.group.forms import MergeGroupsForm
        from apps.notification.models import NotificationType, OpenNotification
        from apps.group.models import CourseGroup, CourseGroupMember
        from apps.chatroom.models import ChatroomMember

        form = MergeGroupsForm(request.POST)
        if form.is_valid():
            groups = form.get_groups()

            first_group = CourseGroup.objects.get(pk=groups[0])
            second_group = CourseGroup.objects.get(pk=groups[1])

            if first_group.is_past or second_group.is_past:
                return HttpResponseRedirect('/django/tools/merge/')

            winner_group = first_group
            loser_group = second_group

            if first_group.coursegroupmember_set.all().count() < second_group.coursegroupmember_set.all().count():
                winner_group = second_group
                loser_group = first_group

            loser_group.is_past = True
            loser_group.save()

            loser_members = CourseGroupMember.objects.filter(course_group=loser_group, is_past=False)
            for member in loser_members:
                member.is_past = True
                old_chat_member = ChatroomMember.objects.get(chatroom=loser_group.chatroom, user=member.student.user)
                old_chat_member.is_past = True
                old_chat_member.save()
                member.save()

                try:
                    # see if they're already a member of the other group
                    existing_member = CourseGroupMember.objects.get(course_group=winner_group, student=member.student)
                    chat_member = ChatroomMember.objects.get(chatroom=winner_group.chatroom, user=member.student.user)
                    if existing_member.is_past:
                        existing_member.is_past = False
                        chat_member.is_past = False
                        chat_member.save()
                        existing_member.save()
                except CourseGroupMember.DoesNotExist:
                    # they weren't already a member, create a new one
                    CourseGroupMember.objects.create(course_group=winner_group, student=member.student, is_past=False)
                    ChatroomMember.objects.create(chatroom=winner_group.chatroom, user=member.student.user)

                # send refresh user notification
                notification_type = NotificationType.objects.get(identifier='REFRESH_FULL_USER_INFORMATION')
                OpenNotification.objects.create(member.student.user, notification_type, None, None, None)

        return HttpResponseRedirect('/django/tools/merge/')


class Messaging(TemplateView):
    template_name = 'messaging.html'

    def get_context_data(self, **kwargs):
        from apps.account.forms import SimpleMessageForm

        context = super(Messaging, self).get_context_data(**kwargs)
        form = SimpleMessageForm()
        context = {'form': form}
        return context

    def post(self, request, *args, **kwargs):
        from apps.account.forms import SimpleMessageForm
        from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomMember, Message, ChatroomActivityTypeManager
        from apps.chatroom.serializers import WelcomeMessageChatroomActivitySerializer
        from apps.notification.models import NotificationType, OpenNotification
        from apps.account.models import User
        from apps.group.models import CourseGroupMember, CourseGroup

        team_user = User.objects.get(email='team@seshtutoring.com')

        form = SimpleMessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            original_text = data['message_text']

            course_groups_lonely = CourseGroup.objects.raw("SELECT * FROM (SELECT cg.id, cg.professor_name, COUNT(*) as count FROM course_group cg INNER JOIN course_group_member cgm ON cg.id=cgm.course_group_id GROUP BY cg.id) as temp WHERE count=1")
            users = {}
            for course_group in course_groups_lonely:
                group = CourseGroup.objects.get(pk=course_group.id)
                group_member = CourseGroupMember.objects.filter(course_group=group, is_past=False)
                if len(group_member) == 1:
                    user = group_member[0].student.user
                    if user.pk not in users:
                        users[user.pk] = user

            for user_id, user in users.iteritems():
                name = "The Sesh Team"
                desc = "We're so happy you're here! Any questions?"
                user_member = ChatroomMember.objects.get(user=user, chatroom__name=name, chatroom__description=desc)
                chatroom = user_member.chatroom
                team_member = ChatroomMember.objects.get(user=team_user, chatroom=chatroom)

                text = original_text.replace("|*NAME*|", user.first_name).replace("|*CODE*|", user.share_code)

                message = Message.objects.create(message=text, chatroom=chatroom, chatroom_member=team_member)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
                activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)

                merge_vars = {
                    "NAME": team_user.full_name,
                    "CHATROOM_NAME": chatroom.name,
                    "MESSAGE": text
                }
                data = {
                    "chatroom_activity": WelcomeMessageChatroomActivitySerializer(activity).data,
                }
                notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
                OpenNotification.objects.create(user, notification_type, data, merge_vars, None)

        return HttpResponseRedirect('/django/tools/messaging/')


class Dashboard(TemplateView):
    template_name = 'team_dashboard.html'

    def get_context_data(self, **kwargs):
        from apps.account.models import User
        from apps.account.forms import AutoMessageForm

        context = super(Dashboard, self).get_context_data(**kwargs)
        team_user = User.objects.get(email='team@seshtutoring.com')
        form = AutoMessageForm()
        context = {'team_user': team_user, 'form': form}
        return context

    def post(self, request, *args, **kwargs):
        from apps.account.forms import AutoMessageForm
        from apps.chatroom.models import ChatroomActivity, ChatroomActivityType, ChatroomMember, Message, ChatroomActivityTypeManager
        from apps.chatroom.serializers import WelcomeMessageChatroomActivitySerializer
        from apps.notification.models import NotificationType, OpenNotification
        from apps.account.models import User

        team_user = User.objects.get(email='team@seshtutoring.com')

        form = AutoMessageForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            text = data['message_text']
            users = form.get_user_list()

            for user_id in users:
                user = User.objects.get(pk=int(user_id))

                name = "The Sesh Team"
                desc = "We're so happy you're here! Any questions?"
                user_member = ChatroomMember.objects.get(user=user, chatroom__name=name, chatroom__description=desc)
                chatroom = user_member.chatroom
                team_member = ChatroomMember.objects.get(user=team_user, chatroom=chatroom)

                message = Message.objects.create(message=text, chatroom=chatroom, chatroom_member=team_member)
                activity_type = ChatroomActivityType.objects.get_activity_type(ChatroomActivityTypeManager.MESSAGE)
                activity = ChatroomActivity.objects.create(chatroom=chatroom, chatroom_activity_type=activity_type, activity_id=message.pk)

                merge_vars = {
                    "NAME": team_user.full_name,
                    "CHATROOM_NAME": chatroom.name,
                    "MESSAGE": text
                }
                data = {
                    "chatroom_activity": WelcomeMessageChatroomActivitySerializer(activity).data,
                }
                notification_type = NotificationType.objects.get(identifier="NEW_MESSAGE")
                OpenNotification.objects.create(user, notification_type, data, merge_vars, None)

        return HttpResponseRedirect('/django/tools/dashboard/')
