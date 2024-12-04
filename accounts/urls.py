from django.urls import path
from .views import register, CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Use CustomLoginView here
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout')
]