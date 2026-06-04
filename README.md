# WindesAPI

WindesAPI is een lokaal draaiende, bewust kwetsbare OSINT-demo-API voor cybersecurityonderwijs. Studenten oefenen met API-verkenning, tokengebruik, endpoint discovery en het herkennen van datalekken in een fictieve OSINT-caseomgeving.

Alle personen, organisaties, domeinen, social handles en gegevens in deze demo zijn fictief. Gebruik deze applicatie alleen lokaal of in een afgesloten labomgeving.

## Docker Desktop Snelstart

Aanbevolen voor studenten:

```bash
docker run --rm --name WindesAPI -p 8000:8000 gzeel/windesapi:latest
```

Open daarna `http://127.0.0.1:8000`.

De container seedt de demo-database automatisch bij het starten. Stoppen en opnieuw starten zet de opdracht terug naar de beginsituatie.

## Image Bouwen Voor Docenten

```bash
docker build -t windesapi:latest .
docker run --rm --name WindesAPI -p 8000:8000 windesapi:latest
```

Met Docker Compose:

```bash
docker compose up --build
```

Exporteren voor verspreiding zonder registry:

```bash
docker save windesapi:latest -o windesapi.tar
```

Studenten importeren dat bestand met:

```bash
docker load -i windesapi.tar
docker run --rm --name WindesAPI -p 8000:8000 windesapi:latest
```

## Lokale Python Installatie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_db.py
uvicorn app.main:app --reload
```

## Demo-accounts

| Gebruiker | Wachtwoord | Rol |
| --- | --- | --- |
| `sanne` | `welkom123` | junior-analyst |
| `milan` | `voetbal2024` | junior-analyst |
| `noor` | `qwerty!` | analyst |
| `admin` | `admin123` | lead-analyst |

## Snelstart

Login als analyst:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v2/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"sanne","password":"welkom123"}'
```

Gebruik de `access_token` als bearer-token:

```bash
curl -s http://127.0.0.1:8000/api/v2/osint/dashboard \
  -H 'Authorization: Bearer <TOKEN>'
```

## Gedeeltelijke API-documentatie Voor Studenten

Deze documentatie is expres onvolledig. Onderzoek responses, ID's, URL-patronen, oude API-versies en afwijkende velden.

### Authenticatie

`POST /api/v2/auth/login`

Body:

```json
{
  "username": "sanne",
  "password": "welkom123"
}
```

### Dashboard

`GET /api/v2/osint/dashboard`

Geeft een korte samenvatting voor de ingelogde analyst.

### Analysts

`GET /api/v2/osint/analysts`

Geeft een lijst met analysts terug.

`PUT /api/v2/osint/analysts/{id}`

Wijzigt profielvelden van de ingelogde analyst.

Voorbeeld:

```json
{
  "full_name": "Sanne de Vries",
  "email": "sanne.devries@windesapi.local"
}
```

### OSINT Cases

`GET /api/v2/osint/cases`

Geeft een lijst met cases terug.

`GET /api/v2/osint/cases/{id}`

Geeft details van een case terug.

### Subjects

`GET /api/v2/osint/subjects`

Geeft een lijst met OSINT-subjects terug.

`GET /api/v2/osint/subjects/{id}`

Geeft details van een subject terug.

`GET /api/v2/osint/subjects/{id}/profiles`

Geeft bekende social profiles van een subject terug.

### Sources

`GET /api/v2/osint/sources`

Geeft geconfigureerde OSINT-bronnen terug.

### Admin

`GET /api/v2/admin/overview`

Alleen bedoeld voor lead analysts.

## Oefendoelen

1. Automatiseer login en hergebruik het bearer-token.
2. Breng de OSINT-endpoints in kaart.
3. Vergelijk cases en subjects door ID's aan te passen.
4. Herken excessive data exposure in responses.
5. Test of extra JSON-velden bij analyst-updates effect hebben.
6. Zoek naar oude of ongedocumenteerde OSINT-exportendpoints.
7. Bespreek welke data in echte OSINT-trajecten binnen scope, proportioneel en ethisch verantwoord is.

## Projectstructuur

```text
app/
  main.py
  database.py
  auth.py
  routers/
scripts/
  seed_db.py
docs/
  ARCHITECT_REDTEAM_NOTES.md
  DOCENTEN_HANDLEIDING.md
docker/
  entrypoint.sh
Dockerfile
docker-compose.yml
```
