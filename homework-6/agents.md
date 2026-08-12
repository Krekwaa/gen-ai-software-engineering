# AI Agent Guidelines - Transaction Pipeline

`specification.md` is authoritative. Agents must preserve Decimal monetary handling, deterministic risk behavior, privacy-safe outputs, and test isolation.

## Agent 1 - Specification

Use `$write-spec` before code changes that alter behavior. Maintain MO and LLT traceability, resolve ambiguity explicitly, and never invent financial policy.

## Agent 2 - Code Generation

Implement one LLT at a time. Consult context7 for current framework APIs, record every query and applied pattern in `research-notes.md`, and keep domain logic independent of FastAPI and MCP transports.

## Agent 3 - Unit Tests

Map tests to the named stage behaviors and integration path. Use temporary directories, cover rejection and risk boundaries, and never weaken or delete a failing test to pass the coverage gate.

## Agent 4 - Documentation

Document only verified commands and results. Keep the author name Vladyslav Shmygelskyy, architecture, setup, evidence links, presentation, and PR narrative synchronized with the implementation.

## Security and completion rules

- Never log or expose plaintext account numbers or descriptions.
- Treat transaction IDs as untrusted when used for file lookup.
- Report commands actually run and distinguish real evidence from illustrative content.
- Completion requires passing tests, at least 80% coverage, all eight final results, valid MCP configuration, and all rubric artifacts.

