import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def app_factory(tmp_path: Path):
    clients = []

    def factory(hardened: bool = False):
        settings = {
            "require_api_key": hardened,
            "enforce_project_ownership": hardened,
            "minimal_responses": hardened,
            "validate_queries": hardened,
            "safe_errors_headers_cors": hardened,
            "rate_limit_and_log": hardened,
        }
        settings_path = tmp_path / f"settings-{len(clients)}.json"
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        key_path = tmp_path / "api.key"
        key_path.write_text("test-api-key\n", encoding="utf-8")
        app = create_app(
            settings_path=settings_path,
            db_path=tmp_path / f"lab-{len(clients)}.db",
            api_key_path=key_path,
            audit_log_path=tmp_path / f"audit-{len(clients)}.log",
        )
        client = TestClient(app, raise_server_exceptions=False)
        client.__enter__()
        clients.append(client)
        return client, app

    yield factory

    for client in clients:
        client.__exit__(None, None, None)
