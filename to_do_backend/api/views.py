from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import RegisterSerializer, LoginSerializer, TodoSerializer

# SimpleJWT imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.

    Request body:
    - username: string
    - email: string
    - password: string

    Returns:
    - 201 with created user data (id, username, email)
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        data = {"id": user.id, "username": user.username, "email": user.email}
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint returning JWT access and refresh tokens.

    Request body:
    - username: string
    - password: string

    Returns:
    - 200 with { access, refresh, user }
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        django_login(request, user)  # optional: maintain session for browsable API
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"id": user.id, "username": user.username, "email": user.email},
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint.

    If refresh token provided, attempts to blacklist it (stateless logout).
    Always clears the Django session.

    Request body (optional):
    - refresh: string (refresh token to blacklist)

    Returns:
    - 204 No Content on success
    """
    # End Django session
    django_logout(request)

    # Try to blacklist provided refresh token if exists and blacklist enabled
    refresh_token = request.data.get("refresh")
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            # If blacklist app were installed, this would blacklist
            # But without blacklist app, calling .blacklist() will fail.
            # So attempt and ignore if unsupported.
            try:
                token.blacklist()  # no-op if blacklist not configured
            except Exception:
                pass
        except Exception:
            # Ignore invalid token in logout
            pass

    return Response(status=status.HTTP_204_NO_CONTENT)


# PUBLIC_INTERFACE
class RefreshTokenView(TokenRefreshView):
    """
    Obtain new access token given a refresh token.

    Request body:
    - refresh: string

    Returns:
    - 200 with { access }
    """
    pass


# PUBLIC_INTERFACE
class TodoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for authenticated CRUD operations on user-owned Todo items.

    Security:
    - Requires JWT (Bearer) or session authentication.
    - Results are scoped to request.user.
    - On create, owner is automatically set to request.user.

    Endpoints (via router):
    - GET /api/todos/ -> list (name: todos-list)
    - POST /api/todos/ -> create
    - GET /api/todos/{pk}/ -> retrieve (name: todos-detail)
    - PATCH /api/todos/{pk}/ -> partial_update
    - PUT /api/todos/{pk}/ -> update
    - DELETE /api/todos/{pk}/ -> destroy
    """
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication, SessionAuthentication]

    def get_queryset(self):
        # Import locally to avoid circular imports at module load for migrations
        from .models import Todo
        # Restrict to items owned by the authenticated user
        return Todo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign owner to the authenticated user
        serializer.save(owner=self.request.user)
