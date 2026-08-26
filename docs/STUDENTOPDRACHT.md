# Practicum REST-API onderzoeken en beveiligen

## Situatie

Je bent junior API-engineer voor een fictief campusproject. Een lokale API ontsluit projectgegevens, maar is te snel als demo gebouwd. Jij brengt eerst normaal API-gedrag in kaart, automatiseert requests met Python, onderzoekt welke informatie onnodig zichtbaar is en voert daarna zes beveiligingsverbeteringen door. Je bewijst steeds met een waarneming wat er voor en na de wijziging gebeurt.

Alle namen, teams, locaties, codes en projectgegevens in dit lab zijn fictief. De zwakke API is uitsluitend bedoeld voor deze lokale onderwijsomgeving en is geen productievoorbeeld.

## Leerdoelen

Na dit practicum kun je:

1. REST-API, endpoint, HTTP-methode, statuscode, header en JSON-response in eigen woorden uitleggen.
2. Een API met een browser, curl en Python `requests` bevragen.
3. JSON-data selecteren, verwerken en als overzicht rapporteren.
4. Parameters, paginering, authenticatie en foutafhandeling onderzoeken.
5. Herkennen welke technische en inhoudelijke informatie een slecht beveiligde API prijsgeeft.
6. Zes lokale beveiligingsmaatregelen toepassen en voor en na testen.
7. Per maatregel uitleggen wat die oplost, welk bewijs je hebt en welk nadeel of neveneffect ontstaat.

Reken op 5 tot 7 uur. Je hebt Docker Desktop of Docker Engine met Docker Compose v2 nodig. Voor het bewerken gebruik je een teksteditor. Een lokale Python-installatie is handig maar niet verplicht, omdat een clientimage met Python, `requests` en curl is meegeleverd.

## Veilige scope

Je mag alleen requests sturen naar `http://127.0.0.1:8000` en naar de services in je eigen Docker Compose-project. Je mag uitsluitend de meegeleverde fictieve data, je eigen bestanden en je eigen containers onderzoeken. Gebruik geen externe API's, scan geen andere hosts, publiceer de zwakke API niet en wijzig de poortbinding niet naar `0.0.0.0`. Stop direct als een commando onverwacht een ander systeem raakt.

De API bevat bewust onveilig gedrag. Gebruik de code niet als basis voor een echte dienst. De gegenereerde API-key is alleen een lokaal labgeheim; commit of deel deze niet.

## Deel A: omgeving maken en starten

Maak een nieuwe lege map, bijvoorbeeld `api-practicum`. Maak daarin met een teksteditor het bestand `compose.yaml`. Windows-gebruikers: controleer in Verkenner dat het bestand niet ongemerkt `compose.yaml.txt` heet.

Neem de volgende configuratie volledig over.

<!-- standalone-compose:start -->
```yaml
name: windesapi-lab

services:
  api:
    image: ${API_IMAGE:-ghcr.io/gzeel/windesapi-api-lab:latest}
    ports:
      - "127.0.0.1:${LAB_PORT:-8000}:8000"
    environment:
      LAB_WORKSPACE: /workspace
      LAB_SETTINGS_PATH: /workspace/lab-settings.json
      LAB_API_KEY_FILE: /workspace/.api-key
      LAB_DB_PATH: /workspace/lab.db
      LAB_AUDIT_LOG_PATH: /workspace/audit.log
    volumes:
      - ${LAB_WORKSPACE:-./workspace}:/workspace:z
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]
      interval: 5s
      timeout: 4s
      retries: 12
      start_period: 5s
    restart: unless-stopped

  client:
    image: ${CLIENT_IMAGE:-ghcr.io/gzeel/windesapi-api-client:latest}
    profiles: ["tools"]
    environment:
      API_BASE_URL: http://api:8000
      API_KEY_FILE: /workspace/.api-key
    volumes:
      - ${LAB_WORKSPACE:-./workspace}:/workspace:z
    depends_on:
      api:
        condition: service_healthy
```
<!-- standalone-compose:end -->

Maak naast `compose.yaml` alvast een lege map met de naam `workspace`. Gebruik hiervoor je bestandsbeheerder of `mkdir workspace`. De map is daardoor van jouw lokale account en je kunt de geinitialiseerde code later bewerken.

