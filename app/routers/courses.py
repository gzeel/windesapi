from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser
from app.database import get_connection, row_to_dict


router = APIRouter(prefix="/api/v2/courses", tags=["courses"])


@router.get("")
def list_courses(current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM courses ORDER BY code").fetchall()
    return {"courses": [row_to_dict(row) for row in rows]}


@router.get("/{course_id}")
def get_course(course_id: int, current_user: CurrentUser) -> dict:
    with get_connection() as connection:
        course = connection.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return row_to_dict(course)
