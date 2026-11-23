> **Windows beta 1.9.3.1.** See the [GitHub release](https://github.com/townlight/townlight/releases/tag/townlight-windows-v1.9.3.1) for downloads.

<a id="civicgrants"></a>

# Townlight Grants

Townlight Grants 0.3.0 is packaged with Windows beta 1.9.3.1. Staff can draft an opportunity, assign it to a named staff member, review it against an adopted Budget revision, a signed Contract and a Records request, then record the award, complete its reporting and download a verified closeout archive. The standalone API provides advisory workpapers and retains its original routes and settings. See the [GitHub release](https://github.com/townlight/townlight/releases/tag/townlight-windows-v1.9.3.1).

Townlight Grants is the Townlight module for grant opportunity triage, eligibility-factor matching, application outline support, compliance-calendar scaffolding, staff review queues, review-required Townlight Records grant context packets, adversarial local integration mocks, and audit-ready grant files.

Current state: **v0.3.0 grant support and staff review queue runtime**. This repo ships a FastAPI package using Townlight Core 1.3.0.dev2, health/root endpoints, documentation gates, deterministic and database-backed grant opportunity triage, compliance-calendar records, staff-only review queue workflows, review-required CivicRecords/grant-file context packets, adversarial local integration mocks, application outline helper, audit-ready export checklist, and accessible public sample UI at `/civicgrants`. It does **not** ship live funder feeds, official eligibility decisions, legal advice, live LLM calls, submission portals, award acceptance, or grant system-of-record integrations.

<a id="what-civicgrants-does"></a>

## What Townlight Grants Does

- Triage sample grant opportunities and recommend a staff owner.
- Match sample eligibility factors that staff must verify.
- Draft application outlines for staff review.
- Build compliance-calendar scaffolds for awarded grants.
- Persist grant opportunity and compliance-calendar records when `CIVICGRANTS_GRANT_DB_URL` is configured.
- Route grant review work through staff-only queue endpoints protected by `CIVICGRANTS_STAFF_API_KEY`.
- Carry Townlight Records and grant-file context IDs into review-required packets without calling those systems live.
- Validate adversarial local integration mocks for spoofed roles, official eligibility attempts, submission attempts, award-acceptance attempts, legal-advice claims, stale context, and live funder-feed claims.
- Produce audit-ready export checklists for grant files.
- Demonstrate a public grant-support UI at `/civicgrants`.

<a id="what-civicgrants-does-not-do"></a>

## What Townlight Grants Does Not Do

- It does not decide official eligibility.
- It does not submit grant applications.
- It does not accept grant awards.
- It does not provide legal advice.
- It does not call live LLMs or live funder feeds in this recovery release.
- It does not replace a grant management system of record.

<a id="civiccore-dependency"></a>

## Townlight Core Dependency

Townlight Grants installs against the pinned Townlight Core source:

```bash
python -m pip install "townlight-core @ git+https://github.com/townlight/core.git@2f6ba9be4a95e3772dc47a3682ac780c5283b626"
```

## API Surface

- `GET /` returns the shipped/planned boundary.
- `GET /health` returns package and Townlight Core versions.
- `GET /civicgrants` returns the accessible public sample UI.
- `POST /api/v1/civicgrants/opportunities/triage` returns sample opportunity triage.
- `POST /api/v1/civicgrants/eligibility/match` returns staff-review eligibility factors.
- `POST /api/v1/civicgrants/applications/outline` returns an application outline and a `staff_review_id` when persistence is configured.
- `POST /api/v1/civicgrants/compliance/calendar` returns compliance reminders and a `compliance_id` when persistence is configured.
- `GET /api/v1/civicgrants/compliance/{compliance_id}` retrieves a persisted compliance calendar when `CIVICGRANTS_GRANT_DB_URL` is configured.
- `POST /api/v1/civicgrants/context/grant-review` returns review-required CivicRecords/grant-file context.
- `POST /api/v1/civicgrants/integrations/mock/grant-context` validates local adversarial integration payloads.
- `POST /api/v1/civicgrants/staff/reviews` creates a staff-only review queue item.
- `GET /api/v1/civicgrants/staff/reviews` lists staff-only review queue items.
- `PATCH /api/v1/civicgrants/staff/reviews/{review_id}` updates staff-only queue status, assignment, and resolution.
- `GET /api/v1/civicgrants/staff/reviews/summary` returns staff queue counts.
- `POST /api/v1/civicgrants/export` returns an audit-file export checklist.

## Optional Persistence And Staff Queue

Set `CIVICGRANTS_GRANT_DB_URL` to enable local SQLAlchemy-backed grant records:

```bash
export CIVICGRANTS_GRANT_DB_URL="sqlite+pysqlite:///./civicgrants.db"
```

Set `CIVICGRANTS_STAFF_API_KEY` before using staff-only review routes:

```bash
export CIVICGRANTS_STAFF_API_KEY="replace-with-city-secret"
```

Staff routes require `X-CivicGrants-Role: staff` and `X-CivicGrants-Staff-Key` matching the configured key. Townlight Grants uses Townlight Core `staff_key_gate` for timing-safe key comparison. Without persistence, Townlight Grants remains deterministic and stateless. Retrieval and staff-only endpoints return actionable `503` responses that name the required configuration.

## Local Development

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
bash scripts/verify-release.sh
```

## License

Code: AGPL-3.0-only, with the TownLight Public Institution Exception for qualifying deployments. See [LICENSE](LICENSE) and [LICENSE-EXCEPTION.md](LICENSE-EXCEPTION.md).
Documentation: CC BY 4.0 ([LICENSE-DOCS](LICENSE-DOCS)).