Open een terminal in de map met `compose.yaml`. Valideer de letterlijke configuratie voordat je images ophaalt:

```bash
docker compose config --quiet
```

Geen uitvoer betekent dat de YAML geldig is. Los een fout eerst op; let vooral op inspringing, tabs en de bestandsnaam. Haal daarna de publieke images op. Hiervoor is geen `docker login` nodig:

```bash
docker compose --profile tools pull
```

Initialiseer de beginsituatie uit het image en start de API:

```bash
docker compose run --rm --user 0:0 api lab-reset
docker compose up -d --wait api
docker compose exec api lab-status
```

`lab-reset` initialiseert de map `workspace` met `app/`, `lab-settings.json`, `.api-key`, `client.py` en `rapportage.md`. Alleen dit korte initialisatiecommando draait als root in de container, zodat een lege bind mount ook op Linux gevuld kan worden; de API zelf blijft als niet-rootgebruiker draaien. Een volgende reset herstelt API-code en instellingen, herstelt de database, verwijdert de auditlog en maakt een nieuwe key. Stop de API altijd voor een latere reset en start haar daarna opnieuw. Je eigen `client.py` en `rapportage.md` blijven behouden, maar maak voor de zekerheid zelf een kopie van werk dat je niet wilt verliezen.

Nuttige commando's:

| Doel | Commando |
| --- | --- |
| Beginsituatie herstellen | `docker compose stop api`, daarna `docker compose run --rm --user 0:0 api lab-reset` en `docker compose up -d --wait api` |
| Hulp tonen | `docker compose exec api lab-help` |
| Status testen | `docker compose exec api lab-status` |
| Hardening controleren | `docker compose exec api lab-check` |
| Auditlog tonen | `docker compose exec api lab-log` |
| Wijziging activeren | `docker compose restart api` |
| API-log volgen | `docker compose logs -f api` |
| Stoppen | `docker compose stop` |
| Starten | `docker compose start` |
| Opruimen | `docker compose down --volumes --remove-orphans` |

## Deel B: API-basis en eerste request

Een REST-API biedt resources via URL's. In `GET /api/v1/projects/1` is `/api/v1/projects/1` het endpoint, `GET` de methode en project 1 de resource. De response bestaat uit een statuscode, headers en meestal een body. Deze API gebruikt JSON: objecten met sleutel-waardeparen en lijsten.

Open `http://127.0.0.1:8000/docs` voor de interactieve OpenAPI-weergave. Voer daarna de eerste request volledig uit:

```bash
curl --max-time 5 -i http://127.0.0.1:8000/health
```

Gebruik in Windows PowerShell zo nodig `curl.exe` in plaats van `curl`. Leg in `workspace/rapportage.md` vast:

1. Welke regel de statuscode bevat.
2. Welke header het mediatype van de body beschrijft.
3. Welke JSON-sleutels je ziet.
4. Het verschil tussen deze waarnemingen en jouw interpretatie dat de dienst gezond is.

Onderzoek vervolgens `GET /api/v1/projects`, `GET /api/v1/projects/1` en een niet-bestaand project. Vergelijk de statuscodes `200` en `404`. Voer via `/docs` ook een geldige `POST /api/v1/reports` uit. Noteer waarom `GET` en `POST` niet uitwisselbaar zijn.

## Deel C: eerste Python-client

Bekijk eerst een volledig uitgewerkte, kleine healthcheck. Deze gebruikt een timeout, controleert de statuscode, verwerkt JSON en vangt netwerk- en JSON-fouten af:

```python
import requests

try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    response.raise_for_status()
    data = response.json()
    print(data.get("status", "status ontbreekt"))
except requests.RequestException as exc:
    print(f"Request mislukt: {exc}")
except ValueError as exc:
    print(f"Response is geen geldige JSON: {exc}")
```

Open nu `workspace/client.py`. Werk de `TODO`-regels uit voor de projectenlijst. Je script moet:

- de basis-URL uit `API_BASE_URL` gebruiken;
- `GET /api/v1/projects` met `timeout=5` uitvoeren;
- de statuscode controleren;
- JSON veilig verwerken en rekening houden met ontbrekende sleutels;
- per project minimaal `id`, `title` en `status` tonen;
- netwerkfouten, ongeldige JSON en onverwachte datastructuren begrijpelijk afhandelen;
- een API-key later uit `API_KEY` lezen en nooit hardcoderen.

