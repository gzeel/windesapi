from typing import Any

from fastapi import APIRouter, Body, HTTPException, status

from app.auth import CurrentUser
from app.database import get_connection, row_to_dict


router = APIRouter(prefix="/api/v2", tags=["users"])


def expose_user(row) -> dict:
    data = row_to_dict(row)
    data["is_admin"] = bool(data["is_admin"])
    data["beta_features"] = bool(data["beta_features"])
    data["can_export"] = bool(data["can_export"])
    return data


@router.get("/me")
def me(current_user: CurrentUser) -> dict:
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "team": current_user["team"],
        "clearance_level": current_user["clearance_level"],
        "is_admin": bool(current_user["is_admin"]),
        "can_export": bool(current_user["can_export"]),
    }


@router.get("/users")
def list_users(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM users ORDER BY id").fetchall()
    return {"users": [expose_user(row) for row in rows]}


@router.get("/users/{user_id}")
def get_user(user_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return expose_user(row)


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    current_user: CurrentUser,
    payload: dict[str, Any] = Body(...),
) -> dict:
    if current_user["id"] != user_id and not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only edit own profile")

    writable_columns = {
        "full_name",
        "email",
        "password",
        "role",
        "is_admin",
        "student_number",
        "team",
        "clearance_level",
        "can_export",
        "api_quota",
        "recovery_code",
        "internal_notes",
        "tuition_balance",
        "beta_features",
    }
    updates = {key: value for key, value in payload.items() if key in writable_columns}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No writable fields supplied")

    set_clause = ", ".join(f"{column} = ?" for column in updates)
    values = [int(value) if isinstance(value, bool) else value for value in updates.values()]
    values.append(user_id)

    with get_connection() as connection:
        connection.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return expose_user(row)


@router.get("/users/{user_id}/grades")
def get_grades(user_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        user = connection.execute("SELECT id, username, full_name FROM users WHERE id = ?", (user_id,)).fetchone()
        rows = connection.execute(
            """
            SELECT courses.code, courses.title, enrollments.grade,
                   enrollments.private_feedback, enrollments.remediation_plan
            FROM enrollments
            JOIN courses ON courses.id = enrollments.course_id
            WHERE enrollments.user_id = ?
            ORDER BY courses.code
            """,
            (user_id,),
        ).fetchall()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"student": row_to_dict(user), "grades": [row_to_dict(row) for row in rows]}
