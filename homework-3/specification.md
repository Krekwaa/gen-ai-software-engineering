# Virtual Card Lifecycle Management Specification

> This document is an implementation-ready product specification. It defines intent, policy, system boundaries, executable work slices, and verification expectations; it does not include implementation.

## 1. High-Level Objective

Enable eligible customers to safely create and control virtual payment cards while giving authorized operations and compliance staff a complete, privacy-preserving audit view; card authorization processing and storage of raw card credentials remain outside this feature.

## 2. Scope

### In scope

- Customer creation of a virtual card for an eligible funding account.
- Card status viewing, freeze, unfreeze, and replacement.
- Per-transaction, daily, and monthly spending limits.
- Paginated transaction history with pending, reversed, declined, and settled states.
- An internal operations/compliance search and audit view.
- Notifications for security-sensitive lifecycle changes.
- Explicit contracts for a card processor, identity/eligibility service, notification service, audit store, and transaction feed.

### Out of scope

- Physical cards, cash withdrawal, peer-to-peer transfer, disputes, chargebacks, rewards, foreign-exchange pricing, and card authorization decisions.
- Storage or display of full PAN, CVV, PIN, magnetic-stripe data, or processor secrets.
- Customer onboarding, KYC adjudication, sanctions screening logic, and funding-account ledger implementation.
- Production code, APIs, database schemas, and UI designs in this homework submission.

## 3. Stakeholders and Roles

| Role | Goal | Allowed actions |
|---|---|---|
| Customer | Use and control their own virtual card | Create, view masked details, freeze/unfreeze, set limits, request replacement, view own transactions |
| Operations analyst | Resolve customer and processor issues | Search cards by safe identifiers, view status/history, retry approved operational workflows; no credential access |
| Compliance auditor | Prove who did what and when | Read immutable audit events and export narrowly scoped evidence |
| Fraud analyst | Investigate suspicious behavior | View risk flags and lifecycle history; place a policy hold through a separately authorized workflow |
| Service account | Integrate trusted internal services | Only explicitly granted machine-to-machine operations |

Authorization is deny-by-default. Customer access is ownership-scoped. Staff access is role- and purpose-scoped, logged, and subject to least privilege. No role in this feature can retrieve raw card credentials.

## 4. Mid-Level Objectives

- **MO-1 — Safe issuance:** An eligible, authenticated customer can create one virtual card per idempotent request and receive a stable card reference plus masked display data, without this system handling raw credentials.
- **MO-2 — Reliable lifecycle control:** A customer can view status, freeze, unfreeze, or replace their card with deterministic behavior under retries, concurrency, processor delays, and policy holds.
- **MO-3 — Enforced spending controls:** A customer can configure valid transaction, daily, and monthly limits in the account currency, with clear validation and predictable effective timing.
- **MO-4 — Understandable transaction history:** A customer can retrieve an ownership-scoped, cursor-paginated history whose monetary values, status transitions, timestamps, and empty states are unambiguous.
- **MO-5 — Controlled internal oversight:** Authorized staff can search safe identifiers and inspect lifecycle, policy, and audit history without exposure of prohibited cardholder data.
- **MO-6 — Evidentiary audit and notification:** Every material command and privileged read creates a tamper-evident audit event, and security-sensitive successful changes trigger a non-sensitive notification.
- **MO-7 — Operational fitness:** The feature meets the stated availability, latency, consistency, capacity, recovery, observability, privacy, and security targets.

## 5. Core Domain Rules

### 5.1 Card states

`PROVISIONING`, `ACTIVE`, `CUSTOMER_FROZEN`, `POLICY_FROZEN`, `REPLACEMENT_PENDING`, `REPLACED`, `CLOSED`, and `PROVISIONING_FAILED` are the only card states visible to this bounded context.

| Current state | Command | Result | Notes |
|---|---|---|---|
| none | Create | `PROVISIONING` then `ACTIVE` or `PROVISIONING_FAILED` | Same idempotency key and payload returns the original operation |
| `ACTIVE` | Freeze | `CUSTOMER_FROZEN` | Repeated freeze is a successful no-op |
| `CUSTOMER_FROZEN` | Unfreeze | `ACTIVE` | Denied if a policy hold now applies |
| `POLICY_FROZEN` | Unfreeze | No change | Customer receives a safe denial and support route |
| `ACTIVE` or `CUSTOMER_FROZEN` | Replace | `REPLACEMENT_PENDING`, then old card `REPLACED` and new card `ACTIVE` | New card activates only after processor confirmation |
| `REPLACED` or `CLOSED` | Any mutation | No change | Terminal state; return a conflict-safe domain error |

