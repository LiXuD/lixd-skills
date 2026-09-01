# Reporting and stable automation

Use this reference when consolidating runtime results or turning proven scenarios into repeatable browser regression.

## 1. Select what to automate

Automate a scenario only when:

- its business invariant and actor are explicit;
- setup and cleanup are deterministic;
- the authentic login path is available;
- selectors reflect stable user-facing behavior or maintained test IDs;
- async effects have bounded waits;
- sensitive evidence can be sanitized;
- a failure cannot be mistaken for a skipped pass.

Keep unstable exploratory paths in the manual ledger. Do not hide them behind retries.

## 2. Automation invariants

- Accept an explicit isolated environment/fixture input and reject ambiguous shared targets.
- Use unique run/scenario IDs and avoid hard-coded mutable database IDs.
- Use the real login UI and normal public routes.
- Keep mock/stub tests in a separately labeled tier.
- Capture sanitized before/after snapshots, network summaries, console output, and final side-effect evidence.
- Fail non-zero on assertion or cleanup failure.
- Preserve a bounded failure snapshot without retaining raw profiles, credentials, or session material.
- Close sessions in a finalizer.
- Make cleanup target validation stricter than setup convenience.

If a security-only change is made after the last passing run, disclose that the exact final version was not fully rerun unless it is rerun.

## 3. Scenario ledger

Use one row per material action:

| ID | Actor | Page/action | Expected | UI | HTTP | Service | Persistence/side effect | Cleanup | Result |
|---|---|---|---|---|---|---|---|---|---|
| S-001 | role | action | invariant | artifact | status/request ID | transition | exact state | cleaned/retained | pass/fail/blocked |

Keep skipped and unverified distinct from passed.

## 4. Known issue record

For every defect or contract gap:

| Field | Content |
|---|---|
| Title | Stable, business-facing description |
| Reproduction | Actor, precondition, exact UI path |
| Expected | Requirement, policy, or confirmed product decision |
| Actual | Visible, HTTP, service, and persisted result |
| Impact | Affected actors, data, security, finance, or operations |
| Evidence | Sanitized artifact and correlation IDs |
| Classification | confirmed / partial / contradicted / unverified |
| Suggested remediation | Smallest valid direction, not an acceptance-time change |
| Retest | Scenario that closes the issue |

List protective failures separately so expected 409/403 behavior is not reported as a defect.

## 5. Final report structure

Keep the report evidence-led:

1. **Scope and environment** — revision, environment, roles, external boundary, run ID.
2. **Acceptance statement** — what is runtime verified and what is not.
3. **Role/menu coverage** — expected versus executed capabilities.
4. **Cross-role journeys** — actor transitions and business invariants.
5. **Positive and negative results** — including async and side effects.
6. **Known issues and contract gaps** — expected/actual/impact/evidence/remediation.
7. **Protective failures** — expected safety behavior.
8. **Automation** — exact command/version, fresh-baseline result, failure behavior.
9. **Evidence security** — scan result, removed artifacts, retention boundary.
10. **Cleanup verification** — isolated state removed, shared state intact.
11. **Unverified boundaries** — production, external, scale, recovery, routes, roles, or notifications not exercised.

Avoid statements such as “all tests passed” when only a subset was executed.

## 6. Completion vocabulary

Use precise states:

- **inventory complete** — roles, menus, capabilities, dependencies, and planned evidence are mapped;
- **runtime verified** — every declared hop and required side effect was observed in the named environment;
- **regression automated** — the stable scenario passed from a fresh isolated baseline using the retained automation;
- **dev closure** — the declared development scope is repeatable;
- **production ready** — use only after production-specific security, capacity, deployment, observability, rollback, and external gates are separately satisfied.

## 7. Final verification checklist

- [ ] The report matches the current revision and actual run.
- [ ] Every pass has sufficient UI/runtime/side-effect evidence.
- [ ] Known defects remain visible and were not silently repaired or excluded.
- [ ] Protective failures are separated from defects.
- [ ] Skipped, blocked, and unverified paths are explicit.
- [ ] Retained evidence contains no known credentials, tokens, keys, private material, or raw browser profiles.
- [ ] Automation syntax and observable behavior were validated proportionally to changes.
- [ ] Cleanup removed only isolated state and shared infrastructure remains healthy.
- [ ] No production, paid, destructive, commit, push, or remediation claim exceeds actual authorization.
