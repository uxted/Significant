"""Pytest configuration for Django."""

import pytest
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


@pytest.fixture
def auth_client(client, django_user_model):
    """Authenticated test client."""
    user = django_user_model.objects.create_user(
        email="test@test.com",
        password="testpassword123",
    )
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def admin_client(client, django_user_model):
    """Admin authenticated test client."""
    user = django_user_model.objects.create_user(
        email="admin@test.com",
        password="adminpassword123",
        role=django_user_model.Role.ADMIN,
    )
    client.force_login(user)
    client.user = user
    return client
