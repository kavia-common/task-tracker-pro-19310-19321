from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Task, UserProfile

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Public view of a user."""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation."""
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer to change the password for the current user."""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["user", "display_name", "bio", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at", "user"]


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    owner = UserPublicSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "due_date",
            "priority",
            "owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
