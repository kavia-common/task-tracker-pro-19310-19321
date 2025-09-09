from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    """
    Stores extra profile information for a user.
    One-to-one relation with the Django auth User model.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=150, blank=True, default="")
    bio = models.TextField(blank=True, default="")

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()


class Task(TimeStampedModel):
    """
    A to-do task belonging to a user.
    """
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    def __str__(self) -> str:
        return f"{self.title} ({'done' if self.completed else 'todo'})"
