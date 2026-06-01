from fastapi import APIRouter

from app.auth import AdminUser
from app.database import get_connection, row_to_dict


router = APIRouter(prefix="/api/v2/admin", tags=["admin"])


@router.get("/overview")
def admin_overview(admin_user: AdminUser) -> dict:
    with get_connection() as connection:
        config = connection.execute("SELECT * FROM system_config ORDER BY key").fetchall()
        events = connection.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT 10").fetchall()
        ticket_count = connection.execute("SELECT COUNT(*) AS count FROM tickets").fetchone()
    return {
        "message": "Welcome to the admin overview",
        "admin": {"id": admin_user["id"], "username": admin_user["username"]},
        "ticket_count": ticket_count["count"],
        "config": [row_to_dict(row) for row in config],
        "recent_audit_events": [row_to_dict(row) for row in events],
    }
