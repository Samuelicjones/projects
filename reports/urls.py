from django.urls import path
from . import views

app_name = 'reports' 

urlpatterns = [
    path('submit/<int:job_id>/', views.submit_report, name='submit_report'),
    path('list/', views.reports_list, name='reports_list'),
    path('add_invoice/<int:report_id>/', views.add_invoice, name='add_invoice'),
    path('<int:report_id>/', views.report_details, name='report_details'),  # New detail page

]


