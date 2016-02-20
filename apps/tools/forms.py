from django import forms


class FilterForm(forms.Form):
    filter_type = forms.ChoiceField(widget=forms.Select(), choices=[('ascending_enrollment', 'acending_enrollment'), ('ascending_activity', 'ascending_activity'), ('descending_enrollment', 'descending_enrollment'), ('descending_activity', 'descending_activity')])