Test zonder lokale Python-installatie:

```bash
docker compose run --rm client python /workspace/client.py
```

Als je wel lokaal Python en `requests` gebruikt, stel dan eerst de variabelen in.

macOS/Linux:

```bash
export API_BASE_URL=http://127.0.0.1:8000
export API_KEY="$(tr -d '\r\n' < workspace/.api-key)"
python workspace/client.py
```

Windows PowerShell:

```powershell
$env:API_BASE_URL = "http://127.0.0.1:8000"
$env:API_KEY = (Get-Content workspace/.api-key -Raw).Trim()
python workspace/client.py
```

## Deel D: JSON, parameters, paginering en fouten

Gebruik eerst handmatige requests en pas daarna je script aan. Onderzoek de parameters `page`, `limit`, `status` en `sort`. Lees zowel de JSON-velden `page`, `limit`, `total` en `next_page` als de responseheaders `X-Page` en `X-Total-Count`.

Voer de volgende onderzoekstaken uit zonder aannames over de uitkomst:

1. Vraag twee opeenvolgende pagina's met elk drie items op.
2. Filter op een geldige status en tel de resultaten.
3. Probeer grenswaarden en ongeldige waarden voor `page` en `limit`.
4. Probeer een niet-bestaande waarde voor `sort` en leg statuscode en response vast.
5. Selecteer in Python alleen actieve projecten en rapporteer hun `id` en `title`.
6. Pas je script zo aan dat het pagina's volgt totdat `next_page` leeg is, zonder een oneindige lus te kunnen maken.

Beschrijf bij een fout apart wat je letterlijk ontving en wat je daaruit afleidt. Een foutmelding die een framework, database, pad of query noemt is zelf ook een API-response die mogelijk te veel onthult.

## Deel E: informatieblootstelling onderzoeken

Onderzoek de beginsituatie als een gewone client. Bekijk lijst- en detailresponses, responseheaders, CORS-gedrag en toegang tot verschillende project-ID's. Een CORS-preflight kun je lokaal uitvoeren met:

```bash
curl --max-time 5 -i -X OPTIONS http://127.0.0.1:8000/api/v1/projects \
  -H "Origin: https://niet-vertrouwd.example" \
  -H "Access-Control-Request-Method: GET"
```

PowerShell-gebruikers zetten dit desgewenst op één regel met `curl.exe`.

Beantwoord op basis van bewijs:

1. Is authenticatie nodig voor projectdata?
2. Kan de vaste student-analist een project van team Echo opvragen?
3. Welke velden zijn nodig voor het projectoverzicht en welke lijken intern?
4. Is het aantal resultaten begrensd en is ongeldige invoer voorspelbaar afgehandeld?
5. Welke technische productinformatie wordt zichtbaar?
6. Welke oorsprongen mogen via een browser een cross-origin request doen?
7. Kun je in korte tijd veel requests uitvoeren en ontstaat daarbij een beveiligingslog?

De codes en locaties zijn fictief, maar behandel de vraag alsof het echte interne bedrijfsinformatie was. Kopieer `.api-key` niet naar je rapport.

## Deel F: code en configuratie lezen

Lees `workspace/lab-settings.json`, `workspace/app/main.py`, `workspace/app/settings.py` en `workspace/app/database.py`. Maak een gegevensstroom van request naar response: route, authenticatie, databasequery, selectie van velden en response.

Zoek voor iedere waargenomen zwakke plek de relevante instelling en code. Noteer regelnummers of functienamen. Leg uit waarom alleen een frontendveld verbergen geen server-side beveiliging is. Wijzig nog niets voordat je de voor-waarnemingen hebt bewaard.

## Deel G: API hardenen

Voer ongeveer zes samenhangende verbeteringen uit. Wijzig `workspace/lab-settings.json`; je mag daarnaast de API-code aanpassen als je een beter onderbouwde oplossing kiest. Herstart na iedere wijziging en test zowel de blokkade als een geldige use-case.

### Maatregel 1: API-key verplichten, volledig voorbeeld

Dit eerste voorbeeld is volledig begeleid. Wijzig in `workspace/lab-settings.json` alleen:

```json
"require_api_key": true
```

Herstart de API:

