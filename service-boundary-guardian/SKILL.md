---
name: service-boundary-guardian
description: Use when reviewing or changing boundaries between packages, modules, domains, services, plugins, data stores, or asynchronous consumers, especially when coupling, ownership, authorization, cyclic dependencies, event reliability, or shared-code abuse may be involved.
---

# Service Boundary Guardian

Protect architectural boundaries without assuming a particular topology, language, framework, transport, or build tool. A boundary may be in-process or remote; its strength comes from explicit ownership and enforceable contracts.

## Boundary Model

For every cross-boundary interaction, identify:

- owner of the behavior and state;
- caller and permitted dependency direction;
- public contract and compatibility policy;
- identity, authorization, and trust boundary;
- transaction and consistency boundary;
- retry, timeout, idempotency, and recovery behavior;
- observability needed to diagnose failures.

Trace at least one successful and one failed critical flow. Import graphs alone do not prove runtime safety.

## Invariants

- Consumers depend on an owner's public contract, not its private implementation or persistence model.
- One owner controls mutations to each business invariant and authoritative data set.
- Cross-boundary messages expose stable facts, not internal storage objects.
- Identity and permissions are established at every trust boundary; “internal” is not an authentication strategy.
- Asynchronous delivery defines commit/publication ordering, retries, deduplication, replay, failure quarantine, and operator recovery.
- Shared code remains domain-neutral; owner-specific rules stay with the owner.
- Failure behavior is explicit. Security, consistency, and configuration failures do not become permissive defaults.

Apply these invariants according to the architecture actually present. A modular monolith may enforce package APIs and exclusive repository ownership; distributed services may additionally require network authentication, schema versioning, and transport failure handling.

## Review Method

1. Read the project's own architecture and contribution rules.
2. Build an ownership map for behavior, data, public interfaces, and events.
3. Inspect dependency and execution flows with the project's available tools.
4. Find cycles, private imports, cross-owner persistence access, duplicated rules, trusted caller claims, and event loss or duplication windows.
5. Verify findings with focused architecture, authorization, failure-injection, and idempotency tests where feasible.
6. Assess impact before editing, using repository-mandated analysis when present.
7. After remediation, rerun the relevant boundary checks and compare the actual change scope with the intended one.

## Findings Contract

Describe each issue as:

`caller → crossed boundary → owner or policy violated → failure mode → evidence → smallest repair`

Separate demonstrated correctness, security, or financial impact from maintainability risk. Preserve project-specific conventions in the project's instruction files rather than embedding them in this skill.
