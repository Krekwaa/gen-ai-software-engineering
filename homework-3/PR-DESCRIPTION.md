# Homework 3 - Specification-Driven Virtual Card Lifecycle

## Summary

Created a documentation-only virtual-card lifecycle specification for a regulated environment. The package contains layered objectives, measurable SLOs, implementation guardrails, edge cases, verification strategy, fourteen executable task slices, and requirements traceability.

## AI-assisted workflow

Codex helped structure and cross-check the specification, agent rules, and Copilot instructions. The output was reviewed for orphaned objectives, unsafe card-data assumptions, ambiguous failure behavior, and unverifiable performance language.

## Review instructions

Start with `README.md`, then review `specification.md`, `agents.md`, and `.github/copilot-instructions.md`. No implementation is required for this homework.

## Challenges

The key challenge was balancing implementable detail with a bounded feature scope. Processor uncertainty, idempotency, audit durability, authorization, and reconciliation are explicit rather than left for future interpretation.

