"""Tests for expense creation, listing, and the approve/reject workflow."""

SAMPLE_EXPENSE = {
    "description": "Team lunch",
    "submitted_by": "bob",
    "category": "meals",
    "amount_minor": 250000,
    "currency": "INR",
}


def test_create_expense_success(client):
    response = client.post("/expenses", json=SAMPLE_EXPENSE)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    assert body["amount_minor"] == 250000
    assert body["currency"] == "INR"


def test_create_expense_rejects_non_positive_amount(client):
    for bad_amount in (0, -100):
        payload = {**SAMPLE_EXPENSE, "amount_minor": bad_amount}
        response = client.post("/expenses", json=payload)
        assert response.status_code == 422


def test_list_expenses_filters_by_status_and_category(client):
    meal = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    travel = client.post(
        "/expenses",
        json={**SAMPLE_EXPENSE, "category": "travel", "currency": "USD", "amount_minor": 15000},
    ).json()
    client.post(f"/expenses/{meal['id']}/approve")

    by_category = client.get("/expenses", params={"category": "travel"}).json()
    assert [e["id"] for e in by_category] == [travel["id"]]

    by_status = client.get("/expenses", params={"status": "approved"}).json()
    assert [e["id"] for e in by_status] == [meal["id"]]


def test_get_expense_404(client):
    response = client.get("/expenses/999")
    assert response.status_code == 404


def test_approve_then_double_approve_returns_409(client):
    expense = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    first = client.post(f"/expenses/{expense['id']}/approve")
    assert first.status_code == 200
    assert first.json()["status"] == "approved"

    second = client.post(f"/expenses/{expense['id']}/approve")
    assert second.status_code == 409


def test_reject_then_approve_returns_409(client):
    expense = client.post("/expenses", json=SAMPLE_EXPENSE).json()
    rejected = client.post(f"/expenses/{expense['id']}/reject")
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    approve_after_reject = client.post(f"/expenses/{expense['id']}/approve")
    assert approve_after_reject.status_code == 409
