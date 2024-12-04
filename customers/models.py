from django.db import models

# Create your models here.
from teams.models import Team

class Customer(models.Model):
    team = models.ForeignKey(Team, related_name='customers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name