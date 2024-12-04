from django.urls import path
from . import views

urlpatterns = [
    path('create-or-invite/', views.create_team_or_invite_view, name='create_team_or_invite'), 
    path('create_team/', views.create_team, name='create_team'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('join/', views.display_join_team, name='display_join_team'),  # Changed this name for clarity
    path('join/team/', views.join_team, name='join_team'),  # This processes the form submission
    path('team-dashboard/<slug:team_slug>/', views.team_dashboard, name='team_dashboard'),
    path('teams/<slug:team_slug>/members/<int:member_id>/', views.team_member_profile, name='team_member_profile'),
    path('full_activity_log/', views.full_activity_log, name='full_activity_log'),


]
