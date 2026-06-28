Database
--------
- All timestamps are stored in UTC.

Request
-------
- Datetime values sent by the frontend must be naive local datetimes.
- Query APIs that only filter by calendar date should use YYYY-MM-DD.

Backend
-------
- Naive local datetimes are interpreted using BUSINESS_TZ.
- They are converted to UTC before persisting.
- Query dates are expanded to BUSINESS_TZ day boundaries before querying.

Response
--------
- API responses always return ISO-8601 datetimes with timezone offsets.
- The frontend is responsible for displaying datetimes in the appropriate timezone.

Future
------
- BUSINESS_TZ is currently a global configuration.
- It may later become company.timezone to support multi-timezone organizations.


```
Frontend
───────────────
Create Shift
2026-07-01 09:00
(naive local datetime)

        │

Backend
───────────────
Interpret as BUSINESS_TZ
↓

Convert to UTC

        │

Database
───────────────
2026-07-01T01:00:00Z

        │

API Response
───────────────
2026-07-01T01:00:00+00:00

        │

Frontend
───────────────
Display using company timezone
```
