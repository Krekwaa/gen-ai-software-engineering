# Copilot Instructions — Virtual Card Lifecycle

Use `../../specification.md` as the source of truth and `../../agents.md` as the working protocol. In suggestions and chat responses, name the relevant MO/LLT requirement IDs and preserve their acceptance criteria.

- Keep domain policy independent from transport, storage, and vendor SDKs. Prefer typed contracts and an explicit exhaustive state machine.
- Model money as integer minor units plus ISO 4217 currency; never use `float`/`double` for money.
- Use UTC timestamps and opaque public identifiers. Use an IANA account time zone only for daily/monthly boundaries.
- Never introduce or echo PAN, CVV, PIN, track data, real customer data, tokens, secrets, raw processor payloads, or sensitive fraud reasons. Use synthetic placeholders and allowlisted structured telemetry.
- Enforce ownership/role, purpose, eligibility, policy, state/version, and recent step-up checks on the server. Deny by default and avoid resource-enumeration differences.
- Require idempotency keys for mutations. Bind a key to a canonical payload, make retries deterministic, and represent uncertain remote outcomes as pending reconciliation.
- Verify webhook authentication, freshness, uniqueness, ordering/version, and valid state transition before applying it.
- Keep audit records append-only and atomically durable with accepted mutations through an outbox or equivalent pattern. Notifications are at-least-once and deduplicated.
- Return stable safe error codes, a correlation ID, and retry guidance. Never expose stack traces or vendor errors.
- Bound queries and exports. Use stable cursor pagination; default 25 and maximum 50.
- Generate tests with every change: state/invariant unit tests, boundary/property cases, authorization negatives, duplicate/concurrent/out-of-order flows, dependency failure injection, and contract tests as applicable.
- Do not “fix” failures by weakening validation, authorization, audit, privacy, retention, or tests. Surface requirement conflicts for human decision.
- Flag any proposed dependency, schema/retention change, sensitive-data expansion, or security-boundary change for explicit review.

Before declaring work complete, state which acceptance criteria were checked, what was not run, and any security, privacy, migration, observability, reconciliation, or rollout impact.
