# Docenthandleiding API-practicum

Niet aan studenten uitdelen. Dit document bevat de volledige oplossing en verwachte resultaten.

## Doelgroep, leerdoelen en duur

Doelgroep: HBO-ICT-studenten met basiskennis Python en containers. Reken op 5 tot 7 uur, eventueel verdeeld over twee bijeenkomsten. Studenten leren HTTP- en REST-begrippen toepassen, JSON met Python verwerken, parameters en paginering onderzoeken, informatieblootstelling herkennen, zes controls doorvoeren en bewijs van interpretatie onderscheiden.

## Opzet en wat echt of gesimuleerd is

De HTTP-requests, FastAPI-validatie, SQLite-query's, CORS-responses, API-keyvergelijking, objectcontrole, responsefiltering, in-memory rate limiter en JSONL-auditlog zijn echt werkende implementaties. Alle personen, teams, locaties, codes, leveranciersgegevens en projecten zijn fictief. De `supplier_access_code`-waarden zijn demonstratietekst en geen werkende secrets. De rate limiter is bewust proceslokaal en niet geschikt voor meerdere replicas. De API-key identificeert in dit lab één vaste fictieve analist; een echte identityprovider valt buiten scope.

## Ingebouwde beginsituatie

| Nr. | Zwakke plek | Voor-waarneming | Risico |
| --- | --- | --- | --- |
| 1 | Geen verplichte authenticatie | Projectlijst geeft zonder `X-API-Key` status `200` | Iedereen met netwerktoegang kan lezen |
| 2 | Geen objectautorisatie | Analist 101 leest project 2 van owner 102 | BOLA/IDOR en teamoverschrijding |
| 3 | Te rijke responses | Velden zoals `budget_eur`, `internal_location`, `supplier_access_code` en `internal_notes` zijn zichtbaar | Excessive data exposure |
| 4 | Zwakke validatie en onbeperkte paginagrootte | `limit=1000` werkt; ongeldige sortering veroorzaakt `500` | Resourcegebruik en onvoorspelbaar gedrag |
| 5 | Technische fouten, productheader en open CORS | Foutbody noemt exception, SQLite, query en pad; `X-Powered-By`; origin `*` | Reconnaissance en browsertoegang vanaf elke origin |
| 6 | Geen rate limiting of securitylogging | Meer dan 15 snelle requests blijven werken; geen `audit.log` | Misbruik wordt niet afgeremd of zichtbaar |

## Volledige oplossing

De canonieke oplossing staat in `solution/hardened-settings.json`:

```json
{
  "require_api_key": true,
  "enforce_project_ownership": true,
  "minimal_responses": true,
  "validate_queries": true,
  "safe_errors_headers_cors": true,
  "rate_limit_and_log": true
}
```

De student kan deze zes waarden zelf activeren. Een inhoudelijk betere codewijziging is ook geldig als de gedragstests slagen en de afweging goed is onderbouwd.

## Verwachte resultaten na hardening

| Controle | Verwacht |
| --- | --- |
| `/health` zonder key | `200`, zodat containerhealth blijft werken |
| Projectlijst zonder of met verkeerde key | `401` |
| Project 1 met gegenereerde key | `200` |
| Project 2 met key van analist 101 | `403` |
| Projectlijst met key | Alleen IDs 1, 3, 5, 7, 9 en 11, afhankelijk van pagina |
| Lijst- en detailvelden | Alleen `id`, `title`, `status`, `category`, `summary` |
| `limit=21`, `page=0`, ongeldige status of sortering | `422` met beperkte fouttekst |
| Geldig rapport voor project 1 | `201` |
| Rapport voor project 2 | `403` |
| Responseheaders | `X-Content-Type-Options: nosniff`, `Cache-Control: no-store`, geen `X-Powered-By` of Uvicorn `Server`-header |
| CORS-origin `https://niet-vertrouwd.example` | Geen `Access-Control-Allow-Origin` |
| CORS-origin `http://127.0.0.1:5500` | Origin expliciet toegestaan |
| Zestiende snelle API-request vanaf dezelfde client | `429` en `Retry-After: 10` |
| Auditlog | JSON-regels voor `authentication_failed`, `authorization_denied` en `rate_limit` |

