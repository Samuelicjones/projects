import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Ensure the slug is unique by checking for existing slugs
        original_slug = self.slug
        counter = 1
        while Team.objects.filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1

        super().save(*args, **kwargs)

    def add_member(self, user, access_level=1):
        """Add a user to the team and create a TeamMember object with the given access level."""
        self.members.add(user)
        # Ensure a TeamMember entry is created
        TeamMember.objects.get_or_create(team=self, user=user, defaults={'access_level': access_level})

    def remove_member(self, user):
        """Remove a user from the team and delete their TeamMember entry."""
        self.members.remove(user)
        TeamMember.objects.filter(team=self, user=user).delete()


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   
    
    ACCESS_LEVEL = (
        (1, 'View Only'),
        (2, 'Add Customers and Jobs'),
        (3, 'Manage Team Members'),
        (4, 'Full Access'),
    )

    access_level = models.IntegerField(choices=ACCESS_LEVEL, default=1)

    class Meta:
        unique_together = ('team', 'user')

def __str__(self):
    if self.user.first_name and self.user.last_name:
        return f'{self.user.first_name} {self.user.last_name} ({self.get_access_level_display()})'
    return f'{self.user.username} ({self.get_access_level_display()})'



class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('completed', 'Completed'),
    ]

    team_member = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    affected_object = models.CharField(max_length=255)  # To store a description of the affected object
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.team_member} {self.action} {self.affected_object} at {self.timestamp}"