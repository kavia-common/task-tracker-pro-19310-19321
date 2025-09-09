from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


# PUBLIC_INTERFACE
class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for representing and updating the authenticated user's profile.

    Fields:
    - id (read-only)
    - username
    - email
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id",)
