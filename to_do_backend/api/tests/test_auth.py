import unittest
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@unittest.skip("Authentication endpoints not yet implemented")
class AuthenticationTests(APITestCase):
    """
    Placeholder tests for user authentication flows.
    Skipped until the corresponding endpoints are implemented.
    """

    def setUp(self):
        # Create a user to test login functionality
        self.username = "testuser"
        self.password = "StrongPass123!"
        self.email = "testuser@example.com"
        User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_register(self):
        """
        Expect: POST /api/auth/register/ creates a new user and returns 201 with user data.
        """
        url = reverse("auth-register")
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123!",
        }
        res = self.client.post(url, data=payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("id", res.data)
        self.assertEqual(res.data.get("username"), payload["username"])

    def test_login(self):
        """
        Expect: POST /api/auth/login/ returns 200 and a token/session.
        """
        url = reverse("auth-login")
        payload = {"username": self.username, "password": self.password}
        res = self.client.post(url, data=payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue("token" in res.data or "access" in res.data)

    def test_access_protected_resource_requires_auth(self):
        """
        Expect: Accessing a protected endpoint without auth returns 401.
        """
        url = reverse("todos-list")  # Assuming DRF router for todos
        res = self.client.get(url)
        self.assertIn(res.status_code, (401, 403))

    def test_logout(self):
        """
        Expect: POST /api/auth/logout/ invalidates token/session and returns 204/200.
        """
        # First log in to obtain token/session
        login_url = reverse("auth-login")
        res_login = self.client.post(login_url, data={"username": self.username, "password": self.password}, format="json")
        self.assertEqual(res_login.status_code, 200)
        token = res_login.data.get("token") or res_login.data.get("access")
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("auth-logout")
        res = self.client.post(url)
        self.assertIn(res.status_code, (200, 204))

    def test_token_refresh(self):
        """
        Expect: POST /api/auth/refresh/ returns new access token given a valid refresh token.
        """
        url = reverse("auth-refresh")
        res = self.client.post(url, data={"refresh": "dummy"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
