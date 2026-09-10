---
name: database-evolution-safety
description: Use when changing, migrating, backfilling, cleaning, or recovering persistent data or its structure, especially when existing data, mixed application versions, online traffic, retries, tenant isolation, destructive operations, or rollback constraints create risk.
---

# Database Evolution Safety

Make persistent-data evolution reproducible, observable, compatible, and recoverable across relational, document, key-value, graph, and managed data systems.

## Establish the Migration Model

1. Identify the authoritative change mechanism, history, checkpoints, deployment coupling, and recovery capabilities.
2. Inspect real stored data and metadata separately from model definitions or migration files.
3. Classify each environment or tenant as fresh, current, legacy, partially migrated, or drifted.
4. Inventory readers, writers, indexes, validators, queries, exports, and downstream consumers affected by the change.
5. Confirm whether a published change may already have run. Preserve immutable history unless every affected environment will be recreated intentionally.

## Design the Change

- Prefer expand–migrate–contract: add compatible structure, migrate data, switch readers and writers, then clean up after the rollback window.
- Keep structure changes, backfill, validation, indexing, and destructive cleanup independently observable and safely ordered.
- Make batches resumable and idempotent with checkpoints. Do not assume a migration ledger makes a large online backfill atomic.
- Support mixed application versions explicitly through compatible reads/writes, canaries, or coordinated downtime.
- Validate existing data before tightening constraints or validators.
- Protect concurrent writes and define conflict handling, throttling, stop conditions, and tenant isolation.
- Define rollback when old data remains usable; otherwise define tested forward recovery and backup restoration.
- Align models, queries, indexes, validators, bootstrap paths, tests, and operational documentation.

Use project-required impact analysis before editing. Treat data consumers and operational jobs as affected even when dependency tools cannot see them.

## Legacy State Adoption

For a store or tenant that predates reliable change tracking:

1. create a verified backup;
2. inspect schema and data invariants;
3. classify which historical changes and data variants are already present;
4. reconcile missing non-destructive changes with resumable, idempotent operations;
5. validate the final schema;
6. record the baseline only after successful reconciliation;
7. prevent unsafe rollback past the adopted baseline.

Never mark work complete merely to silence the change mechanism.

## Regression Matrix

Use isolated data or bounded canary tenants and verify:

- validation and dry-run;
- fresh initialization when supported;
- upgrade from the supported previous state;
- repeated execution with no duplicate effects;
- failure atomicity;
- rollback and re-apply, or forward recovery;
- backup and restore;
- legacy adoption and mixed-version operation when supported;
- concurrent-write behavior and resumability;
- model/query/index/validator compatibility;
- critical data invariants per environment or tenant.

Protect destructive tools so they can target only explicitly selected environments, tenants, collections, tables, or key ranges.

## Report

Separate implementation from actual stored-data state. Report backups, checkpoints, versions or phases, validation counts, conflicts, rollback limits, and the exact next action. Never say “migration fixed” when only an empty store or model definition was tested.
