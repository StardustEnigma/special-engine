from django.db import models

# Reusable tech tags (Django, Tailwind, ML, etc.)
class TechTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# Main project model
class Project(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="thumbnails/")  # Changed from "projects/thumbnails/"

    # Links
    github_link = models.URLField(blank=True, null=True)
    live_demo_link = models.URLField(blank=True, null=True)

    # Relationships
    tech_stack = models.ManyToManyField(TechTag, related_name="projects", blank=True)

    # Flags
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

# Extra screenshots (dashboards, MVP pics, feature UIs)
class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="screenshots/")  # Changed from "projects/screenshots/"
    caption = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.project.title} - {self.caption or 'Screenshot'}"

from django.db import models


class ContactMessage(models.Model):
    # User input fields
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField()

    # Extra metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # to track if you read/responded
    replied = models.BooleanField(default=False)  # if you replied manually

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
