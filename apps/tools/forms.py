from django import forms


class FilterForm(forms.Form):
    filter_type = forms.ChoiceField(widget=forms.Select(), choices=[('total_enrollment', 'enrollment'), ('recent_enrollment', 'recent enrollment')])
