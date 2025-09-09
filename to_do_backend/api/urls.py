from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, TaskViewSet, ProfileViewSet, register, login, logout

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("health/", health, name="Health"),
    path("auth/register/", register, name="Register"),
    path("auth/login/", login, name="Login"),
    path("auth/logout/", logout, name="Logout"),
    path("", include(router.urls)),
]
