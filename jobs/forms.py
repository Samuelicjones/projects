from django import forms
from .models import Job
from customers.models import Customer
from teams.models import TeamMember

class JobForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Job
        fields = ['customer', 'team_member', 'start_time', 'priority', 'job_status', 'job_description', 'additional_notes']

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)  # Pass the team to the form
        super(JobForm, self).__init__(*args, **kwargs)

        # Filter customers based on the team
        if team:
            self.fields['customer'].queryset = Customer.objects.filter(team=team)
            self.fields['team_member'].queryset = TeamMember.objects.filter(team=team)

        # Show the user's name instead of 'TeamMember object (1)', etc.
        self.fields['team_member'].label_from_instance = lambda obj: f'{obj.user.username}'
