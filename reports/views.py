

'''
Report Fields: 
Job Summary: A general overview of what was done, similar to a "job details" section.
Issues Faced: Any difficulties or obstacles encountered.
Job Completion Time: Record the exact time the job was finished.
Customer Feedback: A section where the team member can record any feedback or satisfaction rating from the customer.
Photos: Allow the team member to upload "before" and "after" photos or any relevant images.
Materials Used: Track any parts or materials used during the job (especially useful for locksmith work).
Payment Details: Add more options like "invoiced" for later billing, or split payments (e.g., part cash, part card).
Signature: If required, allow the customer to sign off on the job via a touchscreen device.

Reports Dashboard:
A place where managers or higher access-level users can view all completed job reports.
Filter reports by date range, team member, customer, or issues raised.
Export reports to PDF or Excel for record-keeping or auditing purposes.

Job Performance Metrics:
Track how long it took for the job to be completed.
Capture recurring issues, trends in customer payment methods, and which team members complete jobs faster.
Visual graphs or charts that summarize reports
'''

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Report, Invoice
from teams.models import TeamMember, ActivityLog
from .forms import ReportForm, InvoiceForm
from jobs.models import Job
from django.db.models import Q
from django.utils import timezone
from teams.views import team_redirect
from decimal import Decimal
from notifications.views import notify_manager_on_job_completion


@login_required
def submit_report(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    team_member = TeamMember.objects.get(user=request.user)
    user = request.user
    team_redirect(user, job.customer.team.id)
    if request.method == 'POST':
        # Assuming you have a form for creating reports
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.job = job
            report.completed_by = job.team_member  # Set the current team member as the one completing the report
            report.save()
            ActivityLog.objects.create(
                team_member=team_member,
                action='Added Report',
                affected_object=f"{job.customer.name} (Job)"
        )
            return redirect('reports:add_invoice', report_id=report.id)
    else:
        form = ReportForm()
    context = {
        'form': form,
    }
    return render(request, 'reports/submit_report.html', context)

def add_invoice(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    customer = report.job.customer  # Assuming each job links to a customer
    user = request.user
    team_redirect(user, customer.team.id)
    # Prefill data
    initial_data = {
        'company_name': customer.name,
        'date': timezone.now().date(),
        'address': customer.address,
        'contact_phone': customer.phone_number,
    }

    if request.method == 'POST':
        form = InvoiceForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Capture the items data manually
            items = []
            subtotal = Decimal('0.00')

            # Loop over the form data (assuming these are coming in as arrays)
            for i in range(len(request.POST.getlist('quantity[]'))):
                quantity = int(request.POST.getlist('quantity[]')[i])
                description = request.POST.getlist('description[]')[i]
                price = Decimal(request.POST.getlist('price[]')[i])
                total_amount = quantity * price

                items.append({
                    'quantity': quantity,
                    'description': description,
                    'price': float(price),
                    'total_amount': float(total_amount)
                })
                subtotal += total_amount

            # Create the invoice object and save it
            invoice = form.save(commit=False)
            invoice.report = report
            invoice.items = items  # Save the items list in the JSON field
            invoice.subtotal = subtotal
            invoice.calculate_totals()  # Ensure this still works as expected
            invoice.save()
            # notify_manager_on_job_completion(report)
            return redirect('reports:report_details', report_id=report_id)
        else:
            print(form.errors)
            
    else:
        form = InvoiceForm(initial=initial_data)

    context = {
        'form': form,
        'report': report,
        'initial_data': initial_data,
    }

    return render(request, 'reports/add_invoice.html', context)


@login_required
def reports_list(request):
    # Check if user has access level 3 or higher
    team_member = TeamMember.objects.get(user=request.user)
    team = team_member.team
    access_level = team_member.access_level

    if team_member.access_level < 3:
        return redirect('dashboard')  # Redirect lower access levels to a different page


    reports = Report.objects.filter(job__team_member__team=team)
    query = request.GET.get('q')
    if query:
        reports = reports.filter(
            Q(completed_by__user__first_name__icontains=query) |  # Assuming customer name for filtering
            Q(completed_at__icontains=query) |  # Assuming team_member has a ForeignKey to User
            Q(payment_method__icontains=query) |  # This may need adjustment if 'start_time' is a DateTimeField
            Q(job__customer__name__icontains=query)
        )
  
    context = {
        'reports': reports,
        'access_level': access_level,
    }
    return render(request, 'reports/reports_list.html', context)


@login_required
def report_details(request, report_id):
    team_member = TeamMember.objects.get(user=request.user)
    access_level = team_member.access_level
    report = get_object_or_404(Report, id=report_id)
    user = request.user
    team_redirect(user, report.job.customer.team.id)
    context = {
        'report': report,
        'team_member': team_member,
        'access_level': access_level,
    }
    return render(request, 'reports/report_details.html', context)