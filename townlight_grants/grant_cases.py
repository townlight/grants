"""townlight_grants.grant_cases lifecycle: schema, manifest, verification."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from typing import Any, Mapping

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    MetaData,
    String,
    Table,
    Text,
    UUID,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema

SCHEMA = "townlight_grants"
STAGES = ("draft", "reviewed", "awarded", "closed")

metadata = MetaData(schema=SCHEMA)

grants_cases = Table(
    "grant_cases",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("assigned_to", UUID(as_uuid=True), nullable=True),
    Column("last_actor", UUID(as_uuid=True), nullable=False),
    Column("budget_revision_id", UUID(as_uuid=True), nullable=True),
    Column("contract_id", UUID(as_uuid=True), nullable=True),
    Column("records_request_id", UUID(as_uuid=True), nullable=True),
    Column("title", String(255), nullable=False),
    Column("funding_area", String(128), nullable=True),
    Column("deadline", Date, nullable=True),
    Column("workpapers", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("stage", String(16), nullable=False,
           server_default=text("'draft'"), default="draft"),
    Column("created_at", DateTime(timezone=True), nullable=False,
           server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False,
           server_default=func.now(), onupdate=func.now()),
    Column("award_reference", String(128), nullable=True),
    Column("award_amount_cents", BigInteger, nullable=True),
    Column("report_due", Date, nullable=True),
    Column("report_completed_at", DateTime(timezone=True), nullable=True),
    Column("archived_manifest", Text, nullable=True),
    Column("archived_sha256", String(64), nullable=True),
    CheckConstraint(
        "stage IN ('draft','reviewed','awarded','closed')",
        name="grant_cases_stage_check",
    ),
)


def ensure_grants_schema(engine: Engine) -> None:
    """Create schema townlight_grants and grant_cases in a single transaction.

    Schema creation and table creation share one connection, so a partial
    provision (schema without table, or vice versa) cannot be committed.
    """
    with engine.begin() as conn:
        conn.execute(CreateSchema(SCHEMA, if_not_exists=True))
        metadata.create_all(bind=conn, checkfirst=True)


def _as_mapping(row: Any) -> Mapping[str, Any]:
    if hasattr(row, "_mapping"):
        return row._mapping
    return row


def _canonical(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {k: _canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def build_archive(row: Any, linked_evidence: Mapping[str, Any]) -> tuple[bytes, str]:
    """Return (canonical UTF-8 JSON bytes, sha256 hex) for a closeout row.

    The manifest carries summary identities: link UUIDs plus a SHA-256
    digest of the durable workpapers log. The workpapers themselves are
    stored by the runtime in grant_cases.workpapers (each entry stamped
    with actor/time), so the archive references them by digest rather
    than duplicating the full body.

    linked_evidence must be the caller's actual verified link data; the
    function never infers or fabricates linked identifiers.
    """
    if not isinstance(linked_evidence, Mapping):
        raise TypeError("linked_evidence must be an actual evidence mapping")
    r = _as_mapping(row)
    workpapers_sha256 = hashlib.sha256(
        _canonical_bytes(r.get("workpapers") or {})
    ).hexdigest()
    payload = {
        "schema": f"{SCHEMA}.grant_cases.closeout.v1",
        "id": _canonical(r["id"]),
        "stage": r["stage"],
        "title": r["title"],
        "funding_area": r.get("funding_area"),
        "assigned_to": _canonical(r.get("assigned_to")),
        "last_actor": _canonical(r["last_actor"]),
        "budget_revision_id": _canonical(r.get("budget_revision_id")),
        "contract_id": _canonical(r.get("contract_id")),
        "records_request_id": _canonical(r.get("records_request_id")),
        "deadline": _canonical(r.get("deadline")),
        "award_reference": r.get("award_reference"),
        "award_amount_cents": r.get("award_amount_cents"),
        "report_due": _canonical(r.get("report_due")),
        "report_completed_at": _canonical(r.get("report_completed_at")),
        "created_at": _canonical(r.get("created_at")),
        "updated_at": _canonical(r.get("updated_at")),
        "workpapers_sha256": workpapers_sha256,
        "linked_evidence": _canonical(linked_evidence),
    }
    raw = _canonical_bytes(payload)
    return raw, hashlib.sha256(raw).hexdigest()


def verified_archive(row: Any) -> bytes:
    """Return the stored manifest bytes only if they match archived_sha256."""
    r = _as_mapping(row)
    manifest = r.get("archived_manifest")
    digest = r.get("archived_sha256")
    if not isinstance(manifest, str) or not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("grant_cases row has no verified archive")
    raw = manifest.encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("grant_cases archived manifest digest mismatch")
    return raw


__all__ = [
    "grants_cases",
    "ensure_grants_schema",
    "build_archive",
    "verified_archive",
]