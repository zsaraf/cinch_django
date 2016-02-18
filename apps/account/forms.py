from django import forms
from .models import User


class AutoMessageForm(forms.Form):
    user_id_strings = forms.CharField()
    message_text = forms.CharField(widget=forms.Textarea)

    def get_user_list(self):
        data = self.cleaned_data
        return [item.strip() for item in data['user_id_strings'].split(',')]


class SimpleMessageForm(forms.Form):
    message_text = forms.CharField(widget=forms.Textarea)


class MessageForm(forms.Form):
    message_text = forms.CharField(widget=forms.Textarea)
    user_id = forms.IntegerField(widget=forms.HiddenInput)


class UserForm(forms.Form):
    user_identifier = forms.CharField()

    def get_user(self):
        user = None
        try:
            data = self.cleaned_data
        except:
            return user

        try:
            user = User.objects.get(pk=data['user_identifier'])
        except:
            try:
                user = User.objects.get(email=data['user_identifier'])
            except:
                pass
        return user
