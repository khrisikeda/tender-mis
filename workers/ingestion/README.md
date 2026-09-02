# Tender MIS Ingestion Worker (Node.js / TypeScript)

A resilient two-tier tender synchronization worker for Rwanda's e-Procurement portal (Umucyo) and Open Contracting Data Standard (OCDS) API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Two-Tier Ingestion Strategy                   │
├──────────────────────────────┬──────────────────────────────┤
│ Tier 1: Primary Discovery    │ Tier 2: Deep Fallback Scraper│
│ (Official OCDS API)          │ (Umucyo .do Portal)          │
├──────────────────────────────┼──────────────────────────────┤
│ - Base: /api/v1/releases     │ - Parameterized detail links:│
│ - Idempotent upsert on ocid  │   ?adv_no=...&adv_status=... │
│ - Routine metadata syncs     │ - Session cookie management  │
│ - Zero layout/DOM dependence │ - Exponential backoff retry  │
│ - Offline snapshot fallback  │ - Dead-letter queue capture  │
└──────────────────────────────┴──────────────────────────────┘
```

## Setup & Running

```bash
cd workers/ingestion
npm install

# Run complete two-tier sync
npm run sync:all

# Run Tier 1 (Official OCDS API) only
npm run sync:ocds

# Run Tier 2 (Portal Fallback Scraper) only
npm run sync:portal

# Run test verification
npm test
```

## Dead-Letter Queue

Any non-200 HTTP responses, timeouts, or parsing errors are captured without crashing the service into `../../storage/dead_letters.json`.
Each dead-letter record tracks:
- ISO timestamp
- Endpoint URL & HTTP method
- HTTP status code
- Full error message
- Query/body parameters for retry & replay
