from collections.abc import Iterable

from src.backend.app.models import (
    ClassificationDecisionLog,
    ClassificationResult,
    Ticket,
    TicketCategory,
    TicketPriority,
    utc_now,
)


CATEGORY_KEYWORDS: dict[TicketCategory, tuple[str, ...]] = {
    TicketCategory.ACCOUNT_ACCESS: (
        "login",
        "password",
        "2fa",
        "two-factor",
        "can't access",
        "cannot access",
        "locked out",
        "account access",
    ),
    TicketCategory.BILLING_QUESTION: (
        "payment",
        "invoice",
        "refund",
        "billing",
        "charge",
        "subscription",
    ),
    TicketCategory.FEATURE_REQUEST: (
        "feature",
        "enhancement",
        "suggestion",
        "would like",
        "request",
        "improve",
    ),
    TicketCategory.BUG_REPORT: (
        "bug",
        "defect",
        "reproduce",
        "steps to reproduce",
        "expected result",
        "actual result",
    ),
    TicketCategory.TECHNICAL_ISSUE: (
        "error",
        "crash",
        "broken",
        "not working",
        "failed",
        "timeout",
    ),
}

PRIORITY_KEYWORDS: dict[TicketPriority, tuple[str, ...]] = {
    TicketPriority.URGENT: (
        "can't access",
        "cannot access",
        "critical",
        "production down",
        "security",
    ),
    TicketPriority.HIGH: (
        "important",
        "blocking",
        "asap",
    ),
    TicketPriority.LOW: (
        "minor",
        "cosmetic",
        "suggestion",
    ),
}


class TicketClassifier:
    def classify(self, ticket: Ticket) -> ClassificationResult:
        text = self._ticket_text(ticket)
        category, category_keywords = self._classify_category(text)
        priority, priority_keywords = self._classify_priority(text)
        keywords = self._dedupe([*category_keywords, *priority_keywords])
        confidence = self._confidence(keywords)

        return ClassificationResult(
            category=category,
            priority=priority,
            confidence=confidence,
            reasoning=self._reasoning(category, priority, keywords),
            keywords_found=keywords,
        )

    def create_log(self, ticket: Ticket, result: ClassificationResult) -> ClassificationDecisionLog:
        return ClassificationDecisionLog(
            ticket_id=ticket.id,
            category=result.category,
            priority=result.priority,
            confidence=result.confidence,
            reasoning=result.reasoning,
            keywords_found=result.keywords_found,
            created_at=utc_now(),
        )

    def _ticket_text(self, ticket: Ticket) -> str:
        parts: Iterable[str] = (
            ticket.subject,
            ticket.description,
            " ".join(ticket.tags),
        )
        return " ".join(parts).lower()

    def _classify_category(self, text: str) -> tuple[TicketCategory, list[str]]:
        matches: list[tuple[TicketCategory, list[str]]] = []

        for category, keywords in CATEGORY_KEYWORDS.items():
            found = self._find_keywords(text, keywords)
            if found:
                matches.append((category, found))

        if not matches:
            return TicketCategory.OTHER, []

        return max(matches, key=lambda match: len(match[1]))

    def _classify_priority(self, text: str) -> tuple[TicketPriority, list[str]]:
        for priority in (TicketPriority.URGENT, TicketPriority.HIGH, TicketPriority.LOW):
            found = self._find_keywords(text, PRIORITY_KEYWORDS[priority])
            if found:
                return priority, found

        return TicketPriority.MEDIUM, []

    def _find_keywords(self, text: str, keywords: Iterable[str]) -> list[str]:
        return [keyword for keyword in keywords if keyword in text]

    def _confidence(self, keywords: list[str]) -> float:
        if not keywords:
            return 0.35

        return min(0.95, 0.55 + (0.1 * len(keywords)))

    def _reasoning(
        self,
        category: TicketCategory,
        priority: TicketPriority,
        keywords: list[str],
    ) -> str:
        if keywords:
            return (
                f"Classified as {category} with {priority} priority based on "
                f"keywords: {', '.join(keywords)}."
            )

        return f"Classified as {category} with {priority} priority using default rules."

    def _dedupe(self, values: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()

        for value in values:
            if value not in seen:
                deduped.append(value)
                seen.add(value)

        return deduped


ticket_classifier = TicketClassifier()
