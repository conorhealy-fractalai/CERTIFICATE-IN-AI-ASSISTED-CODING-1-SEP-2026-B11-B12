"""Tests for the /health endpoint."""


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "count": 0}


def test_health_count_increments_after_create(client):
    client.post(
        "/expenses",
        json={
            "description": "Taxi",
            "submitted_by": "carol",
            "category": "travel",
            "amount_minor": 4250,
            "currency": "INR",
        },
    )
    response = client.get("/health")
    assert response.json()["count"] == 1
