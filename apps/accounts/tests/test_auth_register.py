import pytest
from django.contrib.auth import get_user_model

from apps.accounts.models.profile import UserProfile
from apps.accounts.models.role import Role

User = get_user_model()


@pytest.mark.django_db
def test_register_success(api_client):
    payload = {
        "name": "Sergey Galushka",
        "email": "sergey@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    resp = api_client.post("/api/auth/register/", payload, format="json")
    assert resp.status_code == 201, resp.data

    data = resp.data
    assert data["email"] == "sergey@example.com"
    assert "access" in data and data["access"]
    assert "refresh" in data and data["refresh"]
    assert "profile_public_id" in data

    user = User.objects.get(email="sergey@example.com")
    assert user.username == "sergey@example.com"  # default behavior
    assert UserProfile.objects.filter(user=user).exists()

    assert Role.objects.filter(name="tenant").exists()
    assert user.roles.filter(name="tenant").exists()


@pytest.mark.django_db
def test_register_duplicate_email(api_client, user_factory):
    user_factory(email="dup@example.com", username="dup_user")

    payload = {
        "name": "Dup",
        "email": "dup@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    resp = api_client.post("/api/auth/register/", payload, format="json")
    assert resp.status_code == 400
    assert "email" in resp.data


@pytest.mark.django_db
def test_register_password_mismatch(api_client):
    payload = {
        "name": "Test",
        "email": "mismatch@example.com",
        "password": "StrongPass123!",
        "password2": "OtherPass123!",
    }

    resp = api_client.post("/api/auth/register/", payload, format="json")
    assert resp.status_code == 400
    assert "password2" in resp.data