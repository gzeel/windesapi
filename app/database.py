import sqlite3
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    category TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    owner_team TEXT NOT NULL,
    summary TEXT NOT NULL,
    budget_eur INTEGER NOT NULL,
    internal_location TEXT NOT NULL,
    supplier_access_code TEXT NOT NULL,
    internal_notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    analyst_id INTEGER NOT NULL,
    observation TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
"""

PROJECTS = [
    (1, "Zonnepanelen op gebouw Delta", "active", "energy", 101, "delta", "Meet de lokale energieopbrengst.", 42000, "Techniekruimte D-1.14", "DEMO-SUPPLIER-DELTA", "Alleen team Delta mag de omvormerconfiguratie zien."),
    (2, "Toegangsmeting gebouw Echo", "active", "security", 102, "echo", "Analyseer geanonimiseerde tellingen per uur.", 18000, "Patchkast E-0.03", "DEMO-SUPPLIER-ECHO", "Bevat interne informatie van team Echo."),
    (3, "Waterverbruik sporthal", "paused", "sustainability", 101, "delta", "Vergelijk nacht- en dagverbruik.", 12500, "Meterkast S-0.08", "DEMO-SUPPLIER-SPORT", "Sensor wordt in september vervangen."),
    (4, "Bezetting fietsenstalling", "active", "mobility", 102, "echo", "Publiceer alleen totalen per kwartier.", 9700, "Beheerhok F-0.01", "DEMO-SUPPLIER-BIKE", "Ruwe sensordata niet exporteren."),
    (5, "Binnenklimaat lokaal A2.16", "completed", "climate", 101, "delta", "Onderzoek CO2-trends tijdens lessen.", 6400, "Plafondzone A2.16", "DEMO-SUPPLIER-AIR", "Kalibratie afgerond met testaccount."),
    (6, "Laadpalen bezoekers", "active", "mobility", 102, "echo", "Meet beschikbaarheid zonder kentekens.", 31000, "Parkeerzone P2", "DEMO-SUPPLIER-CHARGE", "Contractinformatie is niet publiek."),
    (7, "Afvalstromen restaurant", "active", "sustainability", 101, "delta", "Rapporteer wekelijkse gewichten.", 8300, "Logistieke gang R-0.04", "DEMO-SUPPLIER-WASTE", "Geen namen van medewerkers registreren."),
    (8, "Netwerkverbruik makerspace", "paused", "technology", 102, "echo", "Maak een capaciteitsprognose.", 15600, "Patchkast M-1.02", "DEMO-SUPPLIER-NET", "Topologie valt buiten de publieke response."),
    (9, "Warmtepomp gebouw Delta", "active", "energy", 101, "delta", "Vergelijk verbruik met buitentemperatuur.", 53500, "Techniekruimte D-0.02", "DEMO-SUPPLIER-HEAT", "Onderhoudsvenster iedere eerste maandag."),
    (10, "Geluidmeting studieplein", "completed", "climate", 102, "echo", "Toon gemiddelden zonder audio op te slaan.", 4800, "Studieplein E1", "DEMO-SUPPLIER-SOUND", "Audio-opname is expliciet uitgeschakeld."),
    (11, "Regenwater tuin", "active", "sustainability", 101, "delta", "Bepaal de bespaarde hoeveelheid leidingwater.", 11200, "Pompkast T-0.01", "DEMO-SUPPLIER-RAIN", "Pompcode mag niet naar clients."),
    (12, "Lichtsturing bibliotheek", "active", "energy", 102, "echo", "Optimaliseer schakeltijden op bezetting.", 22800, "Regelkast B-2.07", "DEMO-SUPPLIER-LIGHT", "Configuratie wordt door team Echo beheerd."),
]


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def reset_database(db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.executemany(
            """
            INSERT INTO projects
            (id, title, status, category, owner_id, owner_team, summary, budget_eur,
             internal_location, supplier_access_code, internal_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            PROJECTS,
        )


def ensure_database(db_path: Path) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        count = connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    if count == 0:
        reset_database(db_path)


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)
