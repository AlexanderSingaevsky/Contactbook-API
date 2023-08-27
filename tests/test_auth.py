import pytest
from unittest.mock import MagicMock


@pytest.mark.usefixtures("db")
@pytest.mark.asyncio
async def test_register_user(client, user, monkeypatch):
    monkeypatch.setattr("src.mailing.service.mail_service", MagicMock())
    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 201
    assert response.json()['detail'] == "User successfully created. Check your email for confirmation."


@pytest.mark.usefixtures("db")
@pytest.mark.asyncio
async def test_register_existing_user(client, user, monkeypatch):
    async def mock_get_user_by_email(a, b):
        return True
    monkeypatch.setattr("src.mailing.service.mail_service", MagicMock())
    monkeypatch.setattr('src.auth.repository.get_user_by_email', mock_get_user_by_email)
    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 409
    assert response.json()['detail'] == "Account already exists"
