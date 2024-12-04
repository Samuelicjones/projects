from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('customer', 'team_member', 'start_time', 'priority', 'job_status')
    list_filter = ('priority', 'job_status')