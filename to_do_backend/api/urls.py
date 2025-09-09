from django.urls import path
from .views import health, register, login, logout, RefreshTokenView

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', login, name='auth-login'),
    path('auth/logout/', logout, name='auth-logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
]
