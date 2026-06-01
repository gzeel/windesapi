# WindesAPI

WindesAPI is een lokaal draaiende, bewust kwetsbare demo-API voor cybersecurityonderwijs. De API is bedoeld voor oefeningen met scripts, Postman, curl of Burp Suite.

Gebruik deze applicatie alleen lokaal of in een afgesloten labomgeving. De kwetsbaarheden zijn expres ingebouwd.

## Docker Desktop Snelstart

Aanbevolen voor studenten: draai de API als Docker-container.

```bash
docker run --rm --name WindesAPI -p 8000:8000 windesapi:latest
```

De API is daarna bereikbaar op `http://127.0.0.1:8000`.

De container seedt de demo-database automatisch bij het starten. Stoppen en opnieuw starten zet de opdracht dus terug naar de beginsituatie.

## Image Bouwen Voor Docenten

Build lokaal een image:

```bash
docker build -t windesapi:latest .
```

Start het gebouwde image:

```bash
docker run --rm --name WindesAPI -p 8000:8000 windesapi:latest
```

Of gebruik Docker Compose:

```bash
docker compose up --build
```

Maak een exportbestand om buiten een registry te verspreiden:

```bash
docker save windesapi:latest -o windesapi.tar
```

Studenten kunnen dat bestand importeren met:

```bash
docker load -i windesapi.tar
docker run --rm --name WindesAPI -p 8000:8000 windesapi:latest
```

Als je een registry gebruikt, push dan bijvoorbeeld:

```bash
docker tag windesapi:latest <registry>/<naam>/windesapi:latest
docker push <registry>/<naam>/windesapi:latest
```

Studenten starten dan met:

```bash
docker run --rm --name WindesAPI -p 8000:8000 <registry>/<naam>/windesapi:latest
```

## Lokale Python Installatie

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_db.py
uvicorn app.main:app --reload
```

De API draait daarna standaard op `http://127.0.0.1:8000`.

## Demo-accounts

| Gebruiker | Wachtwoord | Rol |
| --- | --- | --- |
| `sanne` | `welkom123` | student |
| `milan` | `voetbal2024` | student |
| `noor` | `qwerty!` | student |
| `admin` | `admin123` | administrator |

## Snelstart

Login als student:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v2/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"sanne","password":"welkom123"}'
```

Gebruik de `access_token` als bearer-token:

```bash
curl -s http://127.0.0.1:8000/api/v2/me \
  -H 'Authorization: Bearer <TOKEN>'
```

## Gedeeltelijke API-documentatie voor studenten

Deze documentatie is expres onvolledig. Studenten worden aangemoedigd om responses, statuscodes, URL-patronen en versiepaden te onderzoeken.

### Authenticatie

`POST /api/v2/auth/login`

Body:

```json
{
  "username": "sanne",
  "password": "welkom123"
}
```

Response bevat een bearer-token.

### Profiel

`GET /api/v2/me`

Geeft het profiel van de ingelogde gebruiker terug.

### Gebruikers

`GET /api/v2/users`

Geeft een lijst met gebruikers terug.

`GET /api/v2/users/{id}`

Geeft details van een gebruiker terug.

`PUT /api/v2/users/{id}`

Wijzigt profielvelden. Voor normale gebruikers is dit bedoeld voor het eigen profiel.

Voorbeeld:

```json
{
  "full_name": "Sanne de Vries",
  "email": "nieuw@student.windesapi.local"
}
```

### Cijfers

`GET /api/v2/users/{id}/grades`

Geeft cijfers van een student terug.

### Cursussen

`GET /api/v2/courses`

Geeft beschikbare cursussen terug.

`GET /api/v2/courses/{id}`

Geeft details van een cursus terug.

### Admin

`GET /api/v2/admin/overview`

Alleen bedoeld voor administrators.

## Oefendoelen

1. Automatiseer login en hergebruik het bearer-token.
2. Breng endpointpatronen in kaart.
3. Vergelijk responses tussen verschillende ID's.
4. Onderzoek of responses meer data bevatten dan nodig is.
5. Test of extra JSON-velden bij updates effect hebben.
6. Zoek naar oude of ontwikkel-endpoints buiten de gedocumenteerde routes.

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
