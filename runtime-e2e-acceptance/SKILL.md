---
name: runtime-e2e-acceptance
description: Use when a team must prove that a critical process works end to end in its real operating environment, especially when artifact reviews, simulations, unit checks, or individual workstream results cannot establish the final outcome and side effects.
---

# Runtime E2E Acceptance

Treat “runtime” as the project's real operating context: a deployed system, business operation, physical workflow, event, campaign, or service delivery. Acceptance is evidence collection, not a ceremonial walkthrough.

## Define the Proof

Map the critical path before starting anything:

```text
trigger → eligibility and authority → execution → handoffs
        → final outcome → downstream effects → reconciliation and closure
```

For each hop, define observable proof: a signed record, physical state, system event, financial entry, measurement, decision, notification, or accountable confirmation.

## Prepare a Controlled Run

1. Read the project's operating, safety, privacy, and acceptance rules.
2. Inspect the current environment, dependencies, owners, schedules, and existing state.
3. Choose representative cases with unique identifiers and bounded operational, financial, or customer exposure.
4. Confirm prerequisites and readiness at every required workstream.
5. Define stop conditions, rollback or containment, cleanup, and evidence retention before execution.
6. Obtain explicit authorization for effects on real customers, production systems, money, inventory, or other consequential state.

When the real environment is too risky, use the highest-fidelity safe environment and state exactly what remains unproven.

## Exercise the Flow

1. Execute through the same entry point and responsibilities used in normal operation.
2. Observe every handoff and record actor, time, state, decision, and next owner.
3. Verify the final outcome and reconcile all consequential effects rather than checking only that a step occurred.
4. Exercise material exceptions such as ineligible input, missing approval, duplicate submission, dependency failure, delay, partial completion, and recovery.
5. Confirm exception ownership, escalation, communication, compensation, and closure.
6. Repeat affected paths after material fixes.

## Evidence Integrity

- Label document review, simulation, rehearsal, pilot, and live operation separately.
- Treat skipped steps and unobserved downstream effects as unverified.
- Verify exact values and state transitions, not merely artifact or record existence.
- Do not infer authorization, adoption, delivery, or reconciliation from an upstream success signal.
- Record environment-specific blockers and substitutions precisely.

## Cleanup

Restore, remove, reverse, or formally close controlled test state when safe and authorized. Preserve the evidence required for audit and follow-up. Report anything intentionally left active or unresolved.

## Acceptance Report

State:

- the exact flow, cases, and environment;
- positive and negative cases executed;
- outcome and downstream-effect evidence;
- simulations or component checks run in addition to the controlled run;
- unverified real-world conditions;
- cleanup status.

Use “end-to-end verified” only when the whole declared path and its required effects were observed and reconciled.
