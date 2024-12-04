from django.db import models
from jobs.models import Job
from teams.models import TeamMember
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


class Report(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('billed', 'Billed'),
    ]

    job = models.OneToOneField(Job, on_delete=models.CASCADE)  # Each job can have one report
    completed_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    job_details = models.TextField()  # Field for any job-related details or issues
    job_issues = models.TextField(blank=True, null=True)    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_received = models.BooleanField(default=False)
    additional_image = models.ImageField(upload_to='reports_images/', blank=True, null=True)


    

    def __str__(self):
        return f"Report for {self.job}"





class Invoice(models.Model):
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    address = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)


    items = models.JSONField(default=list, blank=True, help_text="List of items: [{'quantity': 2, 'description': 'Lock', 'price': 25.00, 'total_amount': 50.00}, ...]")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))


    def calculate_totals(self):
    # Ensure that the subtotal is a Decimal
        TAX_RATE = Decimal('0.085')
        self.subtotal = sum(Decimal(str(item['quantity'])) * Decimal(str(item['price'])) for item in self.items)
        
        self.tax = (self.subtotal * TAX_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        # Ensure that the total is also a Decimal
        self.total = self.subtotal + self.tax
        
        # Save the updated instance
        self.save()
            
    def __str__(self):
        return f"Invoice for {self.report.job.customer.name} - {self.report.job.job_name}"