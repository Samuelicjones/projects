# Generated by Django 5.1.1 on 2024-09-24 18:56

import uuid
from django.db import migrations, models
from django.utils.text import slugify

def generate_unique_slugs(apps, schema_editor):
    Team = apps.get_model('teams', 'Team')
    for team in Team.objects.all():
        if not team.slug:  # Only generate slugs for teams without one
            base_slug = slugify(team.name)
            slug = base_slug
            counter = 1

            # Ensure the slug is unique
            while Team.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            team.slug = slug
            team.save()

class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_teammember'),  # Update with the correct previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='slug',
            field=models.SlugField(max_length=50, unique=True, blank=True),
        ),
        migrations.RunPython(generate_unique_slugs),  # Run the function to generate slugs
    ]