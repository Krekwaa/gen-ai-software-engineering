from uuid import UUID

import pytest
from pydantic import ValidationError

from src.backend.app.models import (
    ClassificationResult,
    DeviceType,
    Ticket,
    TicketCategory,
    TicketCreate,
    TicketMetadata,
    TicketPriority,
    TicketSource,
    TicketStatus,
    TicketUpdate,
)


def valid_ticket_payload() -> dict:
    return {
        "customer_id": "cust-001",
        "customer_email": "customer@example.com",
        "customer_name": "Ada Lovelace",
        "subject": "Cannot access account",
        "description": "I cannot access my account after password reset.",
    }


def test_ticket_create_accepts_minimum_valid_payload() -> None:
    ticket = TicketCreate(**valid_ticket_payload())

    assert ticket.customer_email == "customer@example.com"
    assert ticket.category == TicketCategory.OTHER
    assert ticket.priority == TicketPriority.MEDIUM
    assert ticket.status == TicketStatus.NEW
    assert ticket.metadata.source == TicketSource.API


def test_ticket_has_uuid_and_timestamps() -> None:
    ticket = Ticket(**valid_ticket_payload())

    assert isinstance(ticket.id, UUID)
    assert ticket.created_at.tzinfo is not None
    assert ticket.updated_at.tzinfo is not None
    assert ticket.resolved_at is None


def test_invalid_email_is_rejected() -> None:
    payload = valid_ticket_payload()
    payload["customer_email"] = "not-an-email"

    with pytest.raises(ValidationError):
        TicketCreate(**payload)


def test_subject_length_is_validated() -> None:
    payload = valid_ticket_payload()
    payload["subject"] = ""

    with pytest.raises(ValidationError):
        TicketCreate(**payload)

    payload["subject"] = "x" * 201

    with pytest.raises(ValidationError):
        TicketCreate(**payload)


def test_description_length_is_validated() -> None:
    payload = valid_ticket_payload()
    payload["description"] = "too short"

    with pytest.raises(ValidationError):
        TicketCreate(**payload)

    payload["description"] = "x" * 2001

    with pytest.raises(ValidationError):
        TicketCreate(**payload)


def test_invalid_enum_values_are_rejected() -> None:
    payload = valid_ticket_payload()
    payload["priority"] = "immediate"

    with pytest.raises(ValidationError):
        TicketCreate(**payload)


def test_metadata_validates_source_and_device_type() -> None:
    metadata = TicketMetadata(
        source=TicketSource.CHAT,
        browser="Firefox",
        device_type=DeviceType.DESKTOP,
    )

    assert metadata.source == TicketSource.CHAT
    assert metadata.device_type == DeviceType.DESKTOP

    with pytest.raises(ValidationError):
        TicketMetadata(source="fax", device_type="watch")


def test_tags_are_normalized_and_deduplicated() -> None:
    payload = valid_ticket_payload()
    payload["tags"] = [" Login ", "login", "URGENT", ""]

    ticket = TicketCreate(**payload)

    assert ticket.tags == ["login", "urgent"]


def test_ticket_update_allows_partial_fields() -> None:
    update = TicketUpdate(status=TicketStatus.IN_PROGRESS, assigned_to=" Agent One ")

    assert update.status == TicketStatus.IN_PROGRESS
    assert update.assigned_to == "Agent One"


def test_resolved_status_sets_resolved_at() -> None:
    payload = valid_ticket_payload()
    payload["status"] = TicketStatus.RESOLVED

    ticket = Ticket(**payload)

    assert ticket.resolved_at is not None


def test_apply_update_refreshes_updated_at_and_status() -> None:
    ticket = Ticket(**valid_ticket_payload())
    updated = ticket.apply_update(TicketUpdate(status=TicketStatus.RESOLVED))

    assert updated.status == TicketStatus.RESOLVED
    assert updated.resolved_at is not None
    assert updated.updated_at >= ticket.updated_at


def test_classification_result_validates_confidence_and_keywords() -> None:
    result = ClassificationResult(
        category=TicketCategory.ACCOUNT_ACCESS,
        priority=TicketPriority.URGENT,
        confidence=0.91,
        reasoning="Detected account access keywords.",
        keywords_found=[" Can't Access ", "PASSWORD", ""],
    )

    assert result.keywords_found == ["can't access", "password"]

    with pytest.raises(ValidationError):
        ClassificationResult(
            category=TicketCategory.OTHER,
            priority=TicketPriority.MEDIUM,
            confidence=1.5,
            reasoning="Out of range.",
        )
