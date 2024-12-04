from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.contrib.auth.decorators import login_required
from .models import Customer
from .forms import CustomerForm
from teams.models import Team, TeamMember, ActivityLog
from jobs.models import Job
from django.db.models import Q
from teams.views import team_redirect

# Create your tests here.

@login_required
def customer_list(request):
    user = request.user
    if not user.teams.exists():
        return redirect('create_team_or_invite')

    team = user.teams.first()
    try:
        # Fetch the user's access level in this team
        team_member = TeamMember.objects.get(team=team, user=user)
        access_level = team_member.access_level
        can_add_customer = team_member.access_level >= 3  # Only level 2 or higher can add customers
    except TeamMember.DoesNotExist:
        can_add_customer = False

    if request.method == 'POST' and can_add_customer:
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.team = team
            customer.save()
            ActivityLog.objects.create(
                team_member=team_member,
                action='Added Customer:',
                affected_object=f"{customer.name} (Customer)"
        )
            return redirect('customer_list')
    else:
        form = CustomerForm()

    query = request.GET.get('q')  # Get the search query from the URL
    if query:
        # Filter customers by name, phone, email, or company
        customers = Customer.objects.filter(team=team).filter(
            Q(name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query)
        )
    else:
        customers = Customer.objects.filter(team=team)
    
    
    
    context = {
        'form': form,
        'customers': customers,
        'team': team,
        'can_add_customer': can_add_customer,
        'access_level': access_level,  # Pass to template
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    user = request.user
    team = customer.team  # Assuming `customer` has a ForeignKey to `team`
    jobs = Job.objects.filter(customer=customer) 
    team_redirect(user, team.id)
    try:
        # Fetch the user's access level in the team
        team_member = TeamMember.objects.get(team=team, user=user)
        access_level = team_member.access_level
    except TeamMember.DoesNotExist:
        access_level = 1  # If the user is not part of the team, set a default access level

    context = {
        'customer': customer,
        'access_level': access_level,  # Pass the access level to the template
        'jobs': jobs,
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    user = request.user
    team = customer.team
    team_redirect(user, customer.team.id)
    try:
        # Fetch the user's access level in this team
        team_member = TeamMember.objects.get(team=team, user=user)
        can_add_customer = team_member.access_level >= 2  # Only level 2 or higher can add customers
    except TeamMember.DoesNotExist:
        can_add_customer = False

    if request.method == 'POST' and can_add_customer:
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            ActivityLog.objects.create(
                team_member=team_member,
                action='Edited Customer:',
                affected_object=f"{customer.name} (Customer)"
        )
            form.save()
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)

    context = {'form' : form, 'customer' : customer, 'can_add_customer' : can_add_customer}        
    return render(request, 'customers/edit_customer.html', context)

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    user = request.user
    team = customer.team
    team_redirect(user, customer.team.id)
    try:
        # Fetch the user's access level in this team
        team_member = TeamMember.objects.get(team=team, user=user)
        can_add_customer = team_member.access_level >= 3  # Only level 3 or higher can add customers
    except TeamMember.DoesNotExist:
        can_add_customer = False

    if request.method == 'POST' and can_add_customer:
        ActivityLog.objects.create(
                team_member=team_member,
                action='Deleted Customer:',
                affected_object=f"{customer.name} (Customer)"
        )
        customer.delete()
        return redirect('customer_list')
    context = {'customer' : customer, 'can_add_customer' : can_add_customer}
    return render(request, 'customers/delete_customer.html', context)
