# Architect en Red Team Overleg

## Thema

De demo gebruikt **WindesAPI** als fictieve OSINT-caseomgeving. Studenten spelen de rol van junior analyst en onderzoeken fictieve organisaties, personen, social handles en bronnen binnen een lokale labscope.

## Besluitvorming

**Architect:** We bouwen de hoofdflow rond `/api/v2/osint`: dashboard, analysts, cases, subjects, profiles en sources.

**Red Teamer:** De kwetsbaarheden moeten logisch passen bij OSINT: te brede case-toegang, te rijke subject-responses, oude crawlerexports en privilege escalation via analyst-profielen.

**Architect:** Authenticatie blijft een eenvoudige bearer-token-sessie in SQLite, zodat studenten met curl, Postman, Python of Burp Suite kunnen oefenen.

**Red Teamer:** Voor BOLA gebruiken we numerieke case-ID's. Sanne mag haar eigen case `201` zien, maar kan ook case `202` opvragen en restricted notes vinden.

**Architect:** De frontend zou normaal alleen publieke OSINT-samenvattingen tonen.

**Red Teamer:** Daarom laten `/api/v2/osint/subjects` en `/api/v2/osint/sources` bewust te veel zien, zoals fictieve e-mails, telefoons, private addresses, gelekte wachtwoorden, raw source JSON en API-keys.

**Architect:** Voor improper assets management voegen we een legacy crawlerexport toe buiten de studentdocumentatie.

**Red Teamer:** `/api/v1/osint/export` vereist bewust geen authenticatie en lekt cases, subjects, profiles en source-keys.

**Architect:** Voor mass assignment gebruiken we een analyst-update die extra velden accepteert.

**Red Teamer:** Daardoor kan Sanne bij `PUT /api/v2/osint/analysts/101` velden zoals `"is_admin": true`, `"can_export": true` en `"clearance_level": "admin"` meesturen.

## Endpoint Matrix

| Endpoint | Auth | Bedoelde functie | Bewuste kwetsbaarheid |
| --- | --- | --- | --- |
| `POST /api/v2/auth/login` | Nee | Login met demo-account | Plaintext wachtwoorden in seed-data |
| `GET /api/v2/osint/dashboard` | Ja | Analyst-overzicht | Geen hoofdkwetsbaarheid |
| `GET /api/v2/osint/analysts` | Ja | Analyst-lijst | Excessive Data Exposure |
| `PUT /api/v2/osint/analysts/{id}` | Ja | Eigen profiel wijzigen | Mass Assignment |
| `GET /api/v2/osint/cases` | Ja | Case-lijst | ID-enumeratie mogelijk |
| `GET /api/v2/osint/cases/{id}` | Ja | Case-details | BOLA / IDOR |
| `GET /api/v2/osint/subjects` | Ja | Subject-lijst | Excessive Data Exposure |
| `GET /api/v2/osint/subjects/{id}/profiles` | Ja | Social profiles | Metadata-lek |
| `GET /api/v2/osint/sources` | Ja | Bronconfiguratie | Excessive Data Exposure |
| `GET /api/v2/admin/overview` | Admin | Adminoverzicht | Bereikbaar na Mass Assignment |
| `GET /api/v1/osint/export` | Nee | Legacy crawlerexport | Shadow API |
| `GET /api/v1/admin/export` | Nee | Legacy globale export | Shadow API |
