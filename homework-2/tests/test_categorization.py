from src.backend.app.classifier import ticket_classifier
from src.backend.app.models import Ticket, TicketCategory, TicketPriority


def make_ticket(subject: str, description: str, tags: list[str] | None = None) -> Ticket:
    return Ticket(
        customer_id="cust-001",
        customer_email="customer@example.com",
        customer_name="Customer One",
        subject=subject,
        description=description,
        tags=tags or [],
    )


def test_classifies_account_access_as_urgent() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Cannot access account",
            "I cannot access my account after resetting my password.",
        )
    )

    assert result.category == TicketCategory.ACCOUNT_ACCESS
    assert result.priority == TicketPriority.URGENT
    assert "cannot access" in result.keywords_found


def test_classifies_billing_question() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Invoice needed",
            "Please send my invoice and explain the billing charge.",
        )
    )

    assert result.category == TicketCategory.BILLING_QUESTION
    assert result.priority == TicketPriority.MEDIUM


def test_classifies_feature_request_as_low_when_suggestion() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Dashboard suggestion",
            "This is a suggestion for a new reporting feature.",
        )
    )

    assert result.category == TicketCategory.FEATURE_REQUEST
    assert result.priority == TicketPriority.LOW


def test_classifies_bug_report() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Bug with export",
            "Steps to reproduce: export a report. Actual result is a defect.",
        )
    )

    assert result.category == TicketCategory.BUG_REPORT


def test_classifies_technical_issue() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "App crash",
            "The app crashes with an error after login.",
        )
    )

    assert result.category == TicketCategory.TECHNICAL_ISSUE


def test_high_priority_keywords_override_default_priority() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Export is blocking launch",
            "This important issue is blocking our team and needs help asap.",
        )
    )

    assert result.priority == TicketPriority.HIGH


def test_urgent_priority_has_precedence_over_high_and_low() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Security issue",
            "This important security issue is blocking us and has a minor cosmetic note.",
        )
    )

    assert result.priority == TicketPriority.URGENT


def test_uncategorized_ticket_defaults_to_other_medium() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "General question",
            "I have a general question about using the service today.",
        )
    )

    assert result.category == TicketCategory.OTHER
    assert result.priority == TicketPriority.MEDIUM
    assert result.confidence == 0.35


def test_tags_are_used_for_classification() -> None:
    result = ticket_classifier.classify(
        make_ticket(
            "Question",
            "I need help understanding behavior in the application.",
            tags=["billing", "invoice"],
        )
    )

    assert result.category == TicketCategory.BILLING_QUESTION


def test_confidence_increases_with_keyword_matches() -> None:
    weak = ticket_classifier.classify(
        make_ticket("Invoice", "Please send the invoice for this month.")
    )
    strong = ticket_classifier.classify(
        make_ticket("Invoice billing charge", "Please explain this payment and subscription charge.")
    )

    assert strong.confidence > weak.confidence
    assert strong.confidence <= 0.95
