from django.contrib.auth.decorators import login_required

def access_level_context(request):
    # Ensure user is authenticated and belongs to a team
    if request.user.is_authenticated and hasattr(request.user, 'team_member'):
        user_team = request.user.team_member.team
        access_level = request.user.team_member.access_level
        return {
            'access_level': access_level,
            'team_name': user_team.name,
        }
    return {}

