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
        "sanne.devries@windesapi.local",
        "junior-analyst",
        0,
        "ANL-101",
        "open-source-cell",
        "public",
        0,
        100,
        "RC-SANNE-8842",
        "Nieuw OSINT-account. Niet tonen in frontend.",
        0,
        0,
    ),
    (
        102,
        "milan",
        "voetbal2024",
        "Milan Jansen",
        "milan.jansen@windesapi.local",
        "junior-analyst",
        0,
        "ANL-102",
        "brand-monitoring",
        "restricted",
        0,
        100,
        "RC-MILAN-1937",
        "FLAG{idor_analyst_profile_found}",
        0,
        1,
    ),
    (
        103,
        "noor",
        "qwerty!",
        "Noor Bakker",
        "noor.bakker@windesapi.local",
        "analyst",
        0,
        "ANL-103",
        "threat-intel",
        "restricted",
        0,
        75,
        "RC-NOOR-5510",
        "Heeft toegang tot gesloten case-notities via team threat-intel.",
        0,
        0,
    ),
    (
        901,
        "admin",
        "admin123",
        "Asha Vermeer",
        "asha.vermeer@windesapi.local",
        "lead-analyst",
        1,
        "LEAD-901",
        "osint-ops",
        "admin",
        1,
        1000,
        "RC-ADMIN-0001",
        "Beheerdersaccount. FLAG{excessive_analyst_dump}",
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
    ("admin_panel_note", "Mass assignment kan is_admin en can_export wijzigen.", 1),
    ("osint_scope_warning", "Alle personen, organisaties en domeinen zijn fictief voor lokaal onderwijs.", 0),
]


OSINT_CASES = [
    (
        201,
        "Publieke footprint fictieve webshop Northwind Gadgets",
        101,
        "open",
        "medium",
        "@northwind-gadgets",
        "Inventariseer publieke accounts, domeinen en gelekte testcredentials van een fictieve webshop.",
        "Let op: testcredential hergebruik gevonden in Pastebin-mirror. Escaleer niet buiten labscope.",
        "n.v.t.",
        "",
    ),
    (
        202,
        "Executive exposure fictieve stichting Zorgbrug",
        102,
        "restricted",
        "high",
        "@zorgbrug-directie",
        "Onderzoek publieke sporen rondom een fictieve bestuurder en gelinkte social accounts.",
        "FLAG{osint_case_bola_restricted_notes}. Beschermde persoon heeft herleidbare privegegevens in oude forumcache.",
        "Mara Vos, fictief bestuurslid",
        "FLAG{osint_case_202_accessed}",
    ),
    (
        203,
        "Typosquatting rond fictief merk Windesmart",
        103,
        "open",
        "low",
        "windesmart-login.example",
        "Vergelijk publieke domeinregistraties, social handles en oude supporttickets.",
        "Intern: domein windesmart-login.example is bewust in de labomgeving geplaatst.",
        "n.v.t.",
        "",
    ),
]


OSINT_SUBJECTS = [
    (
        301,
        "Northwind Gadgets BV",
        "northwind-gadgets",
        "organization",
        "Northwind Gadgets BV",
        "Utrecht, NL",
        0.91,
        "https://example.test/northwind-gadgets",
        "info@northwind-gadgets.example",
        "+31-20-000-0101",
        "summer2024-demo",
        "Fictieve Handelsweg 10, 0000 AA Utrecht",
        '{"source":"cached_company_profile","tags":["webshop","training"],"found_by":"crawler-7"}',
        "FLAG{excessive_osint_subject_dump}",
    ),
    (
        302,
        "Mara Vos",
        "mara-vos-board",
        "person",
        "Stichting Zorgbrug",
        "Zwolle, NL",
        0.84,
        "https://example.test/profiles/mara-vos",
        "mara.vos@zorgbrug.example",
        "+31-38-000-0202",
        "zorgbrug-demo-2023",
        "Fictieve Singel 22, 0000 BB Zwolle",
        '{"source":"archived_forum_cache","breach_id":"LAB-BR-302","risk":"training-only"}',
        "Gevoelige privevelden horen nooit in een lijstresponse.",
    ),
    (
        303,
        "Windesmart Support",
        "windesmart-helpdesk",
        "service-account",
        "Windesmart",
        "Leeuwarden, NL",
        0.72,
        "https://example.test/windesmart/support",
        "support@windesmart.example",
        "+31-58-000-0303",
        "support-reset-demo",
        "Fictieve Campuslaan 3, 0000 CC Leeuwarden",
        '{"source":"old_ticket_export","note":"shadow endpoint confirms this"}',
        "Koppelbaar aan dev dump via /api/v1/osint/export.",
    ),
]


OSINT_SOCIAL_PROFILES = [
    (301, "X", "@northwind_gadgets", "https://social.example/@northwind_gadgets", "search:dork", 1280, 0, "2026-05-20", "Marketingaccount, geen restricted data."),
    (301, "GitHub", "northwind-labs", "https://code.example/northwind-labs", "public repo search", 42, 0, "2026-05-18", "Repo bevat oude config-string: FLAG{profile_metadata_leak}"),
    (302, "LinkedIn", "mara-vos-zorgbrug", "https://professional.example/in/mara-vos-zorgbrug", "name pivot", 610, 1, "2026-05-15", "Privemail gecorreleerd uit oude cache."),
    (302, "Instagram", "@mara.reist.fictief", "https://social.example/@mara.reist.fictief", "image reverse-search", 87, 0, "2026-04-28", "Alleen fictieve labdata, niet buiten scope gebruiken."),
    (303, "Mastodon", "@windesmart_help", "https://fediverse.example/@windesmart_help", "brand query", 212, 0, "2026-05-11", "Supportaccount hergebruikt wachtwoord in subject-dump."),
]


OSINT_SOURCES = [
    (1, "WindesAPI Cache Mirror", "archive", "https://archive.example.test", "Zoek op alias en organisatie.", "FLAG{shadow_osint_source_api_key}", "osint-ops", "Robots-policy genegeerd in legacy crawler; alleen labdata."),
    (2, "Fictional Breach Index", "breach-corpus", "https://breach.example.test", "Query op e-maildomein.", "BR-IDX-DEMO-KEY", "threat-intel", "Bevat uitsluitend fictieve seed-data."),
    (3, "Social Handle Resolver", "resolver", "https://resolver.example.test", "Pivot vanaf handle naar profiel-URL.", "RESOLVE-DEMO-KEY", "brand-monitoring", "Rate limit in frontend, niet in API."),
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
             team, clearance_level, can_export, api_quota, recovery_code, internal_notes,
             tuition_balance, beta_features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        connection.executemany(
            """
            INSERT INTO osint_cases
            (id, title, owner_user_id, status, priority, target_handle, public_summary,
             restricted_notes, protected_person, internal_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            OSINT_CASES,
        )
        connection.executemany(
            """
            INSERT INTO osint_subjects
            (id, display_name, alias, category, organization, location_hint, confidence_score,
             public_profile_url, email, phone, leaked_password, private_address, raw_source_json,
             internal_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            OSINT_SUBJECTS,
        )
        connection.executemany(
            """
            INSERT INTO osint_social_profiles
            (subject_id, platform, handle, profile_url, discovered_from, followers, verified,
             last_seen, private_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            OSINT_SOCIAL_PROFILES,
        )
        connection.executemany(
            """
            INSERT INTO osint_sources
            (id, name, source_type, base_url, collection_hint, api_key, internal_owner, robots_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            OSINT_SOURCES,
        )


if __name__ == "__main__":
    reset_database()
    print(f"Seeded demo database at {DB_PATH}")
