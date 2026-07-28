# Homework 3: Specification-Driven Virtual Card Lifecycle

> **Student:** Vlad
>
> **Task:** Homework 3 — Specification-Driven Design
>
> **Submission date:** July 16, 2026
>
> **AI assistance:** Codex was used to structure, draft, and cross-check the documentation; the submitted artifact is a specification package, not an implementation.

## Task summary

This submission specifies a regulated virtual-card lifecycle feature. Customers can create, view, freeze/unfreeze, limit, replace, and review transactions for a virtual card. Authorized operations, compliance, and fraud personnel receive a strictly controlled oversight view. Actual code, APIs, UI, card authorization, raw credential storage, onboarding, and dispute handling are deliberately out of scope.

## Deliverables

- [`specification.md`](specification.md) — layered product and engineering specification with objectives, policies, context, edge cases, verification, 14 executable task slices, and traceability.
- [`agents.md`](agents.md) — persistent instructions for an AI implementation/review agent.
- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — concise editor-level rules that reinforce safe defaults while code is suggested.
- [`specification-TEMPLATE-example.md`](specification-TEMPLATE-example.md) and [`TASKS.md`](TASKS.md) — supplied homework source material, retained unchanged.

## Rationale

### Why virtual-card lifecycle management

The domain is small enough to define clear boundaries but rich enough to demonstrate realistic FinTech concerns: money, state transitions, retries, external processors, privileged access, fraud-policy precedence, transaction consistency, and regulated evidence. The specification explicitly excludes processor authorization and raw credentials to reduce PCI exposure and prevent the exercise from becoming an entire card platform.

### Why the document is layered

The high-level objective fixes the outcome and scope boundary. Seven observable mid-level objectives separate issuance, lifecycle control, limits, history, internal oversight, evidence, and operational fitness. Domain and non-functional rules then constrain how those outcomes may be achieved. Fourteen low-level tasks name their parent objectives and contain checkable acceptance criteria. The traceability matrix provides a reverse check so an objective, implementation task, or critical failure mode cannot quietly become orphaned.

### How performance targets were chosen

All numbers are labeled assumed targets because no measured production baseline or processor contract was supplied. Interactive reads target 300–500 ms p95 so status, controls, and history feel responsive. Processor-dependent issuance/replacement is acknowledged quickly but may finish asynchronously, with a 10-second p95, 60-second p99, and reconciliation after uncertainty. Pages are capped at 50 to limit query cost and accidental data exposure. Capacity assumes moderate product traffic plus a 3x short burst. Availability, consistency, RPO, and RTO targets make operational tradeoffs testable rather than using vague terms such as “fast” or “reliable.” Before production, owners would validate these values with traffic forecasts, load tests, dependency SLAs, and business-impact analysis.

### Why verification is detailed

Financial workflows fail at boundaries, not only on happy paths. Verification therefore includes state-machine and property tests, service contracts, authorization negatives, concurrent commands, duplicate/out-of-order events, dependency failure injection, reconciliation, performance percentiles, prohibited-data scans, restore exercises, and manual security/privacy/compliance checkpoints. Synthetic fixtures cover all card states, currency precision, daylight-saving boundaries, similar last-four values, and long histories. Each mid-level objective has named evidence in Specification Section 10, while task-level acceptance criteria make “done” independently checkable.

## Industry best practices and where they appear

| Practice | Where applied |
|---|---|
| PCI scope minimization and tokenization | Specification Sections 2, 5.3, and 6.3; agent and Copilot prohibited-data rules |
| Least privilege, ownership checks, purpose-bound staff access | Sections 3, 5.3, 6.3; LLT-02 and LLT-08 |
| Integer minor-unit money and currency invariants | Section 5.2; LLT-06; both AI rule files |
| Idempotency, optimistic/version checks, safe retries | Sections 6.2 and 9; LLT-03 through LLT-06 |
| Explicit state machine and policy-hold precedence | Section 5.1; LLT-01 and LLT-04 |
| Unknown-outcome reconciliation rather than unsafe retry | Sections 5.1, 6.2, and 9; LLT-03, LLT-05, and LLT-12 |
| Append-only, tamper-evident audit and atomic outbox | Sections 6.2 and 6.4; LLT-09 |
| Privacy minimization, retention, and controlled export | Sections 5.3 and 6.3; LLT-08 and LLT-13 |
| Secure webhook processing and event deduplication | Section 9; LLT-07 and agent/editor rules |
| Stable cursor pagination and bounded queries | Sections 6.1 and 9; LLT-07 and LLT-08 |
| Measurable SLOs, observability, recovery, and runbooks | Sections 6.1–6.2; LLT-12 and LLT-14 |
| Defense against object-level authorization and enumeration flaws | Sections 6.3, 7, and 9; LLT-02 and LLT-13 |
| Requirements-to-verification traceability | Sections 10–13, especially the matrix in Section 12 |

These practices are framed as implementation and review requirements, not claims that a future system is automatically compliant. PCI scope, privacy obligations, fraud policy, and retention require validation by qualified organizational owners.

## Submission review checklist

- [x] One crisp high-level objective with an explicit scope boundary.
- [x] Observable mid-level objectives and measurable non-functional targets.
- [x] Beginning and ending context.
- [x] Feature-specific edge cases with customer and audit/recovery outcomes.
- [x] Verification evidence mapped to every mid-level objective.
- [x] Substantial low-level decomposition with acceptance criteria and traceability.
- [x] AI agent rules covering stack assumptions, domain policy, testing, edge cases, security, and compliance.
- [x] Editor/AI rules in a recognized Copilot location.
- [x] README rationale and section-level mapping to industry practices.
- [x] Documentation only; no application implementation.