```bash
docker compose restart api
```

Bewijs daarna twee kanten:

```bash
curl --max-time 5 -i http://127.0.0.1:8000/api/v1/projects
docker compose run --rm client python /workspace/client.py
```

De eerste request hoort niet geauthenticeerd te zijn. De clientcontainer leest de gegenereerde key bij het starten uit `.api-key`, zet deze in de environmentvariabele `API_KEY` en jouw script moet die als `X-API-Key` meesturen. Sla de key zelf niet op in code, Compose of rapportage. Leg uit waarom een key authenticatie toevoegt maar nog niet bepaalt tot welk object de analist toegang heeft.

### Maatregel 2: objectautorisatie, alleen aanwijzingen

Voorkom dat de student-analist projecten van een ander team kan lezen of er een rapport voor kan maken. Zoek waar `owner_id` wordt vergeleken met de huidige gebruiker en welke instelling die controle activeert. Bewijs met minstens één toegestaan Delta-project en één geweigerd Echo-project dat de API niet simpelweg kapot is gemaakt.

### Maatregelen 3 tot en met 6: zelfstandig

Ontwerp, activeer en test daarna zelfstandig maatregelen voor:

- dataminimalisatie in lijst- en detailresponses;
- invoervalidatie en een redelijke maximale paginagrootte;
- generieke foutafhandeling, minder software-informatie, beveiligingsheaders en beperkte CORS;
- rate limiting plus logging van mislukte authenticatie, geweigerde objecttoegang en overschrijding van de limiet.

Gebruik de code, je eerdere waarnemingen, `/docs` en `lab-check` als feedback. Laat gewone requests naar eigen projecten en het maken van een geldig rapport werken. Een API die alle requests afwijst is niet correct gehard.

## Deel H: voor-en-na-controles

Herstart de API en voer uit:

```bash
docker compose exec api lab-status
docker compose exec api lab-check
docker compose exec api lab-log
```

`lab-check` is feedback, geen vervanging voor je eigen bewijs. Het commando stuurt veel requests om rate limiting te testen; wacht zo nodig tien seconden voordat je verder test.

Maak een compacte regressieset die minstens controleert:

- healthcheck zonder authenticatie;
- lijst en detail van een toegestaan project met key;
- ontbrekende of verkeerde key;
- project van een ander team;
- geldige en ongeldige paginaparameters;
- minimale JSON-velden;
- geldige `POST /api/v1/reports` met status `201`;
- veilige foutresponse en relevante headers;
- rate-limitstatus `429` en een bijbehorende auditlogregel.

Bewaar statuscode, relevante headers en een beperkte JSON-fragment als bewijs. Neem geen key op. Controleer na alle beveiliging opnieuw dat je Python-script via de clientcontainer werkt.

## Deel I: rapportage en reflectie

Werk `workspace/rapportage.md` uit. Maak voor ieder van de zes maatregelen een aparte sectie met exact deze structuur:

```text
Zwakke plek:
Wat kon iemand hiermee:
Waarneming voor:
Wijziging:
Waarneming na:
Waarom dit bewijs de conclusie ondersteunt:
Nadeel of neveneffect:
```

Een waarneming is bijvoorbeeld een statuscode, header of aanwezig JSON-veld. Een interpretatie is jouw conclusie over risico of werking. Meng deze niet. Bespreek in je reflectie ook:

1. Welke maatregel de meeste invloed op clients had.
2. Waarom authenticatie en autorisatie verschillende controles zijn.
3. Waarom dataminimalisatie ook bij fictieve of openbare brondata relevant is.
4. Welke beperkingen de eenvoudige lokale rate limiter heeft in een gedistribueerde productieomgeving.
5. Welke aanvullende productiemaatregelen buiten de scope van dit lab vallen.

## Inleveren

Lever uit je lokale map minimaal in:

- `workspace/client.py`;
- `workspace/lab-settings.json`;
- aangepaste bestanden onder `workspace/app/` als je code hebt gewijzigd;
- `workspace/rapportage.md` met zes voor-en-na-analyses en reflectie.

Lever niet in: `workspace/.api-key`, `workspace/lab.db`, `workspace/audit.log`, caches of containerimages. Stop en ruim na beoordeling op met:

```bash
docker compose down --volumes --remove-orphans
```
