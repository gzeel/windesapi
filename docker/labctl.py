#!/usr/bin/env python3
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


WORKSPACE = Path(os.environ.get("LAB_WORKSPACE", "/workspace"))
TEMPLATE = Path("/opt/lab-template")
SETTINGS = WORKSPACE / "lab-settings.json"
KEY_FILE = WORKSPACE / ".api-key"
DB_FILE = Path(os.environ.get("LAB_DB_PATH", WORKSPACE / "lab.db"))
AUDIT_FILE = Path(os.environ.get("LAB_AUDIT_LOG_PATH", WORKSPACE / "audit.log"))
BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def reset() -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    workspace_owner = WORKSPACE.stat()
    WORKSPACE.chmod(0o777)
    target_app = WORKSPACE / "app"
    if target_app.exists():
        shutil.rmtree(target_app)
    shutil.copytree(TEMPLATE / "app", target_app)
    shutil.copy2(TEMPLATE / "lab-settings.json", SETTINGS)
    for name in ("client.py", "rapportage.md"):
        target = WORKSPACE / name
        if not target.exists():
            shutil.copy2(TEMPLATE / "templates" / name, target)
    KEY_FILE.write_text(secrets.token_urlsafe(32) + "\n", encoding="utf-8")
    if os.geteuid() == 0:
        owned_paths = [target_app, SETTINGS]
        owned_paths.extend(WORKSPACE / name for name in ("client.py", "rapportage.md"))
        for owned_path in owned_paths:
            if owned_path.is_dir():
                for path in [owned_path, *owned_path.rglob("*")]:
                    os.chown(path, workspace_owner.st_uid, workspace_owner.st_gid)
            elif owned_path.exists():
                os.chown(owned_path, workspace_owner.st_uid, workspace_owner.st_gid)
        os.chown(KEY_FILE, workspace_owner.st_uid, 10001)
        KEY_FILE.chmod(0o640)
    else:
        KEY_FILE.chmod(0o600)
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(WORKSPACE)
    subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; from app.database import reset_database; "
            f"reset_database(Path({str(DB_FILE)!r}))",
        ],
        cwd=WORKSPACE,
        env=environment,
        check=True,
    )
    if os.geteuid() == 0:
        os.chown(DB_FILE, 10001, 10001)
        DB_FILE.chmod(0o660)
    print(f"Beginsituatie hersteld in {WORKSPACE}")
    print("Eigen client.py en rapportage.md zijn behouden; de API-code en instellingen zijn hersteld.")
    print("Start de API opnieuw zodat herstelde code en instellingen actief worden.")


def ensure_workspace() -> None:
    if not (WORKSPACE / "app" / "main.py").exists() or not SETTINGS.exists():
        reset()


def request(path: str, key: str | None = None, method: str = "GET", data: bytes | None = None):
    headers = {"Accept": "application/json"}
    if key:
        headers["X-API-Key"] = key
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = Request(f"{BASE_URL}{path}", headers=headers, method=method, data=data)
    try:
        with urlopen(req, timeout=4) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, headers, json.loads(response.read())
    except HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        headers = {key.lower(): value for key, value in exc.headers.items()}
        return exc.code, headers, body


def status_check() -> int:
    ensure_workspace()
    try:
        code, _, health = request("/health")
        key = KEY_FILE.read_text(encoding="utf-8").strip() if KEY_FILE.exists() else None
        project_code, _, project = request("/api/v1/projects/1", key)
    except (OSError, URLError) as exc:
        print(f"NIET BEREIKBAAR: {exc}")
        return 1
    if code == 200 and health.get("status") == "ok" and project_code == 200 and project.get("id") == 1:
        print("OK: healthcheck en legitieme projectrequest werken.")
        return 0
    print(f"FOUT: health={code}, legitieme projectrequest={project_code}")
    return 1


def lab_check() -> int:
    ensure_workspace()
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    checks = []
    try:
        no_key, _, _ = request("/api/v1/projects")
        checks.append(("API-key verplicht", no_key == 401))
        own, _, own_body = request("/api/v1/projects/1", key)
        checks.append(("Legitieme toegang blijft werken", own == 200 and own_body.get("id") == 1))
        other, _, _ = request("/api/v1/projects/2", key)
        checks.append(("Objectautorisatie", other == 403))
        listing, _, body = request("/api/v1/projects?limit=5", key)
        leaked = {"budget_eur", "internal_location", "supplier_access_code", "internal_notes", "owner_id", "owner_team"}
        checks.append(("Dataminimalisatie", listing == 200 and body.get("items") and not leaked.intersection(body["items"][0])))
        invalid, _, _ = request("/api/v1/projects?limit=100", key)
        checks.append(("Validatie en paginalimiet", invalid == 422))
        error, error_headers, error_body = request("/api/v1/projects?sort=bestaat_niet", key)
        safe_error = (
            error == 422
            and "component" not in error_body
            and "x-powered-by" not in error_headers
            and error_headers.get("x-content-type-options") == "nosniff"
            and error_headers.get("cache-control") == "no-store"
        )
        checks.append(("Veilige fouten en headers", safe_error))

        rate_limited = False
        for _ in range(18):
            rate_code, _, _ = request("/api/v1/projects/1", key)
            if rate_code == 429:
                rate_limited = True
                break
        checks.append(("Rate limiting", rate_limited))
        audit_log = AUDIT_FILE.read_text(encoding="utf-8") if AUDIT_FILE.exists() else ""
        logged_events = all(event in audit_log for event in ("authentication_failed", "authorization_denied", "rate_limit"))
        checks.append(("Beveiligingslogging", logged_events))
    except (OSError, URLError) as exc:
        print(f"API niet bereikbaar: {exc}")
        return 1

    for label, passed in checks:
        print(f"{'OK' if passed else 'NOG NIET'}: {label}")
    return 0 if all(passed for _, passed in checks) else 1


def start() -> None:
    ensure_workspace()
    os.chdir(WORKSPACE)
    os.environ.setdefault("LAB_SETTINGS_PATH", str(SETTINGS))
    os.environ.setdefault("LAB_API_KEY_FILE", str(KEY_FILE))
    os.environ.setdefault("LAB_DB_PATH", str(DB_FILE))
    os.environ.setdefault("LAB_AUDIT_LOG_PATH", str(AUDIT_FILE))
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"],
    )


def show_log() -> int:
    if not AUDIT_FILE.exists():
        print("Nog geen auditlog gevonden.")
        return 0
    lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines[-30:]:
        print(line)
    return 0


def help_text() -> None:
    print(
        """WindesAPI lokaal onderwijs-lab

lab-reset   Herstel API-code en kwetsbare instellingen vanuit het image (via compose run).
lab-start   Start de API (standaardcommando van de API-service).
lab-status  Test bereikbaarheid en legitieme functionaliteit.
lab-check   Controleer de zes beveiligingsmaatregelen via gedrag.
lab-log     Toon de laatste beveiligingslogregels.
lab-help    Toon deze hulp.

Start en stop containers op de host met docker compose up -d en docker compose down.
Gebruik dit lab uitsluitend lokaal met de fictieve meegeleverde data."""
    )


def main() -> int:
    command = Path(sys.argv[0]).name
    if command == "lab-reset":
        reset()
        return 0
    if command == "lab-start":
        start()
        return 0
    if command == "lab-status":
        return status_check()
    if command == "lab-check":
        return lab_check()
    if command == "lab-log":
        return show_log()
    help_text()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
