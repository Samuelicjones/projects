from django.shortcuts import render, redirect, get_object_or_404
from .models import Team, TeamMember, ActivityLog
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from .forms import TeamCreationForm, JoinTeamForm
from django.utils.timezone import localtime, now
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .forms import UpdateProfileForm, PromoteMemberForm
from django.urls import reverse
from django.core.serializers.json import DjangoJSONEncoder
from jobs.models import Job
import json
from django.utils.timezone import now, timedelta
from django.db.models import Q


@login_required
def create_team(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if team_name:
            user = request.user
            team = Team(name=team_name, creator=user)
            team.save()
            # Add the creator as a member with full access (level 4)
            team.add_member(user, access_level=4)
            return redirect('dashboard')  # Redirect to the dashboard after creation

    return render(request, 'teams/create_team.html')

@login_required
def join_team(request):
    
    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team_uuid = form.cleaned_data.get('team_uuid')
            team = Team.objects.filter(id=team_uuid).first()
            if team:
                if request.user.teams.exists():
                    return render(request, 'teams/join_team.html', {'form': form, 'error': 'You are already part of a team.'})
                team.add_member(request.user, access_level=1)  # Join with access level 1
                return redirect('team_dashboard', team_slug=team.slug)
    else:
        form = JoinTeamForm()
    context = {'form' : form} 
    return render(request, 'teams/join_team.html', context)


@login_required
def team_dashboard(request, team_slug):
    team = get_object_or_404(Team, slug=team_slug)
    user = request.user
    team_redirect(user, team.id)
    user_team = user.teams.first()
    team_member = TeamMember.objects.get(team=user_team, user=user)
    access_level = team_member.access_level
    threshold_time = now() - timedelta(days=1)

    recent_logs = None
    if team_member.access_level >= 3:
        recent_logs = ActivityLog.objects.filter(team_member__team=team).order_by('-timestamp')[:10]

    if access_level >= 3:
        # Access level 3 or higher can view all jobs
        jobs = Job.objects.filter(start_time__gte=threshold_time, team_member__team=team).exclude(job_status='Completed')
    else:
        # Access level 2 or lower can only view their own assigned jobs
        jobs = Job.objects.filter(start_time__gte=threshold_time, team_member=team_member).exclude(job_status='Completed')
    # Format jobs as events for FullCalendar
    jobs_events = [
        {
            'title': job.customer.name,
            'start': localtime(job.start_time).isoformat(),
            'url': reverse('jobs:job_details', args=[job.pk]),
            'priority': job.priority,  # Add priority to the extended props for color coding
        }
        for job in jobs
    ]

    if request.user not in team.members.all():
        return redirect('dashboard')

    context = {
        'team_name': team.name,
        'user_team': team,
        'team_member': team_member,
        'access_level': access_level,
        'recent_logs': recent_logs,
        'jobs_events_json': json.dumps(jobs_events, cls=DjangoJSONEncoder),  # Pass the jobs as JSON
    }

    return render(request, 'teams/dashboard.html', context)


@login_required
def team_member_profile(request, team_slug, member_id):
    team = get_object_or_404(Team, slug=team_slug)
    member = get_object_or_404(TeamMember, team=team, user_id=member_id)

    # Ensure the current user is part of the team
    team_member = get_team_member_or_forbidden(team, request.user)
    team_redirect(request.user, team.id)
    access_level = team_member.access_level
    # Check if the current user is viewing their own profile
    is_own_profile = request.user == member.user
    active_jobs = Job.objects.filter(team_member=member, job_status__in=['Pending', 'In Progress'])

    # Handle POST requests for updating profile or promoting a member
    if request.method == 'POST':
        handle_post_request(request, team_member, member, is_own_profile)

    # Handle the forms
    form, promote_form = get_forms(member, is_own_profile)

    # Pass context to template
    context = {
        'member': member,
        'form': form,
        'active_jobs': active_jobs,
        'promote_form': promote_form,
        'is_own_profile': is_own_profile,
        'access_level': access_level,
    }
    
    return render(request, 'teams/team_member_profile.html', context)


def get_team_member_or_forbidden(team, user):
    """Get the TeamMember object or return a forbidden response if the user is not part of the team."""
    try:
        return TeamMember.objects.get(team=team, user=user)
    except TeamMember.DoesNotExist:
        raise HttpResponseForbidden("You are not a member of this team.")


def handle_post_request(request, team_member, member, is_own_profile):
    if 'update_profile' in request.POST:
        if is_own_profile:
            update_profile(request, member)
            
    elif 'promote_member' in request.POST and not is_own_profile:
        promote_member(request, team_member, member)
        


def update_profile(request, member):
    form = UpdateProfileForm(request.POST, instance=member.user)
    if form.is_valid():
        form.save()



def promote_member(request, team_member, member):
    promote_form = PromoteMemberForm(request.POST, instance=member)
    if promote_form.is_valid():
        new_access_level = promote_form.cleaned_data['access_level']
        choices = ['View Only', 'Create Jobs', 'Manage']
        # Prevent self-promotion or self-demotion
        if request.user == member.user:
            return HttpResponseForbidden("You cannot promote or demote yourself.")

        # Check if the user has permission to promote/demote based on their access level
        if team_member.access_level == 4 and new_access_level <= 3:
            member.access_level = new_access_level
            member.save()
            ActivityLog.objects.create(
                team_member=team_member,
                action='promoted',
                affected_object=f"{member.user.username} ({choices[new_access_level - 1]})"
        )
        elif team_member.access_level == 3 and new_access_level <= 2:
            member.access_level = new_access_level
            member.save()
            ActivityLog.objects.create(
                team_member=team_member,
                action='promoted',
                affected_object=f"{member.user.username} ({choices[new_access_level - 1]})"
        )
        else:
            return HttpResponseForbidden("You don't have permission to promote/demote this member.")


def get_forms(member, is_own_profile):
    form = UpdateProfileForm(instance=member.user) if is_own_profile else None
    promote_form = PromoteMemberForm(instance=member) if not is_own_profile else None
    return form, promote_form

@login_required
def full_activity_log(request):
    team_member = TeamMember.objects.get(user=request.user)
    if team_member.access_level < 3:
        return redirect('dashboard')

    all_logs = ActivityLog.objects.filter(team_member__team=team_member.team).order_by('-timestamp')
    
    # Check if there is a query parameter for search
    query = request.GET.get('q')
    if query:
        all_logs = all_logs.filter(
            Q(team_member__user__username__icontains=query) |
            Q(team_member__user__first_name__icontains=query) |
            Q(action__icontains=query) |
            Q(affected_object__icontains=query) |
            Q(timestamp__icontains=query)
        )
        
    context = {
        'all_logs': all_logs
    }
    return render(request, 'teams/full_activity_log.html', context)

@login_required
def dashboard(request):
    user = request.user
    teams = user.teams.all()
    
    if teams.exists():
        return redirect('team_dashboard', team_slug=teams.first().slug)  # Redirect to the first team’s dashboard
    else:
        return redirect('create_team_or_invite')

@login_required
def display_join_team(request):
    form = JoinTeamForm()
    return render(request, 'teams/join_team.html', {'form': form})


@login_required
def create_team_or_invite_view(request):
    return render(request, 'teams/create_team_or_invite.html')

def team_redirect(user, team_id):
    try:
        user_team = TeamMember.objects.get(user=user).team
    except TeamMember.DoesNotExist:
        raise PermissionDenied("You are not a member of any team.")

    if user_team.id != team_id:
        raise PermissionDenied("Access denied. You cannot view resources from other teams.")
