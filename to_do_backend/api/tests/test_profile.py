import unittest
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@unittest.skip("User profile endpoints not yet implemented")
class UserProfileTests(APITestCase):
    """
    Placeholder tests for user profile retrieval and update.
    Skipped until the corresponding endpoints are implemented.
    """
    def setUp(self):
        self.username = "profile_user"
        self.email = "profile_user@example.com"
        self.password = "StrongPass123!"
        User.objects.create_user(username=self.username, email=self.email, password=self.password)
        # Authenticate
        login_url = reverse("auth-login")
        res_login = self.client.post(login_url, data={"username": self.username, "password": self.password}, format="json")
        token = res_login.data.get("token") or res_login.data.get("access")
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_get_profile(self):
        url = reverse("user-profile")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get("username"), self.username)
        self.assertEqual(res.data.get("email"), self.email)

    def test_update_profile(self):
        url = reverse("user-profile")
        new_email = "updated@example.com"
        res = self.client.patch(url, data={"email": new_email}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get("email"), new_email)
