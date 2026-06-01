from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth import create_session
from app.database import get_connection


router = APIRouter(prefix="/api/v2/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(credentials: LoginRequest) -> dict:
    with get_connection() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (credentials.username, credentials.password),
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_session(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "is_admin": bool(user["is_admin"]),
        },
    }
