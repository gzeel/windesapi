# Containerimages

Het practicum gebruikt bewust twee images. Zo blijft de API-image klein en niet-root, terwijl studenten zonder lokale Python-installatie dezelfde versie van `requests` en curl kunnen gebruiken. De scheiding maakt bovendien netwerkverkeer tussen een client- en API-container zichtbaar.

## Publieke packages

| Image | Inhoud |
| --- | --- |
| `ghcr.io/gzeel/windesapi-api-lab` | FastAPI-runtime, fictieve begintemplate en `lab-*`-commando's |
| `ghcr.io/gzeel/windesapi-api-client` | Python, `requests` en curl |

Beide images ondersteunen `linux/amd64` en `linux/arm64`. Beschikbare tags:

- `latest`: laatste geslaagde publicatie vanaf `main`;
- `sha-<commit>`: onveranderlijke verwijzing naar een specifieke broncommit.

Studenten hoeven geen `docker login` uit te voeren. Beide GHCR-packages moeten de zichtbaarheid **Public** hebben. Als een nieuwe package na de eerste workflowrun nog Private is, open op GitHub de package, kies **Package settings**, ga naar **Danger Zone > Change package visibility** en zet deze op **Public**. Herhaal dit voor beide packages en test daarna uitgelogd met `docker pull`.

## Veiligheids- en runtimekeuzes

- De API bindt in de student-Compose alleen aan `127.0.0.1`.
- Beide runtime-images draaien als gebruiker met UID 10001 en bevatten geen echte secrets.
- `lab-reset` genereert lokaal een willekeurige API-key in de bind mount; die staat niet in het image of Compose.
- De API-image heeft een HTTP-healthcheck en start Uvicorn zonder `Server`-header.
- Images zijn gelabeld als lokaal onderwijs-lab en geen productievoorbeeld.
- Beide images gebruiken een kleine, actuele Python Alpine-base.
- Directe en transitieve Python-dependencies zijn op versies vastgezet en base-images op multi-architecture digests. Alpine voert tijdens beide builds beveiligingsupdates uit en kiest binnen release 3.24 de actuele revision van curl. GitHub Actions bouwt met Buildx, QEMU en registrycache.

## Lokaal bouwen

```bash
docker build --target runtime -t windesapi-api-lab:dev .
docker build -f client/Dockerfile -t windesapi-api-client:dev .
```

De publicatieworkflow voegt OCI-labels voor bronrepository, revisie, aanmaakdatum, titel, beschrijving en licentie toe.
