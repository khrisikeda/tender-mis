# Medical Tender Intelligence & Bid Management System — MVP Foundations

This is the first coding milestone from the MVP roadmap: **authentication,
role-based access control, database schema, and tender source management.**
Collection/extraction/matching modules come next, built on top of this
foundation.

## What's included

- **Auth**: JWT-based login/refresh, admin-only user creation, password hashing (bcrypt)
- **RBAC**: 7 roles (admin, management, sales, biomedical_engineer, procurement, finance, viewer), enforced server-side on every protected endpoint
- **Tender Source Management**: full CRUD for the sources the (future) collection service will scan, including compliance fields (robots.txt status, manual-import flag) and health tracking (last scan, last error, tenders collected)
- **Audit log**: append-only, written on every create/update/status-change/login — nothing is silently deleted

## Project structure

```
app/
  core/          settings, security (JWT/bcrypt), RBAC dependency, audit helper, enums
  models/        SQLAlchemy models (User, Role, TenderSource, AuditLog)
  schemas/       Pydantic request/response schemas
  routers/       API endpoints (auth, tender-sources)
  database.py    engine/session setup
  main.py        FastAPI app entrypoint
scripts/
  seed.py        creates roles + first admin user
requirements.txt
.env.example      copy to .env and fill in real values
```

## Setup

1. **Create a PostgreSQL database** and user matching what you'll put in `.env`.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # edit .env: set DATABASE_URL and a real random SECRET_KEY
   ```
   Generate a secret key: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

4. **Seed roles and create the first admin user:**
   ```bash
   python -m scripts.seed
   ```
   This creates all tables (dev convenience — see note below on migrations), seeds the 7 roles, and interactively creates your first admin account.

5. **Run the API:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

## Using it

1. `POST /auth/login` (form data: `username`=email, `password`) → returns `access_token` + `refresh_token`
2. Use `Authorization: Bearer <access_token>` on subsequent requests
3. `GET /auth/me` → confirm who you're logged in as and your role
4. `POST /auth/users` (admin only) → create Sales/Engineer/Finance/etc. accounts for your team
5. `GET /tender-sources` → list sources (any authenticated user)
6. `POST /tender-sources` (admin/management only) → register a new source to monitor, e.g.:
   ```json
   {
     "name": "Rwanda Public Procurement Authority",
     "website": "https://www.rppa.gov.rw",
     "country": "Rwanda",
     "category": "government_portal",
     "collection_method": "webpage",
     "scan_frequency_hours": 24
   }
   ```

## Important notes

- **Migrations**: `scripts/seed.py` uses `Base.metadata.create_all()` for local development convenience. Before this touches a real/shared database, switch to **Alembic** migrations (`alembic init`, then `alembic revision --autogenerate`) so schema changes are tracked and reversible.
- **RBAC is enforced in the API layer** (`app/core/deps.py::require_roles`), not just hidden in the UI — this matches the spec requirement that permissions be a real boundary, not cosmetic.
- **Sources are deactivated, not deleted** (`POST /tender-sources/{id}/deactivate`) to preserve audit/collection history, per the "no silent deletion" requirement.
- **Compliance fields on TenderSource** (`robots_txt_allows_collection`, `requires_manual_import`) exist so the next module — the collection service — can refuse to scan anything that isn't legitimately allowed, and fall back to flagging it for manual import instead.

## What's next (per the MVP roadmap)

1. Collection service: scheduled fetchers per source, respecting the compliance fields already in the schema
2. Extraction service: PDF/DOCX/HTML parsing into structured `Tender` records with field-level provenance
3. Classification + duplicate detection
4. Product catalogue + basic product matching
5. Relevance scoring + dashboard feed

Let me know when you're ready for the next module and I'll build it on top of this same codebase.
