from typing import Any

from fastapi import APIRouter, Body, HTTPException, status

from app.auth import CurrentUser
from app.database import get_connection, row_to_dict
from app.routers.users import expose_user


router = APIRouter(prefix="/api/v2/osint", tags=["osint"])


def bool_fields(data: dict, *fields: str) -> dict:
    for field in fields:
        data[field] = bool(data[field])
    return data


@router.get("/dashboard")
def dashboard(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        own_cases = connection.execute(
            "SELECT COUNT(*) AS count FROM osint_cases WHERE owner_user_id = ?",
            (current_user["id"],),
        ).fetchone()
        subject_count = connection.execute("SELECT COUNT(*) AS count FROM osint_subjects").fetchone()
        source_count = connection.execute("SELECT COUNT(*) AS count FROM osint_sources").fetchone()

    return {
        "analyst": {
            "id": current_user["id"],
            "username": current_user["username"],
            "team": current_user["team"],
            "clearance_level": current_user["clearance_level"],
        },
        "own_case_count": own_cases["count"],
        "known_subject_count": subject_count["count"],
        "configured_source_count": source_count["count"],
        "scope": "Alle data is fictief en bedoeld voor lokale OSINT-training.",
    }


@router.get("/analysts")
def list_analysts(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM users ORDER BY id").fetchall()
    return {"analysts": [expose_user(row) for row in rows]}


@router.put("/analysts/{analyst_id}")
def update_analyst(
    analyst_id: int,
    current_user: CurrentUser,
    payload: dict[str, Any] = Body(...),
) -> dict:
    if current_user["id"] != analyst_id and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only edit own analyst profile")

    writable_columns = {
        "full_name",
        "email",
        "password",
        "role",
        "is_admin",
        "team",
        "clearance_level",
        "can_export",
        "api_quota",
        "recovery_code",
        "internal_notes",
        "beta_features",
    }
    updates = {key: value for key, value in payload.items() if key in writable_columns}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No writable fields supplied")

    set_clause = ", ".join(f"{column} = ?" for column in updates)
    values = [int(value) if isinstance(value, bool) else value for value in updates.values()]
    values.append(analyst_id)

    with get_connection() as connection:
        connection.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        row = connection.execute("SELECT * FROM users WHERE id = ?", (analyst_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analyst not found")
    return expose_user(row)


@router.get("/cases")
def list_cases(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, owner_user_id, status, priority, target_handle, public_summary, created_at
            FROM osint_cases
            ORDER BY priority DESC, id
            """
        ).fetchall()
    return {"cases": [row_to_dict(row) for row in rows]}


@router.get("/cases/{case_id}")
def get_case(case_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        case = connection.execute("SELECT * FROM osint_cases WHERE id = ?", (case_id,)).fetchone()
        owner = None
        if case is not None:
            owner = connection.execute(
                "SELECT id, username, full_name, team, clearance_level FROM users WHERE id = ?",
                (case["owner_user_id"],),
            ).fetchone()

    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSINT case not found")
    return {"case": row_to_dict(case), "owner": row_to_dict(owner)}


@router.get("/subjects")
def list_subjects(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM osint_subjects ORDER BY id").fetchall()
    return {"subjects": [row_to_dict(row) for row in rows]}


@router.get("/subjects/{subject_id}")
def get_subject(subject_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        subject = connection.execute("SELECT * FROM osint_subjects WHERE id = ?", (subject_id,)).fetchone()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return row_to_dict(subject)


@router.get("/subjects/{subject_id}/profiles")
def get_subject_profiles(subject_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        subject = connection.execute(
            "SELECT id, display_name, alias, category FROM osint_subjects WHERE id = ?",
            (subject_id,),
        ).fetchone()
        rows = connection.execute(
            "SELECT * FROM osint_social_profiles WHERE subject_id = ? ORDER BY platform",
            (subject_id,),
        ).fetchall()

    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    profiles = [bool_fields(row_to_dict(row), "verified") for row in rows]
    return {"subject": row_to_dict(subject), "profiles": profiles}


@router.get("/sources")
def list_sources(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM osint_sources ORDER BY id").fetchall()
    return {"sources": [row_to_dict(row) for row in rows]}
