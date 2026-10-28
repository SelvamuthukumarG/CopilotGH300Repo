from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    return TestClient(app_module.app)


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_adds_participant_and_updates_activity_list(client):
    email = "new-student@mergington.edu"

    response = client.post("/activities/Basketball Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Basketball Club"
    activities = client.get("/activities").json()
    assert email in activities["Basketball Club"]["participants"]


def test_signup_rejects_duplicate_without_changing_participants(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants.count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404


def test_unregister_removes_participant_from_activity_list(client):
    email = "michael@mergington.edu"

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_returns_not_found_for_unregistered_email(client):
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": "not-signed-up@mergington.edu"}
    )

    assert response.status_code == 404


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup", params={"email": "student@mergington.edu"}
    )

    assert response.status_code == 404


def test_root_redirects_to_static_homepage(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"