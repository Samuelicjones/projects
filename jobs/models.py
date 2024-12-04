from django.db import models
from customers.models import Customer
from teams.models import TeamMember
from django.utils import timezone
# Create your models here.


class Job(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, related_name='jobs', on_delete=models.CASCADE)
    team_member = models.ForeignKey(TeamMember, related_name='jobs', on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    job_description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    job_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.customer.name} ({self.priority})'