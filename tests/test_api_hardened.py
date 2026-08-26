SENSITIVE_FIELDS = {
    "owner_id",
    "owner_team",
    "budget_eur",
    "internal_location",
    "supplier_access_code",
    "internal_notes",
}
HEADERS = {"X-API-Key": "test-api-key"}


def test_authentication_and_legitimate_functionality(app_factory):
    client, _ = app_factory(hardened=True)

    missing = client.get("/api/v1/projects")
    wrong = client.get("/api/v1/projects", headers={"X-API-Key": "wrong"})
    valid = client.get("/api/v1/projects/1", headers=HEADERS)

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert valid.status_code == 200
    assert valid.json()["id"] == 1


def test_authorization_and_data_minimization(app_factory):
    client, _ = app_factory(hardened=True)

    listing = client.get("/api/v1/projects", headers=HEADERS)
    own = client.get("/api/v1/projects/1", headers=HEADERS)
    other = client.get("/api/v1/projects/2", headers=HEADERS)

    assert listing.status_code == 200
    assert {item["id"] for item in listing.json()["items"]} <= {1, 3, 5, 7, 9, 11}
    assert not SENSITIVE_FIELDS.intersection(listing.json()["items"][0])
    assert not SENSITIVE_FIELDS.intersection(own.json())
    assert other.status_code == 403


def test_query_validation_and_safe_errors(app_factory):
    client, _ = app_factory(hardened=True)

    too_many = client.get("/api/v1/projects", params={"limit": 21}, headers=HEADERS)
    bad_page = client.get("/api/v1/projects", params={"page": 0}, headers=HEADERS)
    bad_status = client.get("/api/v1/projects", params={"status": "secret"}, headers=HEADERS)
    bad_sort = client.get("/api/v1/projects", params={"sort": "missing"}, headers=HEADERS)

    assert {too_many.status_code, bad_page.status_code, bad_status.status_code, bad_sort.status_code} == {422}
    assert "component" not in bad_sort.json()
    assert "x-powered-by" not in bad_sort.headers
    assert bad_sort.headers["x-content-type-options"] == "nosniff"


def test_cors_is_restricted(app_factory):
    client, _ = app_factory(hardened=True)

    denied = client.options(
        "/api/v1/projects",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    allowed = client.options(
        "/api/v1/projects",
        headers={"Origin": "http://127.0.0.1:5500", "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in denied.headers
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5500"


def test_reports_keep_working_and_enforce_ownership(app_factory):
    client, _ = app_factory(hardened=True)

    own = client.post(
        "/api/v1/reports",
        headers=HEADERS,
        json={"project_id": 1, "observation": "Legitieme rapportage blijft mogelijk."},
    )
    other = client.post(
        "/api/v1/reports",
        headers=HEADERS,
        json={"project_id": 2, "observation": "Dit project hoort bij een ander team."},
    )

    assert own.status_code == 201
    assert other.status_code == 403


def test_rate_limit_and_security_logging(app_factory, tmp_path):
    client, app = app_factory(hardened=True)

    responses = [
        client.get(
            "/api/v1/projects/1",
            headers={**HEADERS, "Origin": "http://127.0.0.1:5500"},
        )
        for _ in range(16)
    ]

    assert responses[-1].status_code == 429
    assert responses[-1].headers["x-content-type-options"] == "nosniff"
    assert responses[-1].headers["cache-control"] == "no-store"
    assert responses[-1].headers["access-control-allow-origin"] == "http://127.0.0.1:5500"
    log_files = list(tmp_path.glob("audit-*.log"))
    assert log_files
    log = log_files[0].read_text(encoding="utf-8")
    assert "rate_limit" in log

    app.state.requests.clear()
    client.get("/api/v1/projects/2", headers=HEADERS)
    assert "authorization_denied" in log_files[0].read_text(encoding="utf-8")

    app.state.requests.clear()
    client.get("/api/v1/projects")
    assert "authentication_failed" in log_files[0].read_text(encoding="utf-8")


def test_health_checks_database_readiness(app_factory):
    client, _ = app_factory(hardened=True)

    assert client.get("/health").status_code == 200
