from django import forms
from .models import Team, TeamMember
from django.contrib.auth.models import User
from accounts.models import CustomUser

class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class JoinTeamForm(forms.Form):
    team_uuid = forms.UUIDField(label='Team UUID', required=True)

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number']
class PromoteMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['access_level']
        widgets = {
            'access_level': forms.Select(choices=TeamMember.ACCESS_LEVEL)
        }