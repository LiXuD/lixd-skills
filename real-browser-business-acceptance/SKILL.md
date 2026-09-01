---
name: real-browser-business-acceptance
description: Plan, execute, and automate evidence-first acceptance of a business system through a real browser and its real application chain, including roles and menus, interactive login, UI actions, contracts, gateway and service traffic, persisted side effects, cross-role workflows, negative paths, evidence sanitization, and isolated cleanup. Use when browser-level business acceptance is required beyond unit, API-only, or backend-only testing.
metadata:
  short-description: Prove real browser business flows end to end
---

# Real Browser Business Acceptance

Prove the declared business capability as a user experiences it:

```text
actor → browser UI → public entry point → authentication/authorization
      → owning services → downstream/async work → persisted business state
      → audit, billing, notifications, and observability where applicable
```

A page rendering, an HTTP 200, a backend test, or a database row alone is not a full-chain pass.

## Select the working mode

- For repository discovery, role/menu inventory, capability mapping, or execution planning, read [references/inventory-and-plan.md](references/inventory-and-plan.md).
- For starting an environment and performing real browser acceptance, read [references/runtime-execution.md](references/runtime-execution.md).
- For turning stable scenarios into regression automation or producing the final report, read [references/report-and-automation.md](references/report-and-automation.md).
- When the request spans all modes, perform them in that order and retain the phase gates.

## Core invariants

1. **Separate expected behavior from current behavior.** Build the expected role/menu/capability inventory from product requirements, policy, or explicit user confirmation. Current menus, routes, permissions, seeds, and migrations are candidate evidence, not the expectation by themselves.
2. **Use authentic interactive identity.** Log in through the supported UI and real identity/session path. Do not inject tokens, storage state, cookies, or mocked identity unless the user explicitly requests a separate synthetic tier. For SSO, MFA, passkeys, or device approval, use the real supported flow or mark it blocked.
3. **Exercise the real public chain.** Browser actions must use the normal frontend, gateway or edge, services, integrations, and persistence. Do not bypass the gateway by calling an internal service merely because it is easier.
4. **Corroborate discovery.** Code graphs, wikis, generated route maps, and documentation accelerate candidate discovery. Confirm material conclusions in current source, configuration, migrations, runtime traffic, and owned persistence.
5. **Keep defects in scope.** Record known defects and contract mismatches; do not repair them during acceptance or skip their paths unless the user separately authorizes remediation. A safe failure is evidence, not permission to change business code.
6. **Do not force generic CRUD.** Test list/query/create/update/delete and domain actions only where the product exposes or requires them. Missing edit/delete/approve/revoke/export behavior is either not applicable or a product gap; determine which instead of inventing an action.
7. **Isolate state and actors.** Use unique test data, separate role sessions, bounded external effects, and a cleanup plan. A combined admin-plus-approver account does not prove role separation.
8. **Treat asynchronous state explicitly.** Use bounded polling for messages, workflows, call records, billing, search indexes, notifications, and other eventually consistent effects. Never turn an unbounded wait into a pass.
9. **Preserve authorization boundaries.** Inventory is read-only. Runtime writes, destructive cleanup, paid external calls, production access, bulk operations, and remediation each require authority appropriate to their impact.
10. **Protect evidence.** Browser traces, profiles, request bodies, exports, screenshots, and fixture state can contain passwords, cookies, API keys, personal data, or private keys. Prefer sanitized snapshots and request metadata. Do not retain raw profiles or traces in the repository unless explicitly required and safely handled.

## Acceptance layers

### Menu-level vertical slices

For every confirmed role and expected page:

- verify authentic login, identity refresh, landing route, and visible menu;
- open the page through normal navigation;
- execute each applicable action through the UI;
- verify loading, success, empty, validation, and material error states;
- correlate the frontend request and response with backend behavior;
- verify parsed content and the resulting business state;
- verify audit or other mandatory side effects;
- clean or intentionally retain the isolated object.

### Cross-role business journeys

Connect already-proven page capabilities into realistic actor transitions. A journey normally includes prerequisites, actor changes, a decisive business action, downstream use of its result, negative or revocation behavior, and final state reconciliation.

Use separate sessions for distinct actors. Re-authenticate after permission or status changes when the real product requires session refresh.

### Stable regression automation

Automate only scenarios whose data setup, business semantics, selectors, waits, assertions, and cleanup are understood. Keep exploratory or unstable paths in the manual evidence ledger until their behavior is resolved.

## Evidence model

Each claimed action should have the applicable parts of one proof packet:

| Layer | Minimum useful proof |
|---|---|
| UI | actor, route, control used, visible result, snapshot or sanitized screenshot |
| HTTP | public request, response status/business code, relevant redacted shape, correlation ID |
| Service | owning component, decisive log/state transition, downstream outcome |
| Persistence and side effects | exact business row/state, audit, billing, message, notification, or metric |

Classify conclusions as `confirmed`, `partially confirmed`, `contradicted`, or `unverified`. Use `runtime verified` only when every required hop and side effect inside the declared scope was observed.

## Phase flow

1. Establish repository, worktree, environment, and authority boundaries.
2. Inventory roles, expected menus, capabilities, contracts, object dependencies, and known issues.
3. Confirm any unresolved product choices that materially change actors, actions, test data, or external effects.
4. Prepare and prove an isolated runtime, including health and service discovery where used.
5. Pass the smallest vertical slice: authentic login, current identity/menu, and one low-risk page.
6. Expand through menu capabilities in dependency order.
7. Execute cross-role journeys and material negative paths.
8. Automate the stable subset and rerun it on a fresh isolated baseline.
9. Produce the report, sanitize evidence, close sessions, clean isolated state, and verify shared state remains intact.

## Stop conditions

Stop and report the exact boundary when:

- the target cannot be isolated or safely cleaned;
- required credentials, roles, product expectations, or external authority are missing;
- another executor owns the same mutable runtime;
- a production, paid, destructive, or broad operation was not authorized;
- runtime health or routing is uncertain enough that a business conclusion would be false;
- evidence contains secrets that cannot be safely sanitized.

Do not label a blocked, skipped, mocked, historical, or inferred path as passed.

## Required deliverables

Keep the deliverables proportional to scope, but for a broad acceptance program normally produce:

- an inventory and execution plan;
- a scenario/evidence ledger;
- a final result report with known issues separated from protective failures;
- an automation entry point for the stable subset;
- a sensitive-evidence scan result;
- a cleanup verification record;
- explicit unverified and production-only boundaries.
