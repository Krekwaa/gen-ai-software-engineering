# AI Agent Guidelines — Virtual Card Project

These rules govern any AI coding or review agent working from `specification.md`. The specification is authoritative. When requirements conflict or remain ambiguous, stop, identify the affected requirement IDs, and request a decision; do not invent financial policy.

## Working protocol

1. Read `specification.md` and the applicable editor rules before proposing changes.
2. State which MO and LLT IDs the work serves and keep the change inside that slice.
3. Inspect existing contracts and tests before editing. Preserve backward compatibility unless an approved migration says otherwise.
4. Make the smallest coherent change, update traceability and documentation, then verify at the appropriate layers.
5. Report assumptions, commands/checks run, evidence, and remaining risks. Never claim a check passed if it was not run.

## Assumed implementation stack

If a future team has not selected a stack, assume Python 3.12, FastAPI, Pydantic v2, PostgreSQL, an asynchronous job/event worker, OpenTelemetry, pytest, and OpenAPI. These are planning assumptions, not requirements of this documentation-only homework. Follow the repository's actual stack when one exists.

## Non-negotiable domain rules

- Represent money as integer minor units and ISO 4217 currency. Never use binary floating point.
- Treat processor tokens as opaque. Never request, store, generate, log, or test with real PAN, CVV, PIN, magnetic-stripe data, access tokens, or secrets.
- Use opaque public IDs. Do not encode customer data or expose sequential database keys.
- Enforce authentication, ownership/role, purpose, policy, and current-state checks server-side. UI restrictions are not authorization.
- Mutating workflows must be idempotent, version-aware, auditable, and safe under timeout or replay.
- Unknown processor outcomes remain pending until reconciled. Never infer success or blindly retry a potentially completed issuance/replacement.
- Policy holds override customer controls. Do not reveal fraud rules or another customer's resource existence.
- Audit records are append-only. Correct with a linked event, never an update/delete.
- Notifications and telemetry contain only non-sensitive references and safe reason codes.

## Architecture and coding conventions

- Separate domain policy, application orchestration, adapters, and transport concerns. Domain logic must not depend on HTTP or a processor SDK.
- Define typed, versioned contracts at boundaries. Validate all external input and distrust webhook order, uniqueness, and authenticity.
- Prefer explicit state machines and exhaustive matches over scattered boolean flags.
- Use UTC for persistence and events; use the account's IANA time zone only for product period boundaries and display.
- Use stable machine-readable error codes and safe messages. Do not pass dependency messages or stack traces to callers.
- Use structured logs with correlation IDs and allowlisted fields. Do not place customer/card IDs in metric labels.
- Add comments for policy rationale or non-obvious invariants, not narration of straightforward code.
- Do not add a dependency, weaken validation, change retention, or expand data collection without recording rationale and review impact.

## Edge-case behavior

For every mutation, consider duplicate delivery, conflicting idempotency payload, concurrent commands, stale version, dependency timeout before/after remote acceptance, partial persistence, and replay. For every read, consider empty state, stale data, pagination under inserts, authorization enumeration, excessive scope, and dependency lag. Important edge cases must become executable tests and, where operationally relevant, alerts or reconciliation checks.

Fail closed for authorization, step-up authentication, audit durability, webhook verification, and policy decisions. Degrade safely for optional notification delivery and read-only freshness, clearly showing last-confirmed state and timestamp.

## Testing and verification

- Map tests to MO/LLT IDs or named acceptance criteria.
- Use unit/property tests for money, invariants, and all state-command pairs.
- Use integration/contract tests for persistence, idempotency, processor, identity, transaction feed, audit, and notifications.
- Include concurrency, duplicate/out-of-order event, timeout, retry, and failure-injection tests.
- Include object-level authorization, role matrix, enumeration, injection, webhook forgery/replay, and sensitive-data leakage tests.
- Verify pagination stability, reconciliation totals, retention behavior, audit integrity, and recovery.
- Measure p95/p99 targets and assumed burst capacity in a production-like environment; do not substitute a single local timing.
- Use synthetic fixtures only, including 0/2/3-decimal currencies, daylight-saving boundaries, every card state, similar last-four values, and long histories.
- Scan logs, traces, metrics, events, errors, snapshots, and fixtures for prohibited data.

No agent may delete or relax a failing test simply to make a build pass. Update tests only when an approved requirement or contract changes, and explain the change.

## Security and compliance review triggers

Request explicit security/privacy/compliance review for changes to authentication or authorization, card-data boundaries, audit schema, encryption/key use, retention/deletion, staff search/export, processor/webhook trust, fraud/policy decisions, or externally observable error semantics. Treat PCI DSS and privacy statements as scope assumptions requiring qualified human validation, not as compliance claims.

## Completion report

An agent handoff must list: changed artifacts; MO/LLT coverage; acceptance criteria satisfied; verification run and results; privacy/security impact; migrations or rollout needs; and unresolved assumptions. If blocked, provide evidence and the smallest decision needed to continue.
