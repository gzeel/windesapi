# WindesAPI API-practicum

WindesAPI is een volledig lokaal, Nederlandstalig HBO-practicum over REST-API's, Python-clients en API-hardening. De FastAPI-app bevat uitsluitend fictieve projectdata en zes bewust ingebouwde, lokaal aantoonbare zwakke plekken. Het project is nadrukkelijk geen productievoorbeeld.

## Documentatie

- [Zelfstandige studentopdracht](docs/STUDENTOPDRACHT.md): het enige document dat aan studenten wordt uitgedeeld.
- [Docenthandleiding](docs/DOCENTHANDLEIDING.md): oplossingen, verwachte resultaten en nakijkmodel; niet uitdelen.
- [Containerimages](docs/IMAGES.md): image-inhoud, tags, platformen en publicatie.

De studentopdracht bevat de volledige veilige scope en Compose-configuratie. Studenten hebben geen toegang tot deze repository nodig.

## Ontwikkelen

Vereisten: Docker Engine of Docker Desktop met Compose v2.

```bash
docker compose -f compose.yaml -f compose.dev.yaml config --quiet
docker compose -f compose.test.yaml build test
docker compose -f compose.test.yaml run --rm test
```

Start een lokale ontwikkelversie:

```bash
docker compose -f compose.yaml -f compose.dev.yaml build
mkdir -p workspace
docker compose -f compose.yaml -f compose.dev.yaml run --rm --user 0:0 api lab-reset
docker compose -f compose.yaml -f compose.dev.yaml up -d --wait api
docker compose -f compose.yaml -f compose.dev.yaml exec api lab-status
```

Opruimen:

```bash
docker compose -f compose.yaml -f compose.dev.yaml down --volumes --remove-orphans
```

De standaard werkmap is `workspace/` en wordt niet gecommit. Zet `LAB_WORKSPACE` op een andere map om tests te isoleren.

## Validatie

De volledige zelfstandige route vanuit een lege tijdelijke map wordt getest met:

```bash
SKIP_PULL=1 API_IMAGE=windesapi-api-lab:dev CLIENT_IMAGE=windesapi-api-client:dev sh tests/standalone-smoke.sh
```

De test extraheert het YAML-blok letterlijk uit de studentopdracht, valideert Compose voor het ophalen van images, initialiseert beginbestanden, start de API, voert een clientrequest uit, controleert de geharde situatie en ruimt containers en netwerken op.

## Structuur

```text
app/                 FastAPI-app die in het labimage als begintemplate wordt geleverd
client/              Clientimage met Python, requests en curl
docker/              Labcommando's
docs/                Student-, docent- en imagedocumentatie
solution/            Gehard instellingenprofiel voor docenten en tests
templates/           Lokale studentbestanden die lab-reset initialiseert
tests/               API-, documentatie- en standalone tests
compose.yaml         Canonieke zelfstandige Compose-configuratie
compose.dev.yaml     Lokale build-overrides
compose.test.yaml    Geisoleerde testservice
```

## Publicatie

GitHub Actions test pull requests en pushes. Alleen een push naar `main` publiceert multi-architecture images voor `linux/amd64` en `linux/arm64` naar GHCR met `latest` en `sha-<commit>` tags. Zie [docs/IMAGES.md](docs/IMAGES.md).
