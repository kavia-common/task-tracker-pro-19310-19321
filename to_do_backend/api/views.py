from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login as django_login, logout as django_logout
from .serializers import RegisterSerializer, LoginSerializer

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
