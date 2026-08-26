def test_normal_response_and_json_structure(app_factory):
    client, _ = app_factory()

    response = client.get("/api/v1/projects", params={"page": 1, "limit": 3})

    assert response.status_code == 200
    assert response.headers["x-total-count"] == "12"
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 3
    assert body["next_page"] == 2
    assert len(body["items"]) == 3
    assert {"id", "title", "status", "category", "summary"} <= body["items"][0].keys()


def test_vulnerable_state_is_observable(app_factory):
    client, _ = app_factory()

    no_auth = client.get("/api/v1/projects/2")
    unlimited = client.get("/api/v1/projects", params={"limit": 1000})

    assert no_auth.status_code == 200
    assert no_auth.json()["owner_id"] == 102
    assert "supplier_access_code" in no_auth.json()
    assert unlimited.status_code == 200
    assert len(unlimited.json()["items"]) == 12
    assert unlimited.headers["x-powered-by"].startswith("FastAPI")


def test_vulnerable_error_leaks_technical_details(app_factory):
    client, _ = app_factory()

    response = client.get("/api/v1/projects", params={"sort": "missing_column"})

    assert response.status_code == 500
    assert response.json()["exception"] == "RuntimeError"
    assert "SQLite" in response.json()["component"]
    assert "ORDER BY" in response.json()["detail"]


def test_vulnerable_cors_and_no_rate_limit(app_factory):
    client, app = app_factory()

    preflight = client.options(
        "/api/v1/projects",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    statuses = [client.get("/api/v1/projects/1").status_code for _ in range(20)]

    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "*"
    assert 429 not in statuses
    assert not app.state.settings.rate_limit_and_log


def test_post_and_error_statuses(app_factory):
    client, _ = app_factory()

    created = client.post(
        "/api/v1/reports",
        json={"project_id": 1, "observation": "De sensor geeft geldige fictieve waarden."},
    )
    missing = client.get("/api/v1/projects/999")
    invalid = client.post("/api/v1/reports", json={"project_id": 1, "observation": "kort"})

    assert created.status_code == 201
    assert created.json()["status"] == "created"
    assert missing.status_code == 404
    assert invalid.status_code == 422
