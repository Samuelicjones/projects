from django import forms
from .models import Report, Invoice

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['job_details', 'job_issues', 'payment_method', 'payment_received', 'additional_image']
        widgets = {
            'job_details': forms.Textarea(attrs={'rows': 4}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        
        fields = ['company_name', 'contact_name', 'address', 'contact_phone', 'items']