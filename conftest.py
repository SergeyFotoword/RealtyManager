# conftest.py
import pytest
from rest_framework.test import APIClient
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def client():
    """
    Django test client (аналог self.client в TestCase)
    """
    return Client()


@pytest.fixture
def api_client():
    """
    DRF APIClient (аналог self.client в APITestCase)
    """
    return APIClient()

@pytest.fixture
def user(db):
    """
    Basic user without rights and roles
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
    )


@pytest.fixture
def auth_client(api_client, user):
    """
    APIClient with an authorized user
    """
    api_client.force_authenticate(user=user)
    return api_client