# Inventory and execution planning

Use this reference before broad browser execution. The outcome is a reviewable business map and an agreed execution order, not a claim that the system works.

## 1. Establish the baseline

Record:

- repository and current revision;
- worktree state and user-owned changes;
- applicable repository rules and authoritative documents;
- target environment and what may be read, started, written, or cleaned;
- whether the task is inventory-only, runtime acceptance, or both.

Preserve unrelated work. Historical reports are context, not fresh evidence for the current revision.

## 2. Discover candidate behavior

Inspect the smallest useful set of current artifacts:

- frontend routes, navigation, route guards, API clients, state/session handling, and action controls;
- backend public routes, authorization checks, gateway/edge routing, owning services, and internal boundaries;
- schemas, migrations, seeds, workflow definitions, queues/events, audit, billing, and observability;
- start, migration, fixture, test, and cleanup instructions.

Code graphs and generated wikis are useful for repository topology, candidate execution flows, and impact discovery. They are not authoritative for dynamic routes, annotations, reflection, workflow engines, runtime permissions, or response shapes. Corroborate material findings.

## 3. Maintain separate expectation and implementation views

Do not infer expected menus from whatever the current account happens to display.

### Role and menu matrix

| Role/actor | Expected menus/pages | Expected capabilities | Source of expectation | Current candidate behavior | Status |
|---|---|---|---|---|---|
| actor | product-approved list | view/create/... | requirement/policy/user | source/runtime candidate | confirmed/partial/contradicted/unverified |

If the product expectation is missing, continue candidate discovery but pause before broad mutable execution when the choice would materially change coverage.

### Menu capability matrix

| Page/domain | Applicable actions | Preconditions | Request/owner | Required side effects | Cleanup | Open questions |
|---|---|---|---|---|---|---|
| page | list/query/create/... | object/role | public route/service | row/audit/event/... | supported action | unresolved semantics |

Include domain actions such as approve, reject, claim, revoke, publish, rollback, export, reconcile, retry, test, or disable. Do not force CRUD where it is not meaningful.

### Contract map

For each material action, map:

```text
UI field/state
  → frontend request and response assumptions
  → gateway/public route
  → backend request/response contract
  → database/event/external effect
```

Record enum drift, missing required fields, envelope mismatches, status-code/business-code differences, and async timing assumptions as candidates for runtime verification.

## 4. Build the object dependency order

List the minimum prerequisites and ownership for each business object. Order menu tests so later steps can reuse earlier isolated data without hiding dependencies.

Example shape:

```text
tenant/account
  → user and role
  → business resource/configuration
  → credential or permission
  → transaction/use
  → records, billing, audit, notification
```

The names vary by product; the dependency logic does not.

## 5. Select golden journeys

Prefer a small set of journeys that collectively cover:

- creation and later use of a business object;
- at least two genuinely separate actors or roles;
- approval or state transition where the domain has one;
- a real downstream request or transaction;
- financial, audit, notification, or other mandatory side effects;
- revocation, rejection, invalid input, or unauthorized use;
- cleanup or terminal reconciliation.

A journey should state its business invariant, not just a click sequence.

## 6. Record known issues without changing them

For every candidate defect or contract mismatch, record:

- reproduction path;
- expected behavior and its source;
- current or suspected behavior;
- likely impact;
- evidence already available;
- runtime test still required;
- remediation suggestion, clearly deferred.

Known issues remain in the execution scope unless running them would be unsafe.

## 7. Define the phase gate

Before broad mutable execution, make the following explicit:

- approved roles and expected menus;
- allowed actions and high-side-effect exclusions;
- test-data creation and cleanup policy;
- environment and external-call boundary;
- evidence location and retention policy;
- first low-risk vertical slice;
- stop points for newly discovered safety or product choices.

The plan is ready when each planned pass has an actor, action, observable result, evidence source, and cleanup strategy.
