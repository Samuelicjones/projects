from django.contrib import admin
from .models import Team, TeamMember

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'check_access_levels')

    def check_access_levels(self, obj):
        issues = obj.check_access_levels()
        if not issues:
            return "All access levels are correct."
        else:
            return ", ".join(issues)

    check_access_levels.short_description = 'Access Level Check'

admin.site.register(Team, TeamAdmin)