`lab-check` test deze gedragingen. Omdat het rate limiting als laatste controleert, kan direct daarna kort een `429` volgen. De window verloopt na tien seconden.

## Begeleiding

Werk klassikaal alleen de healthcheck, begrippen en eerste authenticatiemaatregel uit. Vraag bij objectautorisatie steeds om zowel een toegestane als geweigerde testcase. Geef bij de overige maatregelen eerst vragen in plaats van instellingen: welk veld hoort bij de client, wat is een grenswaarde, wat hoeft een foutgebruiker te weten, en welk event moet een beheerder kunnen terugvinden?

Laat studenten voor iedere conclusie eerst statuscode, header of JSON-fragment aanwijzen. Accepteer geen screenshot zonder context van requestmethode en endpoint. Laat ze bij rate limiting uitleggen dat een lokale deque niet gedeeld wordt tussen processen of replicas.

## Veelvoorkomende fouten

- `compose.yaml.txt` op Windows of tabs/verkeerde YAML-inspringing.
- Een oude Docker Compose v1 gebruiken in plaats van `docker compose`.
- Poort 8000 is al bezet; laat de student het conflicterende lokale proces stoppen, niet de binding openbaar maken.
- `client.py` bevat nog `NotImplementedError` of stuurt de key onder de verkeerde headernaam.
- De key wordt letterlijk in Python geplakt in plaats van uit `API_KEY` gelezen.
- Na een configuratiewijziging is `docker compose restart api` vergeten.
- Een JSON-boolean staat als string (`"true"`) in plaats van `true`.
- De student gebruikt project 2 als positieve test en denkt dat `403` betekent dat alles stuk is.
- `lab-check` veroorzaakt bewust een korte rate-limitwindow.
- Een reset is uitgevoerd zonder eerst eigen code buiten `workspace/app` te kopieren; `client.py` en rapportage blijven wel behouden.
- Alleen de frontendoutput wordt aangepast terwijl de ruwe API-response gevoelig blijft.

## Nakijkcriteria (100 punten)

| Onderdeel | Punten | Criteria |
| --- | ---: | --- |
| API-basis en scope | 10 | Begrippen correct, scope gevolgd, methoden/statuscodes/headers benoemd |
| Python-client | 20 | Timeout, statuscontrole, veilige JSON-verwerking, relevante velden, foutafhandeling, environmentkey, paginering |
| Onderzoek beginsituatie | 15 | Zes zwakke plekken met reproduceerbare voor-waarnemingen |
| Hardening | 30 | Zes controls werken; legitieme GET en POST blijven werken; geen hardcoded key |
| Bewijs en rapportage | 20 | Per maatregel volledig format, voor/na, waarneming gescheiden van interpretatie, nadeel besproken |
| Reflectie en afwerking | 5 | Heldere productiebeperkingen, nette inlevering zonder key/database |

Geef bij hardening per control maximaal 5 punten: 2 voor juiste werking, 1 voor negatieve test, 1 voor positieve regressietest en 1 voor onderbouwd neveneffect. Een API die alle requests weigert krijgt geen punten voor functionele hardening.

## Vooraf standalone testen

Test altijd het exacte studentdocument vanuit een lege tijdelijke map, niet vanuit repositorybestanden:

1. Bouw lokaal met `docker compose -f compose.yaml -f compose.dev.yaml build`.
2. Voer `SKIP_PULL=1 API_IMAGE=windesapi-api-lab:dev CLIENT_IMAGE=windesapi-api-client:dev sh tests/standalone-smoke.sh` uit.
3. Test na publicatie nogmaals zonder `SKIP_PULL` en met de GHCR-image-URLs.
4. Controleer op een machine zonder GHCR-login dat `docker pull ghcr.io/gzeel/windesapi-api-lab:latest` en de clientimage werken.
5. Controleer zowel amd64 als arm64 via de manifestgegevens of op twee platforms.

De smoketest extraheert de letterlijke YAML uit de opdracht, voert eerst `docker compose config --quiet` uit, initialiseert bestanden, controleert health en een Python-request vanuit de clientcontainer, activeert het geharde profiel, test legitieme functionaliteit en controleert opruimen van containers en netwerken.
