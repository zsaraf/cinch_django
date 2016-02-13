from django.views.generic.base import TemplateView
from django.db.models import Count
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from rest_framework import exceptions


class Leaderboard(TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        from apps.chatroom.models import File, Upload
        from apps.account.models import ContestShare, SharePromo

        context = super(Leaderboard, self).get_context_data(**kwargs)

        referral_leaders = ContestShare.objects.values('contest_code_id', 'contest_code__identifier').annotate(count=Count('contest_code_id')).order_by('-count')
        uploads = File.objects.values('upload_id').annotate(count=Count('upload_id')).order_by('-count')
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
            data = form.cleaned_datai
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
