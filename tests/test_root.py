from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_not_found():
    response = client.get("/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
