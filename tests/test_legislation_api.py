import os

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_returns_extractive_answer_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post(
        "/api/v1/legislation/ask",
        json={"question": "What is the Zvw employer contribution rate?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["generated_by_llm"] is False
    assert len(data["sources"]) >= 1
    assert "6.10" in data["answer"] or "Zvw" in data["answer"]


def test_ask_with_no_matching_content_says_so_rather_than_guessing():
    response = client.post(
        "/api/v1/legislation/ask",
        json={"question": "What time does the Amsterdam office open?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == []
    assert data["generated_by_llm"] is False


def test_response_never_contains_employee_shaped_fields():
    response = client.post(
        "/api/v1/legislation/ask",
        json={"question": "What is the algemene heffingskorting for 2026?"},
    )
    data = response.json()
    assert "employee_id" not in data
    assert "employee_name" not in data
    assert "gross" not in data
