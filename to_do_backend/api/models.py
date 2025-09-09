from django.conf import settings
from django.db import models


class Todo(models.Model):
    """
    A to-do item owned by a user.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="todos",
        help_text="Owner of the to-do item",
    )
    title = models.CharField(max_length=255, help_text="Short title of the task")
    description = models.TextField(blank=True, help_text="Detailed description of the task")
    completed = models.BooleanField(default=False, help_text="Whether the task is completed")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({'done' if self.completed else 'pending'})"
