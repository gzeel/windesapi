from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database import DB_PATH, SCHEMA_SQL, get_connection  # noqa: E402


USERS = [
    (
        101,
        "sanne",
        "welkom123",
        "Sanne de Vries",
        "sanne.devries@student.windesapi.local",
        "student",
        0,
        "S2024101",
        100,
        "RC-SANNE-8842",
        "Heeft vrijstelling voor Lab 2. Niet tonen in frontend.",
        245.50,
        0,
    ),
    (
        102,
        "milan",
        "voetbal2024",
        "Milan Jansen",
        "milan.jansen@student.windesapi.local",
        "student",
        0,
        "S2024102",
        100,
        "RC-MILAN-1937",
        "FLAG{idor_milan_profile_found}",
        0,
        1,
    ),
    (
        103,
        "noor",
        "qwerty!",
        "Noor Bakker",
        "noor.bakker@student.windesapi.local",
        "student",
        0,
        "S2024103",
        75,
        "RC-NOOR-5510",
        "Financiele blokkade actief. Alleen zichtbaar voor administratie.",
        1299.99,
        0,
    ),
    (
        901,
        "admin",
        "admin123",
        "Asha Vermeer",
        "asha.vermeer@windesapi.local",
        "administrator",
        1,
        "STAFF-901",
        1000,
        "RC-ADMIN-0001",
        "Beheerdersaccount. FLAG{excessive_user_dump}",
        0,
        1,
    ),
]


COURSES = [
    (1, "CS101", "API Fundamentals", "dr. Van Leeuwen", 30, "BUDGET-CS-2024-ALPHA", "FLAG{course_answer_key_leak}"),
    (2, "SEC220", "Web Security Testing", "ir. Demir", 24, "BUDGET-SEC-REDTEAM", "A,C,D,B,C"),
    (3, "OPS310", "Blue Team Operations", "drs. Kramer", 20, "BUDGET-OPS-SIEM", "B,B,A,D,A"),
]


ENROLLMENTS = [
    (101, 1, 8.1, "Sterke automatisering met Python.", "Geen actie nodig."),
    (101, 2, 7.4, "Let op scope-afbakening bij testen.", "Extra Burp Suite-lab aanbevolen."),
    (102, 1, 6.2, "Heeft hints gebruikt voor endpoint discovery.", "Herhaal oefening zonder OpenAPI-docs."),
    (102, 2, 9.1, "FLAG{grades_bola_private_feedback}", "Mag extra challenge proberen."),
    (103, 1, 5.4, "Mist basiskennis HTTP-statuscodes.", "Verplicht remediatiegesprek."),
]


TICKETS = [
    (101, "Kan niet inloggen in labomgeving", "Mijn token lijkt steeds ongeldig te worden.", "closed", "Wachtwoord per mail gedeeld door servicedesk."),
    (102, "Cijfer niet zichtbaar", "Ik zie SEC220 niet op mijn dashboard.", "open", "Controleer enrollments handmatig."),
    (103, "Betalingsmelding", "Ik krijg een blokkade bij inschrijving.", "pending", "Openstaand saldo zichtbaar in intern profiel."),
]


AUDIT_EVENTS = [
    (101, "login", "127.0.0.1", "Student login via Postman"),
    (901, "admin_export", "10.0.0.5", "Legacy export gebruikt tijdens migratie"),
    (None, "dev_endpoint_enabled", "127.0.0.1", "FLAG{legacy_shadow_api_found}"),
]


SYSTEM_CONFIG = [
    ("environment", "local-training", 0),
    ("support_email", "servicedesk@windesapi.local", 0),
    ("legacy_export_key", "FLAG{legacy_export_leaks_config}", 1),
    ("jwt_signing_secret", "demo-not-a-real-secret", 1),
    ("admin_panel_note", "Mass assignment kan is_admin wijzigen.", 1),
]


def reset_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)
        connection.executemany(
            """
            INSERT INTO users
            (id, username, password, full_name, email, role, is_admin, student_number,
             api_quota, recovery_code, internal_notes, tuition_balance, beta_features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            USERS,
        )
        connection.executemany(
            "INSERT INTO courses (id, code, title, coordinator, capacity, internal_budget_code, exam_answer_key) VALUES (?, ?, ?, ?, ?, ?, ?)",
            COURSES,
        )
        connection.executemany(
            "INSERT INTO enrollments (user_id, course_id, grade, private_feedback, remediation_plan) VALUES (?, ?, ?, ?, ?)",
            ENROLLMENTS,
        )
        connection.executemany(
            "INSERT INTO tickets (user_id, subject, message, status, internal_notes) VALUES (?, ?, ?, ?, ?)",
            TICKETS,
        )
        connection.executemany(
            "INSERT INTO audit_events (user_id, action, ip_address, details) VALUES (?, ?, ?, ?)",
            AUDIT_EVENTS,
        )
        connection.executemany(
            "INSERT INTO system_config (key, value, is_secret) VALUES (?, ?, ?)",
            SYSTEM_CONFIG,
        )


if __name__ == "__main__":
    reset_database()
    print(f"Seeded demo database at {DB_PATH}")
