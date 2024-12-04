from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>', views.job_detail, name='job_details'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:pk>/<str:new_status>/', views.change_status, name='change_status'),  

]