Processor state is authoritative for credential activation; the local state is authoritative for the last confirmed workflow state. Unknown or timed-out outcomes remain pending and are reconciled rather than guessed.

### 5.2 Money and limits

- Monetary values use integer minor units plus an ISO 4217 currency code; binary floating point is forbidden.
- Limits must use the funding account currency and be whole minor units greater than zero.
- Assumed product ranges: per-transaction `100`–`500,000` minor units, daily `100`–`1,000,000`, and monthly `100`–`5,000,000`. Product configuration may narrow these ranges.
- Invariant: per-transaction limit must not exceed daily limit; daily limit must not exceed monthly limit.
- A limit change takes effect for new authorization requests within 5 seconds of confirmed persistence. It does not retroactively affect pending or settled transactions.
- Lowering a limit below already-spent daily/monthly totals is allowed; subsequent authorizations are expected to be declined until the period resets. The response must disclose this consequence.
- Calendar periods use the funding account's configured IANA time zone. Stored timestamps remain UTC.

### 5.3 Identity and sensitive data

- Public resource IDs are opaque UUID/ULID-style identifiers and must not encode customer or account data.
- Display data is limited to card label, network, expiry month/year when supplied as a processor tokenized display attribute, and last four digits. Full PAN and CVV never cross this system boundary.
- Logs, traces, metrics, errors, notifications, analytics, and audit metadata must not contain PAN, CVV, authentication tokens, processor secrets, or unrestricted customer profile data.
- Staff search supports card reference, customer reference, processor reference, and last four plus an additional discriminator. Searching by last four alone is prohibited.

## 6. Non-Functional and Policy Requirements

All numerical targets below are **assumed design targets** for a consumer FinTech product and must be validated against production traffic and processor contracts before launch.

### 6.1 Performance and capacity

| Operation | Target, measured server-side excluding client network |
|---|---|
| Read card status/limits | p95 <= 300 ms, p99 <= 800 ms |
| List transactions | p95 <= 500 ms, p99 <= 1.2 s for pages up to 50 |
| Accept freeze/unfreeze/limit command | p95 <= 500 ms when processor confirmation is not required |
| Issue/replace workflow acknowledgement | p95 <= 800 ms; asynchronous completion target <= 10 s p95 and <= 60 s p99 |
| Operations search | p95 <= 1 s for a maximum page of 50 |

- Default transaction page size is 25; allowed range is 1–50. Cursor pagination must be stable under new inserts and use deterministic ordering by effective timestamp then immutable transaction ID.
- Design capacity assumption: 200 read requests/second and 50 mutation requests/second sustained, with a 3x burst for 60 seconds.
- Customer rate limits: 60 reads/minute and 10 lifecycle mutations/minute per customer; create and replace additionally allow 3 attempts/hour. Staff limits are role-specific and monitored.

These targets keep interactive controls responsive while acknowledging processor-dependent workflows. Cursor and page limits bound database and data-exposure costs.

### 6.2 Reliability, consistency, and recovery

- Monthly service availability target: 99.95% for reads and 99.9% for lifecycle commands, excluding announced maintenance.
- After a successful local write, reads reflect the change within 2 seconds. Processor-dependent state converges within 60 seconds p99; older pending operations generate an alert and enter reconciliation.
- Mutations require an idempotency key retained for at least 24 hours. Reusing a key with a different canonical payload returns `IDEMPOTENCY_CONFLICT` and performs no action.
- Outbound processor calls use bounded timeouts, exponential backoff with jitter, and a circuit breaker. Retry only operations known to be idempotent or carrying a processor idempotency key.
- Audit and workflow events use a transactional outbox or equivalent atomic persistence pattern. Notifications are at-least-once and consumers deduplicate by event ID.
- Recovery objectives for owned state: RPO <= 5 minutes and RTO <= 60 minutes. Audit evidence has RPO 0 for acknowledged writes through atomic event persistence.

