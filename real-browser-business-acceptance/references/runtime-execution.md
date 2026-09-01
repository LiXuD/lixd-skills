# Runtime browser execution

Use this reference after the inventory boundary is agreed and runtime actions are authorized.

## 1. Prepare an isolated runtime

Prefer a project-provided fixture or environment lifecycle over ad hoc data creation.

Record and verify:

- unique run label and test-data namespace;
- database/schema/tenant isolation;
- migrations applied through the real mechanism;
- test users and roles without exposing credentials;
- required dependencies and services;
- public browser URL and normal gateway/edge route;
- exact cleanup target and guard conditions.

Inspect existing processes, ports, containers, databases, and other executors before starting. Do not take ownership of an ambiguous shared runtime.

Production, shared business databases, paid providers, real customer identities, bulk actions, and irreversible workflows require explicit authority and a recoverable plan.

## 2. Prove readiness

Do not treat a started process as ready. Verify the signals the architecture actually requires:

- infrastructure health;
- service health/readiness;
- discovery/registration or load-balancer visibility;
- migration state;
- frontend reachability;
- public gateway routing;
- one unauthenticated negative probe;
- baseline counts or states for the effects that later scenarios will assert.

If routing or registration is stale, repair only runtime ownership issues already in scope. Do not classify transport failure as business failure.

## 3. Start with the minimum vertical slice

1. Open a clean named browser session.
2. Navigate to the real login entry.
3. Enter the test identity through the supported interactive flow.
4. Observe the real authentication and current-identity requests.
5. Confirm the actor, roles, permissions, landing route, and expected menu.
6. Open one low-risk page through normal navigation.
7. Correlate the UI with public requests and server/persistence state.

Passing this slice proves only that slice. It is a gate for expansion, not complete acceptance.

## 4. Execute one action as one proof packet

For each action, record:

- scenario/run ID and actor;
- precondition and baseline state;
- page/route and control used;
- user input category, with secrets redacted;
- public request method/route and response outcome;
- correlation or request ID when available;
- owning service and decisive downstream result;
- exact persisted state and mandatory side effects;
- visible postcondition;
- cleanup state.

Capture a UI snapshot immediately before and after material interactions when practical. Save console errors and sanitized network summaries. A response body parsed incorrectly by the frontend is a failure even when the backend response is correct.

## 5. Cover menu capabilities in dependency order

For each confirmed role and page:

- visible and hidden menu expectations;
- direct route guard behavior;
- list/query and empty/loading/error states;
- create/edit/delete where applicable;
- enable/disable and domain actions;
- validation and contract parsing;
- permissions at both UI and service boundary;
- audit and other required effects.

Hidden buttons or routes do not prove backend authorization. Where authorization is material, test the normal public API through the gateway using the actor's real session, without calling an internal service directly.

## 6. Execute cross-role journeys

Use separate sessions and identities. A typical pattern is:

```text
actor A creates/submits
  → actor B reviews/approves/rejects
  → actor C consumes or operates the result
  → actor D revokes/audits/reconciles
```

After role, permission, or status changes, follow the product's real refresh/re-login behavior. Verify state in both the actor-facing UI and the owning data/audit stores.

## 7. Material negative paths

Choose negatives based on the business invariant:

- invalid or expired credentials;
- actor sees or reaches something they should not;
- missing required input or invalid enum/shape;
- rejected or revoked permission;
- duplicate/idempotent action;
- dependency failure, timeout, fallback, or circuit behavior;
- rate/quota limit;
- invalid downstream response or contract;
- publish/disable/delete while active references exist.

Distinguish a protective failure from a defect. A 409 that preserves an active binding may be the expected safety behavior; a 500 for a valid publish path is not.

## 8. Handle asynchronous effects

Establish the baseline before the action and poll for a bounded duration. Assert exact correlation, state, amount, actor, or version—not merely that a row exists.

On timeout, preserve the last observed state and relevant logs. Do not keep waiting silently or reinterpret absence as success.

## 9. Evidence safety

- Never copy credential/state files into evidence.
- Redact passwords, cookies, bearer/session tokens, API keys, secrets, private keys, personal data, and signed payloads.
- Raw browser profiles and traces often contain login request bodies and authorization material. Do not retain them in the repository by default.
- If raw trace is explicitly required, store it outside the repository with restrictive permissions, document retention, and remove it after sanitized extraction.
- Scan retained evidence using both exact known test-secret values and pattern searches. Search hidden files and compressed/container formats where applicable.
- Retain sanitized snapshots, response shapes, IDs, counts, amounts, status transitions, and logs sufficient to reproduce the conclusion.

## 10. Failure and cleanup

When an action fails:

1. capture the visible state, request outcome, console, owning-service state, and persistence state;
2. classify environment/tool failure separately from product behavior;
3. record the defect without fixing it;
4. continue only when the next scenario is safe and the failed state is understood.

At the end:

- close browser sessions;
- remove or deactivate isolated users, keys, objects, messages, and databases through authorized project mechanisms;
- stop only processes owned by the run;
- verify ports/processes are stopped;
- verify isolated state is absent;
- verify shared databases, containers, and services remain intact;
- report any intentionally retained state or evidence.
