from django.urls import path
from . import views



urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete', views.delete_customer, name='delete_customer'),
]