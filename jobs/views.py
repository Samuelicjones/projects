from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from teams.models import TeamMember, Team, ActivityLog
from .models import Job
from .forms import JobForm
from django.db.models import Q
from teams.views import team_redirect

# Create your views here.
@login_required
def job_list(request):
    team_member = TeamMember.objects.get(user=request.user)
    team = team_member.team  # Assuming each team member is related to one team
    access_level = team_member.access_level
    query = request.GET.get('q')

    if access_level >= 3:
        jobs = Job.objects.filter(team_member__team=team, job_status__in=['Pending', 'In Progress'])
    else:
        jobs = Job.objects.filter(team_member=team_member, job_status__in=['Pending', 'In Progress'])

    # Apply search filter if query exists
    if query:
        jobs = jobs.filter(
            Q(customer__name__icontains=query) |  # Assuming customer name for filtering
            Q(team_member__user__first_name__icontains=query) |  # Assuming team_member has a ForeignKey to User
            Q(start_time__icontains=query) |  # This may need adjustment if 'start_time' is a DateTimeField
            Q(priority__icontains=query) |
            Q(job_status__icontains=query)
        )

    if request.method == 'POST':
        form = JobForm(request.POST, team=team)  # Pass the team to the form
        if form.is_valid():
            job = form.save(commit=False)
            job.team_member = form.cleaned_data['team_member']
            job.save()
            ActivityLog.objects.create(
                team_member=team_member,
                action='Added Job:',
                affected_object=f"{job.customer.name} (Job)"
        )
            return redirect('jobs:job_list')
    else:
        form = JobForm(team=team)  # Pass the team to the form when rendering

    context = {
        'jobs': jobs, 
        'form': form,
        'access_level' : access_level
    }
    return render(request, 'jobs/job_list.html', context)

@login_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    user = request.user
    team_redirect(user, job.customer.team.id)
    context = {'job':job}
    return render(request, 'jobs/job_details.html', context)


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    team_member = TeamMember.objects.get(user=request.user)
    user = request.user
    user = request.user
    team_redirect(user, job.customer.team.id)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            ActivityLog.objects.create(
                team_member=team_member,
                action='Edited Job:',
                affected_object=f"{job.customer.name} (Job)"
        )
            form.save()
            return redirect('jobs:job_details', pk=pk)
    else:
        form = JobForm(instance=job)
    
    context = {'form':form}
    return render(request, 'jobs/job_edit.html', context)

@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    team_member = TeamMember.objects.get(user=request.user)
    user = request.user
    team = user.teams.first()
    team_redirect(user, team.id)
    if request.method == 'POST':
        ActivityLog.objects.create(
                team_member=team_member,
                action='Deleted Job:',
                affected_object=f"{job.customer.name} (Job)"
        )
        job.delete()
        return redirect('jobs:job_list')
    context = {'job' : job}
    return render(request, 'jobs/job_delete.html', context)


@login_required
def change_status(request, pk, new_status):
    job = get_object_or_404(Job, pk=pk)
    team_member = TeamMember.objects.get(user=request.user)
    if new_status in ['Pending', 'In Progress', 'Completed', 'Canceled']:
        job.job_status = new_status
        job.save()
        ActivityLog.objects.create(
                team_member=team_member,
                action='Changed Status:',
                affected_object=f"{job.customer.name} (Job)"
        )
        if new_status == 'Completed':
            return redirect('reports:submit_report', job_id=job.pk)
        
    return redirect('jobs:job_details', pk=pk)