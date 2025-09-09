from rest_framework.test import APITestCase
from django.urls import reverse

class HealthTests(APITestCase):
    """
    Tests for the health check endpoint.
    """
    def test_health(self):
        url = reverse('Health')  # Ensure URL name matches api/urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"message": "Server is up!"})
