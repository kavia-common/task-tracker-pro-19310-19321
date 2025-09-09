from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, register, login, logout, RefreshTokenView, TodoViewSet

router = DefaultRouter()
# This will expose names 'todos-list' and 'todos-detail'
router.register(r'todos', TodoViewSet, basename='todos')

urlpatterns = [
    path('health/', health, name='Health'),
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', login, name='auth-login'),
    path('auth/logout/', logout, name='auth-logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='auth-refresh'),
    path('', include(router.urls)),
]
