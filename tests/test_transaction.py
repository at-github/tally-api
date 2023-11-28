from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_read_transaction():
    response = client.get('/transactions/1')
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "amount": 800,
        "date": "2024-01-01"
    }
