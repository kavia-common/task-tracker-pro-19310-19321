from django.contrib import admin
from .models import Task, UserProfile


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "completed", "priority", "due_date", "created_at")
    list_filter = ("completed", "priority", "created_at")
    search_fields = ("title", "description", "owner__username")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name", "created_at", "updated_at")
    search_fields = ("user__username", "display_name")
