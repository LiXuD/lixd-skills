---
name: evidence-first-project-audit
description: Use when a project claim, readiness statement, completion report, suspected problem, proposed change, or review finding must be checked against current evidence before deciding whether it is true or what to do next.
---

# Evidence-First Project Audit

Build conclusions from current, direct evidence—not from confident wording, stale summaries, or the absence of an obvious contradiction.

## Workflow

1. Define the decision being audited and the consequence of a false positive or false negative.
2. Translate the headline claim into discrete, falsifiable criteria.
3. Identify the authoritative source and direct proof for each criterion. Depending on the project, evidence may include approved plans, signed agreements, delivered artifacts, source code, tests, financial records, observed rehearsals, system state, or accountable confirmations.
4. Establish scope, version, date, owner, and comparison baseline so evidence from different periods or workstreams is not mixed.
5. Triangulate summaries against primary artifacts and observed outcomes. Inspect end-to-end flows when a result depends on several handoffs.
6. Classify every criterion as:
   - confirmed;
   - partially confirmed;
   - contradicted;
   - unverified because evidence is missing.
7. Assess impact, dependencies, owners, and reversibility before recommending action. Use the project's required analysis tools when they exist.
8. Report only decision-relevant findings. When reviewing a change, distinguish introduced issues from pre-existing conditions; when judging readiness, include every condition that can block the outcome.

## Evidence Rules

- Prefer current primary evidence over plans, recollections, and historical status reports.
- Match proof to the claim: preparation does not prove execution; existence does not prove usability; a narrow check does not prove broad readiness.
- Treat skipped, draft, assumed, expired, inaccessible, or unverifiable evidence as unverified.
- Treat absence as evidence only after confirming the correct scope, source, and search method.
- Keep the audit read-only unless the user explicitly requests remediation or another state-changing action.
- Preserve source evidence and disclose conflicts, limitations, and uncertainty.

## Output

Lead with the conclusion and confidence. For each finding include:

- severity based on the decision's real impact;
- exact evidence with artifact, date, owner, or observable location;
- why the behavior matters;
- the smallest valid remediation;
- the validation needed to close it.

When the claim is inaccurate, provide a corrected formulation with the proven scope. End with confirmed facts, unresolved evidence, blockers, and the next decision—not a generic checklist.

## Completion Gate

Finish only after every material criterion has direct evidence or is explicitly marked unverified. Never turn “not disproven” into “confirmed.”
