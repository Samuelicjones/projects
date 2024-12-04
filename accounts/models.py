from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
        ('manager', 'Manager'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    is_active = models.BooleanField(default=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Add related_name to fix the clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )
