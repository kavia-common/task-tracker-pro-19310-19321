from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Task, UserProfile
from .serializers import (
    TaskSerializer,
    RegisterSerializer,
    UserPublicSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


@api_view(["GET"])
def health(request):
    """
    PUBLIC_INTERFACE
    Returns a simple health check message.
    """
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Register a new user",
    operation_description="Create a new user account and return the created user and auth token.",
    request_body=RegisterSerializer,
    responses={201: UserPublicSerializer},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Create a user account and return a token for authentication.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"user": UserPublicSerializer(user).data, "token": token.key}, status=status.HTTP_201_CREATED)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Login",
    operation_description="Obtain a token for an existing user. Provide username and password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["username", "password"],
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={"token": openapi.Schema(type=openapi.TYPE_STRING)})},
    tags=["auth"],
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    Authenticate user and return token.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response({"detail": "username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    # Ensure profile exists
    UserProfile.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": UserPublicSerializer(user).data})


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method="post",
    operation_summary="Logout",
    operation_description="Invalidate the current user's token.",
    tags=["auth"],
    responses={204: "No content"},
)
@api_view(["POST"])
def logout(request):
    """
    Delete the current user's token.
    """
    try:
        request.auth.delete()
    except Exception:
        pass
    return Response(status=status.HTTP_204_NO_CONTENT)


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access or edit it.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner_id", None) == request.user.id


# PUBLIC_INTERFACE
class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoints for CRUD operations on tasks.

    list:
      Get a list of the authenticated user's tasks. Supports search by title/description via ?q=
    retrieve:
      Get a specific task by ID (must be owned by the user).
    create:
      Create a new task.
    update/partial_update:
      Update an existing task.
    destroy:
      Delete a task.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.filter(owner=user).order_by("-created_at")
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=["post"], detail=True, url_path="toggle-complete")
    def toggle_complete(self, request, pk=None):
        """
        PUBLIC_INTERFACE
        Toggle the completion status of a task.
        """
        task = self.get_object()
        task.completed = not task.completed
        task.save(update_fields=["completed", "updated_at"])
        return Response(self.get_serializer(task).data)


# PUBLIC_INTERFACE
class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Retrieve and update the authenticated user's profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @swagger_auto_schema(
        method="post",
        operation_summary="Change password",
        operation_description="Change the password for the current user.",
        request_body=ChangePasswordSerializer,
        tags=["profile"],
        responses={204: "No content"},
    )
    @action(methods=["post"], detail=False, url_path="change-password")
    def change_password(self, request):
        """
        PUBLIC_INTERFACE
        Change the current user's password.
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        # Invalidate token to enforce re-login
        Token.objects.filter(user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
