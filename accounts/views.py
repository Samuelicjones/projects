from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

@login_required
def redirect_view(request):
    user = request.user
    teams = user.teams.all()
    
    if teams.exists():
        return redirect('team_dashboard', team_slug=teams.first().slug)  # Redirect to the dashboard
    else:
        return redirect('create_team_or_invite')
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()
    context = {'form': form}    
    return render(request, 'accounts/register.html', context)
