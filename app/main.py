import json
import os
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.database import ensure_database, get_connection, row_to_dict
from app.settings import LabSettings, load_settings


PUBLIC_PROJECT_FIELDS = {"id", "title", "status", "category", "summary"}
VALID_STATUSES = {"active", "paused", "completed"}
VALID_SORTS = {"id", "title", "status", "category"}


class ReportInput(BaseModel):
    project_id: int = Field(ge=1)
    observation: str = Field(min_length=10, max_length=500)


def create_app(
    settings_path: Path | None = None,
    db_path: Path | None = None,
    api_key_path: Path | None = None,
    audit_log_path: Path | None = None,
) -> FastAPI:
    settings = load_settings(settings_path)
    database_path = db_path or Path(os.environ.get("LAB_DB_PATH", "data/lab.db"))
    key_path = api_key_path or Path(os.environ.get("LAB_API_KEY_FILE", ".api-key"))
    log_path = audit_log_path or Path(os.environ.get("LAB_AUDIT_LOG_PATH", "audit.log"))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        ensure_database(database_path)
        yield

    api = FastAPI(
        title="WindesAPI lokaal onderwijs-lab",
        description="Bewust kwetsbare, uitsluitend lokale API met fictieve projectdata.",
        version="3.0.0-lab",
        lifespan=lifespan,
    )
    api.state.settings = settings
    api.state.requests = defaultdict(deque)
    api.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5500"] if settings.safe_errors_headers_cors else ["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key"],
        expose_headers=["X-Page", "X-Total-Count"],
    )

    def audit(event: str, request: Request, detail: str) -> None:
        if not settings.rate_limit_and_log:
            return
        log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "time": int(time.time()),
            "event": event,
            "client": request.client.host if request.client else "unknown",
            "path": request.url.path,
            "detail": detail,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    @api.middleware("http")
    async def security_controls(request: Request, call_next):
        if settings.rate_limit_and_log and request.url.path != "/health":
            client = request.client.host if request.client else "unknown"
            now = time.monotonic()
            attempts = api.state.requests[client]
            while attempts and now - attempts[0] > 10:
                attempts.popleft()
            if len(attempts) >= 15:
                audit("rate_limit", request, "meer dan 15 requests in 10 seconden")
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Te veel requests; probeer het later opnieuw."},
                    headers={"Retry-After": "10"},
                )
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["Cache-Control"] = "no-store"
                if request.headers.get("origin") == "http://127.0.0.1:5500":
                    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
                    response.headers["Vary"] = "Origin"
                return response
            attempts.append(now)

        response = await call_next(request)
        if settings.safe_errors_headers_cors:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["X-Powered-By"] = "FastAPI/Uvicorn (training leak)"
        return response

    @api.exception_handler(RequestValidationError)
    async def request_validation_handler(_: Request, exc: RequestValidationError):
        if settings.safe_errors_headers_cors:
            return JSONResponse(status_code=422, content={"detail": "Ongeldige invoer."})
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @api.exception_handler(Exception)
    async def unhandled_error(_: Request, exc: Exception):
        if settings.safe_errors_headers_cors:
            return JSONResponse(status_code=500, content={"detail": "Interne fout."})
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "exception": type(exc).__name__,
                "component": "FastAPI + SQLite",
                "database": str(database_path),
            },
        )

    def current_user(
        request: Request,
        x_api_key: Annotated[str | None, Header()] = None,
    ) -> dict:
        if settings.require_api_key:
            expected = key_path.read_text(encoding="utf-8").strip() if key_path.is_file() else ""
            if not expected or not x_api_key or not secrets.compare_digest(x_api_key, expected):
                audit("authentication_failed", request, "ontbrekende of ongeldige API-key")
                raise HTTPException(status_code=401, detail="Geldige X-API-Key vereist.")
        return {"id": 101, "username": "student-analist", "team": "delta"}

    CurrentUser = Annotated[dict, Depends(current_user)]

    def parse_query(page: str, limit: str, project_status: str | None, sort: str) -> tuple[int, int]:
        try:
            parsed_page = int(page)
            parsed_limit = int(limit)
        except ValueError as exc:
            if settings.validate_queries:
                raise HTTPException(status_code=422, detail="page en limit moeten gehele getallen zijn.") from exc
            raise ValueError(f"invalid literal in pagination: page={page!r}, limit={limit!r}") from exc

        if settings.validate_queries:
            if parsed_page < 1 or not 1 <= parsed_limit <= 20:
                raise HTTPException(status_code=422, detail="page >= 1 en 1 <= limit <= 20 vereist.")
            if project_status is not None and project_status not in VALID_STATUSES:
                raise HTTPException(status_code=422, detail="Onbekende statusparameter.")
            if sort not in VALID_SORTS:
                raise HTTPException(status_code=422, detail="Onbekende sorteerparameter.")
        elif sort not in VALID_SORTS:
            raise RuntimeError(f"sqlite3.OperationalError: no such column: {sort}; ORDER BY {sort}")
        return parsed_page, parsed_limit

    @api.get("/", include_in_schema=False)
    def root() -> dict:
        return {
            "name": "WindesAPI lokaal onderwijs-lab",
            "scope": "Alleen fictieve data; uitsluitend lokaal gebruiken.",
            "documentation": "/docs",
        }

    @api.get("/health")
    def health() -> dict:
        try:
            with get_connection(database_path) as connection:
                connection.execute("SELECT 1 FROM projects LIMIT 1").fetchone()
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Database niet gereed.") from exc
        return {"status": "ok", "service": "windesapi-api-lab"}

    @api.get("/api/v1/projects")
    def list_projects(
        response: Response,
        current_user: CurrentUser,
        page: str = Query("1"),
        limit: str = Query("5"),
        project_status: str | None = Query(None, alias="status"),
        sort: str = Query("id"),
    ) -> dict:
        parsed_page, parsed_limit = parse_query(page, limit, project_status, sort)
        clauses = []
        values: list[object] = []
        if project_status:
            clauses.append("status = ?")
            values.append(project_status)
        if settings.enforce_project_ownership:
            clauses.append("owner_id = ?")
            values.append(current_user["id"])
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        offset = (parsed_page - 1) * parsed_limit
        with get_connection(database_path) as connection:
            total = connection.execute(f"SELECT COUNT(*) FROM projects{where}", values).fetchone()[0]
            rows = connection.execute(
                f"SELECT * FROM projects{where} ORDER BY {sort} LIMIT ? OFFSET ?",
                [*values, parsed_limit, offset],
            ).fetchall()
        items = [row_to_dict(row) for row in rows]
        if settings.minimal_responses:
            items = [{key: value for key, value in item.items() if key in PUBLIC_PROJECT_FIELDS} for item in items]
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Page"] = str(parsed_page)
        next_page = parsed_page + 1 if offset + len(items) < total else None
        return {"items": items, "page": parsed_page, "limit": parsed_limit, "total": total, "next_page": next_page}

    @api.get("/api/v1/projects/{project_id}")
    def get_project(project_id: int, request: Request, current_user: CurrentUser) -> dict:
        with get_connection(database_path) as connection:
            row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Project niet gevonden.")
        project = row_to_dict(row)
        if settings.enforce_project_ownership and project["owner_id"] != current_user["id"]:
            audit("authorization_denied", request, f"project_id={project_id}")
            raise HTTPException(status_code=403, detail="Geen toegang tot dit project.")
        if settings.minimal_responses:
            project = {key: value for key, value in project.items() if key in PUBLIC_PROJECT_FIELDS}
        return project

    @api.post("/api/v1/reports", status_code=201)
    def create_report(payload: ReportInput, request: Request, current_user: CurrentUser) -> dict:
        with get_connection(database_path) as connection:
            project = connection.execute("SELECT owner_id FROM projects WHERE id = ?", (payload.project_id,)).fetchone()
            if project is None:
                raise HTTPException(status_code=404, detail="Project niet gevonden.")
            if settings.enforce_project_ownership and project["owner_id"] != current_user["id"]:
                audit("authorization_denied", request, f"report project_id={payload.project_id}")
                raise HTTPException(status_code=403, detail="Geen toegang tot dit project.")
            cursor = connection.execute(
                "INSERT INTO reports (project_id, analyst_id, observation) VALUES (?, ?, ?)",
                (payload.project_id, current_user["id"], payload.observation),
            )
        return {"id": cursor.lastrowid, "project_id": payload.project_id, "status": "created"}

    return api


app = create_app()
