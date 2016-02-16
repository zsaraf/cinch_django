from django import forms


class MergeGroupsForm(forms.Form):
    group_id_strings = forms.CharField()

    def get_groups(self):
        data = self.cleaned_data
        return [item.strip() for item in data['group_id_strings'].split(',')]