### 6.3 Security, privacy, and compliance

- Strong customer authentication is required; replacement and sensitive display access require a recent step-up authentication signal no older than 5 minutes.
- Service-to-service traffic uses authenticated encryption; stored customer and audit data uses managed encryption with key rotation and separated access duties.
- Follow PCI DSS scope-minimization principles: use processor tokens and hosted credential reveal; never store sensitive authentication data. Final PCI scope requires qualified review.
- Apply GDPR-style data minimization, purpose limitation, access recording, retention, and data-subject workflows. Legal retention overrides deletion only for the necessary records.
- Lifecycle and privileged-read audit records are retained for 7 years as an assumed regulatory target; operational logs for 30 days and traces for 7 days unless policy requires otherwise. Retention is configurable and legal/compliance must approve it.
- Threat modeling must cover broken object-level authorization, replay, enumeration, confused-deputy access, injection, webhook forgery, race conditions, and sensitive-data leakage.

### 6.4 Audit event minimum fields

Every material command attempt records: unique event ID, UTC timestamp, actor type and opaque actor ID, authenticated session/service ID, action, target reference, request correlation ID, idempotency key hash where applicable, outcome, safe reason code, prior/new state, policy decision reference, source channel, and integrity-chain metadata. Audit records are append-only; corrections are new linked events. Privileged reads also record declared purpose and result count, never returned sensitive content.

## 7. Error Semantics

Errors use a stable machine code, safe user message, correlation ID, and retryability flag. Internal stack traces, processor payloads, and existence-revealing details are excluded.

| Condition | Code | Expected handling |
|---|---|---|
| Invalid field or limit invariant | `VALIDATION_FAILED` | Identify safe field errors; no mutation |
| Authentication missing/expired | `UNAUTHENTICATED` | Re-authenticate |
| Ownership or role check fails | `NOT_FOUND_OR_FORBIDDEN` | Do not reveal whether another customer's card exists; audit denial |
| Step-up required | `STEP_UP_REQUIRED` | Challenge before command |
| Policy hold blocks action | `POLICY_RESTRICTION` | Safe explanation and support route; audit policy reference |
| State transition invalid | `STATE_CONFLICT` | Return current safe state and refresh guidance |
| Idempotency key reused differently | `IDEMPOTENCY_CONFLICT` | No action; use a new key for a new intent |
| Dependency unavailable/unknown result | `OPERATION_PENDING` | Return operation reference; reconcile asynchronously |
| Rate exceeded | `RATE_LIMITED` | Return retry-after value; monitor abuse signals |

## 8. Beginning and Ending Context

### Beginning context

Assume an engineering repository with authenticated customer and staff shells, a funding-account service, an external PCI-compliant card processor, notification delivery, centralized observability, and deployment pipelines. Interfaces are not yet agreed; no virtual-card domain model, workflows, audit schema, contract tests, runbooks, or feature-specific dashboards exist. Test environments offer processor and notification sandboxes plus synthetic customers only.

### Ending context

An implementation based on this specification would contain:

- Versioned domain and API contracts for cards, limits, transactions, staff queries, errors, events, and dependency adapters.
- Persistent card/workflow state, idempotency records, and atomic audit/outbox events.
- Customer and staff experiences with enforced authorization boundaries.
- Processor, transaction-feed, identity, audit, and notification adapters with sandbox contract tests.
- Unit, property, integration, concurrency, end-to-end, security, performance, resilience, reconciliation, and accessibility verification.
- Dashboards, alerts, privacy controls, data-retention jobs, incident/runbook documentation, and an approved release checklist.

This list describes hypothetical implementation artifacts and does not require code for Homework 3.

## 9. Edge Cases and Failure Modes

