from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with basic validation.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # Create user using Django's create_user to hash password
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login via username/password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        attrs["user"] = user
        return attrs


# PUBLIC_INTERFACE
class TodoSerializer(serializers.ModelSerializer):
    """
    Serializer for Todo model. Owner is read-only and inferred from request.user.
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        from .models import Todo
        model = Todo
        fields = ("id", "title", "description", "completed", "owner", "created_at", "updated_at")
        read_only_fields = ("id", "owner", "created_at", "updated_at")
