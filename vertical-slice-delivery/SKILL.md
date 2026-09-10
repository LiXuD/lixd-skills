---
name: vertical-slice-delivery
description: Use when an outcome crosses several workstreams or handoffs, when partial delivery would be unusable, or when a team needs a small end-to-end result that can be reviewed, piloted, measured, and expanded safely.
---

# Vertical Slice Delivery

Deliver the smallest complete outcome that a real user, operator, or stakeholder can exercise and evaluate. “Small” reduces risk; “complete” prevents disconnected partial work.

## Define the Slice

Before changing artifacts or systems, write an acceptance matrix containing:

- target user or beneficiary;
- concrete start and end state;
- included workstreams and accountable owners;
- decisions, inputs, and handoffs;
- visible or measurable outcome;
- exceptions and failure cases;
- evidence required for acceptance;
- rollback, support, or follow-up needs.

Choose a representative slice that reaches the outcome through every necessary workstream. A software slice may cross interface, data, service, client, and operations; a business slice may cross policy, process, training, communications, and measurement.

## Deliver in Dependency Order

1. Read the project's governing constraints, current state, and user intent.
2. Map dependencies and resolve upstream decisions before producing downstream artifacts.
3. Establish one source of truth for terms, rules, ownership, and acceptance criteria.
4. Produce the minimum artifacts and changes required across all included workstreams.
5. Exercise the whole slice with a representative case and material exceptions.
6. Capture observed outcomes, defects, delays, and support needs.
7. Fix material gaps and repeat the affected path.
8. Update operational guidance, ownership, and status records.
9. Compare the delivered scope and side effects with the acceptance matrix before expanding rollout.

## Design Rules

- Reuse established project capabilities and conventions before creating parallel mechanisms.
- Give each decision, artifact, and handoff one accountable owner.
- Keep terminology and rules consistent across workstreams.
- Protect sensitive information and apply the project's authorization requirements.
- Make retries, repeated submissions, and partial failure safe when the workflow permits them.
- Preserve user choices and avoid compatibility work that the outcome does not require.
- Keep state-changing actions within the user's authorization.

## Verification Ladder

Build evidence from narrow checks to whole-outcome proof:

1. validate individual artifacts and decisions;
2. verify handoffs between workstreams;
3. rehearse the end-to-end path with a representative case;
4. exercise important exceptions and recovery;
5. pilot or run in the real operating context when required.

Do not call the slice complete because every team produced an artifact. Completion requires the intended outcome and its necessary handoffs to work together.

## Handoff

Report the delivered outcome, included workstreams, observed evidence, unresolved risks, accountable owners, and next expansion decision. Distinguish designed, produced, rehearsed, piloted, and operationally proven states.
