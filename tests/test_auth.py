import pytest
from unittest.mock import MagicMock


@pytest.mark.usefixtures("db")
@pytest.mark.asyncio
async def test_register_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.mailing.service.mail_service", mock_send_email)
    response = client.post("/api/auth/signup", json=user)

    assert response.status_code == 201
    assert response.json()['detail'] == "User successfully created. Check your email for confirmation."
