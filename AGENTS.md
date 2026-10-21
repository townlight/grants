<a id="civicgrants-agent-contract"></a>

# Townlight Grants Agent Contract

## Source of Truth

- Upstream suite spec: `townlight/townlight/docs/CivicSuiteUnifiedSpec.md`, especially the Townlight Grants catalog entry and suite-wide non-negotiables.
- Townlight Grants supports opportunity triage, eligibility-factor matching, application outline support, compliance-calendar scaffolding, and audit-ready grant files.
- Staff own every decision.

## Hard Boundaries

- Townlight Grants never determines official eligibility, submits applications, provides legal advice, or updates a grant system of record.
- Townlight Grants v0.2.0 must not call live LLMs or live funder feeds.
- Application outlines and eligibility matches must be marked review-required.
- Townlight Grants depends on Townlight Core; Townlight Core must never depend on Townlight Grants.
- Townlight Grants may reference Townlight Records concepts only through released contracts, context IDs, or deterministic sample data in this recovery release.

## Verification

Run `bash scripts/verify-release.sh` before every push or release.
