from fastapi import APIRouter

from app.database import get_connection, row_to_dict


router = APIRouter(tags=["legacy"])


def fetch_all(connection, table: str) -> list[dict]:
    rows = connection.execute(f"SELECT * FROM {table}").fetchall()
    return [row_to_dict(row) for row in rows]


@router.get("/api/v1/admin/export")
def legacy_admin_export() -> dict:
    with get_connection() as connection:
        return {
            "warning": "Legacy export endpoint. Do not expose publicly.",
            "users": fetch_all(connection, "users"),
            "sessions": fetch_all(connection, "sessions"),
            "courses": fetch_all(connection, "courses"),
            "enrollments": fetch_all(connection, "enrollments"),
            "tickets": fetch_all(connection, "tickets"),
            "system_config": fetch_all(connection, "system_config"),
            "osint_cases": fetch_all(connection, "osint_cases"),
            "osint_subjects": fetch_all(connection, "osint_subjects"),
            "osint_social_profiles": fetch_all(connection, "osint_social_profiles"),
            "osint_sources": fetch_all(connection, "osint_sources"),
        }


@router.get("/api/dev/users")
def dev_users_dump() -> dict:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, username, password, email, role, is_admin, recovery_code, internal_notes
            FROM users
            ORDER BY id
            """
        ).fetchall()
    return {"environment": "local-dev", "users": [row_to_dict(row) for row in rows]}


@router.get("/api/v1/osint/export")
def legacy_osint_export() -> dict:
    with get_connection() as connection:
        return {
            "warning": "Legacy OSINT crawler export. Authentication was never implemented.",
            "scope": "Fictieve labdata voor studenten.",
            "cases": fetch_all(connection, "osint_cases"),
            "subjects": fetch_all(connection, "osint_subjects"),
            "profiles": fetch_all(connection, "osint_social_profiles"),
            "sources": fetch_all(connection, "osint_sources"),
            "flag": "FLAG{legacy_osint_shadow_api_found}",
        }