| Scenario | User/ops-visible behavior | Audit, recovery, or compliance behavior |
|---|---|---|
| No card or no transactions | Clear empty state and eligible next action | No synthetic records; ordinary read telemetry only |
| Duplicate create/replace submission | Same key and payload returns original operation/result | One effective mutation; attempts linked to the idempotency record |
| Same idempotency key, different payload | Conflict response; no new operation | Security-relevant conflict event recorded |
| Freeze and unfreeze arrive concurrently | Serialize per card; one valid transition wins, loser receives current state/conflict | Both attempts and ordering recorded |
| Freeze races with authorization | UI states that in-flight authorization may complete; confirmed freeze blocks subsequent authorizations per processor SLA | Record freeze confirmation time; reconciliation flags later unexpected authorizations |
| Customer unfreezes a policy-frozen card | Denial without revealing fraud rules | Policy decision reference and denied attempt recorded |
| Processor times out after accepting create | Return pending, never issue a second card blindly | Poll/webhook reconciliation by idempotency reference; alert after 60 seconds |
| Forged, duplicate, or out-of-order webhook | No unsafe state regression | Verify signature/timestamp, deduplicate event ID, enforce transition/version, quarantine invalid event |
| Replacement succeeds remotely but local update fails | Pending message; old card not represented as safely replaced until reconciled | Outbox/reconciliation repairs state; high-priority alert if SLA exceeded |
| Invalid, negative, zero, excessive, mismatched-currency limit | Field-specific safe rejection | Record validation metric; audit only if abuse threshold or policy requires |
| Limit lowered below spend-to-date | Warn that further spending may decline; save valid limit | Store effective time and prior/new values |
| Stale client updates a limit | Version conflict and refreshed values | No overwrite; attempted version recorded safely |
| Transaction changes pending -> reversed -> settled correction | Show ordered status history/current status without double-counting | Immutable feed events; reconciliation validates aggregate totals |
| Duplicate transaction-feed event | No duplicate row or spend total | Deduplicate on provider event/transaction version |
| Transaction feed delayed | Display “last updated” time; do not imply completeness | Alert at feed-lag threshold; backfill and reconcile |
| Unauthorized card ID enumeration | Uniform not-found/forbidden response | Rate-limit, audit denied access, raise anomaly signal |
| Staff performs broad search or export | Require filters, purpose, and bounded result set; reject excessive scope | Privileged-read event; export watermark, expiry, and access record |
| Notification delivery fails | Successful card action remains successful; notification may be delayed | Retry with deduplication; dead-letter and alert without sensitive payload |
| Audit sink temporarily unavailable | Do not acknowledge a material mutation unless audit/outbox is atomically durable | Circuit-break or fail closed for regulated actions; recover from outbox |
| Dependency outage | Reads may show last confirmed state with timestamp; mutations return pending or unavailable according to certainty | No unsafe retry; alert and reconcile |
| Customer/account becomes ineligible mid-flow | Stop before activation or policy-freeze according to confirmed processor state | Record eligibility decision version; route ambiguous cases to ops |

## 10. Verification Strategy

| Objective | Evidence required |
|---|---|
| MO-1 | Eligibility/ownership decision tests; processor contract tests; create retry and unknown-outcome scenarios; scan proving prohibited card data is absent |
| MO-2 | State-machine unit/property tests; concurrent-command integration tests; webhook ordering/signature tests; replacement reconciliation end-to-end scenario |
| MO-3 | Boundary, currency, invariant, time-zone, stale-version, and effective-time tests; authorization-control contract test |
| MO-4 | Pagination stability, deduplication, status-transition, empty-state, ownership, formatting, and feed-lag tests; aggregate reconciliation fixture |
| MO-5 | Role/attribute authorization matrix; object-level authorization and enumeration tests; privileged-search audit review; export expiry check |
| MO-6 | Audit schema/integrity/retention tests; atomicity failure injection; notification deduplication and dead-letter tests; manual compliance evidence review |
| MO-7 | Load test against stated percentiles/capacity; dependency latency/failure injection; backup restore exercise; dashboard/alert and privacy-log review |

Required fixtures include: eligible/ineligible customers, multiple customers with deliberately similar last-four values, every card state, policy holds, currencies with 0/2/3 minor digits, daylight-saving transitions, boundary limit values, duplicate/out-of-order events, long transaction histories, delayed dependencies, and synthetic fraud-like retry/enumeration bursts. Production card data is forbidden in tests.

Release requires product, engineering, security, privacy/compliance, operations, and processor-integration review. Any unmet target needs a documented owner, risk acceptance, expiry date, and rollback/containment plan.

## 11. Low-Level Tasks

Each task below is an executable slice for a future implementation team. File paths are proposed ending-context artifacts, not deliverables for this homework.

