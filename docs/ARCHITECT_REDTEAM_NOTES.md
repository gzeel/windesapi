# Architect en Red Team Overleg

## Thema

De demo gebruikt het fictieve studentenportaal **WindesAPI**. Studenten kunnen inloggen, hun profiel bekijken, cursussen en cijfers ophalen en een beperkt adminscherm ontdekken.

## Besluitvorming

**Architect:** We bouwen een realistische REST API rond studenten, cursussen, cijfers en supporttickets. De hoofdversie is `/api/v2`, zodat er ruimte is voor een oude API-versie.

**Red Teamer:** De kwetsbaarheden moeten logisch aanvoelen en niet afhankelijk zijn van crashes of race conditions. Elke kwetsbaarheid krijgt een herkenbare datavondst of flag in de seed-data.

**Architect:** Authenticatie wordt een simpele bearer-token-sessie in SQLite. Dat is begrijpelijk voor studenten en makkelijk te inspecteren met Postman of curl.

**Red Teamer:** Voor BOLA gebruiken we numerieke student-ID's. Een gebruiker kan `/api/v2/users/101` opvragen en daarna het ID aanpassen naar `102` of `103`.

**Architect:** De frontend zou normaal maar een subset tonen, maar API-responses mogen intern meer velden bevatten.

**Red Teamer:** Daarom laten `/api/v2/users` en `/api/v2/courses` gevoelige velden teruggeven zoals plaintext wachtwoorden, interne notities en answer keys.

**Architect:** Voor legacy assets voegen we endpoints buiten de v2-documentatie toe.

**Red Teamer:** `/api/v1/admin/export` en `/api/dev/users` vereisen bewust geen authenticatie en lekken systeemdata.

**Architect:** Voor mass assignment gebruiken we een profielupdate die alle databasekolommen accepteert die technisch schrijfbaar zijn.

**Red Teamer:** Daardoor kan een student bij `PUT /api/v2/users/{eigen_id}` extra JSON meesturen, zoals `"is_admin": true`, en daarna `/api/v2/admin/overview` openen.

## Endpoint Matrix

| Endpoint | Auth | Bedoelde functie | Bewuste kwetsbaarheid |
| --- | --- | --- | --- |
| `POST /api/v2/auth/login` | Nee | Login met demo-account | Plaintext wachtwoorden in database |
| `GET /api/v2/me` | Ja | Eigen profiel bekijken | Geen hoofdkwetsbaarheid |
| `GET /api/v2/users` | Ja | Gebruikerslijst | Excessive Data Exposure |
| `GET /api/v2/users/{id}` | Ja | Profieldetails | BOLA / IDOR |
| `PUT /api/v2/users/{id}` | Ja | Profiel wijzigen | Mass Assignment |
| `GET /api/v2/users/{id}/grades` | Ja | Cijfers bekijken | BOLA / IDOR plus privacy-lek |
| `GET /api/v2/courses` | Ja | Cursuslijst | Excessive Data Exposure |
| `GET /api/v2/admin/overview` | Admin | Adminoverzicht | Bereikbaar na Mass Assignment |
| `GET /api/v1/admin/export` | Nee | Legacy export | Shadow API |
| `GET /api/dev/users` | Nee | Dev-dump | Shadow API |
