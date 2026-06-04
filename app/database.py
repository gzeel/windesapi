import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(
    os.environ.get("WINDES_DB_PATH")
    or os.environ.get("CAMPUS_DB_PATH", BASE_DIR / "data" / "windesapi.db")
)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    is_admin INTEGER NOT NULL DEFAULT 0,
    student_number TEXT NOT NULL,
    team TEXT NOT NULL DEFAULT 'training',
    clearance_level TEXT NOT NULL DEFAULT 'public',
    can_export INTEGER NOT NULL DEFAULT 0,
    api_quota INTEGER NOT NULL DEFAULT 100,
    recovery_code TEXT NOT NULL,
    internal_notes TEXT NOT NULL DEFAULT '',
    tuition_balance REAL NOT NULL DEFAULT 0,
    beta_features INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    coordinator TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    internal_budget_code TEXT NOT NULL,
    exam_answer_key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    grade REAL,
    private_feedback TEXT NOT NULL,
    remediation_plan TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL,
    internal_notes TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    is_secret INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS osint_cases (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    owner_user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    target_handle TEXT NOT NULL,
    public_summary TEXT NOT NULL,
    restricted_notes TEXT NOT NULL,
    protected_person TEXT NOT NULL,
    internal_flag TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS osint_subjects (
    id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL,
    alias TEXT NOT NULL,
    category TEXT NOT NULL,
    organization TEXT NOT NULL,
    location_hint TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    public_profile_url TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    leaked_password TEXT NOT NULL,
    private_address TEXT NOT NULL,
    raw_source_json TEXT NOT NULL,
    internal_notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS osint_social_profiles (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    handle TEXT NOT NULL,
    profile_url TEXT NOT NULL,
    discovered_from TEXT NOT NULL,
    followers INTEGER NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    last_seen TEXT NOT NULL,
    private_metadata TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES osint_subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS osint_sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    base_url TEXT NOT NULL,
    collection_hint TEXT NOT NULL,
    api_key TEXT NOT NULL,
    internal_owner TEXT NOT NULL,
    robots_note TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(SCHEMA_SQL)


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)