### LLT-01 — Define domain vocabulary and state machine

- **Serves:** MO-1, MO-2
- **Prompt:** Define versioned virtual-card entities, command results, permitted state transitions, invariants, and safe error codes from Sections 5 and 7. Reject unlisted transitions and model pending/unknown dependency outcomes explicitly.
- **Create/update:** `docs/domain/virtual-card.md`, domain model/state-machine module
- **Acceptance criteria:** Every state/transition in Section 5 has a deterministic result; terminal and policy-frozen behavior is explicit; automated table-driven tests cover every state-command pair.

### LLT-02 — Specify customer authorization and eligibility

- **Serves:** MO-1, MO-2, MO-3, MO-4
- **Prompt:** Define authentication, ownership, eligibility, recent step-up, and policy-decision contracts with deny-by-default behavior and uniform resource-denial responses.
- **Create/update:** `docs/security/access-control.md`, authorization policy module
- **Acceptance criteria:** An access matrix covers every customer command; cross-customer access never reveals existence; stale/unavailable eligibility decisions fail safely; denials produce safe audit events.

### LLT-03 — Specify idempotent card issuance

- **Serves:** MO-1, MO-6
- **Prompt:** Design the create-card workflow with payload hashing, 24-hour idempotency retention, processor tokenization, unknown-outcome reconciliation, and prohibited-data boundaries.
- **Create/update:** issuance contract/workflow and processor adapter contract
- **Acceptance criteria:** Identical retries yield one card; conflicting reuse yields no mutation; timeouts never cause blind duplicate issuance; returned data contains only allowed display attributes; audit persistence is atomic.

### LLT-04 — Specify freeze and unfreeze commands

- **Serves:** MO-2, MO-6
- **Prompt:** Define serialized, version-aware freeze/unfreeze commands, idempotent no-ops, policy-hold precedence, processor confirmation, and concurrent-action behavior.
- **Create/update:** lifecycle command contract/workflow
- **Acceptance criteria:** Concurrency tests yield one valid ordered state history; policy-frozen cards cannot be customer-unfrozen; retry behavior is deterministic; success and denial audits contain prior/new state.

### LLT-05 — Specify replacement workflow

- **Serves:** MO-2, MO-6
- **Prompt:** Define replacement reason codes, step-up authentication, pending operation tracking, old/new card linkage, processor reconciliation, and safe customer messaging.
- **Create/update:** replacement contract/workflow and reconciliation job
- **Acceptance criteria:** One replacement intent produces at most one new card; old card becomes terminal only after confirmed outcome; partial failures reconcile; reason and linkage are auditable without sensitive data.

### LLT-06 — Specify spending-limit management

- **Serves:** MO-3, MO-6
- **Prompt:** Define versioned limit reads/updates using minor units, currency and range validation, invariants, effective timestamp, account time zone, and spend-to-date warning behavior.
- **Create/update:** limits contract/policy module
- **Acceptance criteria:** Boundary and currency fixtures pass; floating point is absent; stale updates do not overwrite; propagation is measurable against the 5-second target; audit records prior/new values.

### LLT-07 — Specify transaction ingestion and history

- **Serves:** MO-4, MO-7
- **Prompt:** Define deduplicated/versioned transaction ingestion and ownership-scoped cursor pagination for pending, declined, reversed, and settled transactions, including delayed-feed indicators.
- **Create/update:** transaction-feed contract, read model, and history contract
- **Acceptance criteria:** Duplicate/out-of-order fixtures converge correctly; pages contain no repeats or gaps during inserts; maximum 50 is enforced; totals do not double-count reversals; empty and stale states are explicit.

### LLT-08 — Specify staff search and audit inspection

- **Serves:** MO-5, MO-6
- **Prompt:** Define purpose-bound staff search and evidence inspection using only safe identifiers, least-privilege filters, bounded pagination, and expiring exports.
- **Create/update:** operations contract, staff authorization matrix, evidence-export policy
- **Acceptance criteria:** Last-four-only search is rejected; unauthorized fields/actions are absent; every privileged read records purpose and count; exports are scoped, watermarked, encrypted, expire, and have access logs.

### LLT-09 — Define audit and event delivery

