from django import forms


class AutoMessageForm(forms.Form):
    user_id_strings = forms.CharField()
    message_text = forms.CharField(widget=forms.Textarea)

    def get_user_list(self):
        data = self.cleaned_data
        return [item.strip() for item in data['user_id_strings'].split(',')]