- **Serves:** MO-6, MO-7
- **Prompt:** Define append-only audit events and transactional outbox delivery with integrity chaining, schema versioning, deduplication, retention, and correction-by-linked-event.
- **Create/update:** audit/event schemas, outbox contract, retention policy
- **Acceptance criteria:** All Section 6.4 fields are represented; acknowledged mutations survive injected sink failure with evidence intact; events contain no prohibited data; tampering and event gaps are detectable.

### LLT-10 — Define safe notifications

- **Serves:** MO-6
- **Prompt:** Define notifications for creation, freeze/unfreeze, limit change, and replacement using event IDs, non-sensitive templates, preference rules where legally permitted, retries, and dead-letter handling.
- **Create/update:** notification event/template contracts
- **Acceptance criteria:** Duplicate delivery is suppressed; content contains no full credential or sensitive reason; notification failure cannot roll back a card action; exhausted retries alert operators.

### LLT-11 — Build the verification specification

- **Serves:** MO-1 through MO-7
- **Prompt:** Convert Section 10 into a traceable verification plan with fixtures, automated test categories, manual checkpoints, negative tests, performance scenarios, and evidence owners.
- **Create/update:** `docs/testing/virtual-card-verification.md`, requirements trace matrix
- **Acceptance criteria:** Every MO and edge case maps to at least one check; critical state transitions have unit, integration, and failure-injection coverage; all fixtures are synthetic; exit criteria and evidence locations are named.

### LLT-12 — Define observability, SLOs, and reconciliation

- **Serves:** MO-2, MO-4, MO-7
- **Prompt:** Define redacted metrics, structured logs, traces, dashboards, alerts, reconciliation checks, and runbooks for latency, pending age, processor divergence, feed lag, audit delivery, and notification backlog.
- **Create/update:** observability specification and operational runbooks
- **Acceptance criteria:** Each SLO has a measurement and alert; no high-cardinality sensitive labels exist; reconciliation detects missing/duplicate/state-divergent records; every alert links to an owner and runbook.

### LLT-13 — Perform security and privacy readiness review

- **Serves:** MO-5, MO-6, MO-7
- **Prompt:** Threat-model all trust boundaries and document privacy inventory, lawful purpose, minimization, retention, deletion/restriction behavior, secrets handling, and PCI scope assumptions.
- **Create/update:** threat model, data-flow diagram, privacy and retention assessment
- **Acceptance criteria:** Section 6.3 threats have mitigations and verification; prohibited-data scans cover every channel; retention exceptions require approval; unresolved high-severity threats block release.

### LLT-14 — Define rollout and recovery readiness

- **Serves:** MO-7
- **Prompt:** Define backward-compatible contract rollout, feature flags, sandbox certification, canary metrics, rollback/kill-switch behavior, backup restoration, and incident response exercises.
- **Create/update:** release plan and recovery runbook
- **Acceptance criteria:** Rollback does not strand pending workflows; a restore exercise demonstrates RPO/RTO; canary abort thresholds are numeric; on-call ownership and dependency escalation paths are documented.

## 12. Requirements Traceability Matrix

| Objective | Primary tasks | Primary edge/failure evidence |
|---|---|---|
| MO-1 | LLT-01, 02, 03, 11 | duplicate create, conflicting key, processor timeout, mid-flow ineligibility |
| MO-2 | LLT-01, 02, 04, 05, 12 | concurrent commands, policy hold, authorization race, partial replacement |
| MO-3 | LLT-02, 06, 11 | invalid currency/range, spend-to-date, stale version |
| MO-4 | LLT-02, 07, 12 | empty history, duplicate/out-of-order events, delayed feed |
| MO-5 | LLT-02, 08, 13 | enumeration, excessive staff search/export, permission boundaries |
| MO-6 | LLT-03–10, 13 | audit outage, duplicate notification, privileged read, correction event |
| MO-7 | LLT-09, 11–14 | dependency outage, burst load, restoration, reconciliation and alerting |

## 13. Definition of Done

A future implementation is ready for release only when all low-level acceptance criteria are evidenced, the traceability matrix has no orphan requirement, numerical targets pass in a production-like environment, processor sandbox certification succeeds, prohibited-data scans are clean, recovery and reconciliation exercises pass, and product/security/privacy/compliance/operations approvals are recorded. No acceptance criterion may be waived silently.
