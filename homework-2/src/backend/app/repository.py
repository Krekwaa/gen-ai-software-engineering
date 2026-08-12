from __future__ import annotations

from threading import RLock
from uuid import UUID

from src.backend.app.models import (
    ClassificationDecisionLog,
    Ticket,
    TicketClassificationUpdate,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TicketUpdate,
)


class TicketRepository:
    def __init__(self) -> None:
        self._tickets: dict[UUID, Ticket] = {}
        self._classification_logs: list[ClassificationDecisionLog] = []
        self._lock = RLock()

    def create(self, payload: TicketCreate) -> Ticket:
        ticket = Ticket.model_validate(payload.model_dump(exclude={"auto_classify"}))
        with self._lock:
            self._tickets[ticket.id] = ticket
        return ticket

    def list(
        self,
        category: TicketCategory | None = None,
        priority: TicketPriority | None = None,
        status: TicketStatus | None = None,
    ) -> list[Ticket]:
        with self._lock:
            tickets = list(self._tickets.values())

        if category is not None:
            tickets = [ticket for ticket in tickets if ticket.category == category]

        if priority is not None:
            tickets = [ticket for ticket in tickets if ticket.priority == priority]

        if status is not None:
            tickets = [ticket for ticket in tickets if ticket.status == status]

        return sorted(tickets, key=lambda ticket: ticket.created_at)

    def get(self, ticket_id: UUID) -> Ticket | None:
        with self._lock:
            return self._tickets.get(ticket_id)

    def update(self, ticket_id: UUID, payload: TicketUpdate) -> Ticket | None:
        with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                return None

            updated_ticket = ticket.apply_update(payload)
            self._tickets[ticket_id] = updated_ticket
            return updated_ticket

    def apply_classification(
        self,
        ticket_id: UUID,
        payload: TicketClassificationUpdate,
    ) -> Ticket | None:
        with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                return None

            updated_ticket = ticket.apply_classification(payload)
            self._tickets[ticket_id] = updated_ticket
            return updated_ticket

    def add_classification_log(self, log: ClassificationDecisionLog) -> None:
        with self._lock:
            self._classification_logs.append(log)

    def list_classification_logs(self, ticket_id: UUID | None = None) -> list[ClassificationDecisionLog]:
        with self._lock:
            if ticket_id is None:
                return list(self._classification_logs)

            return [log for log in self._classification_logs if log.ticket_id == ticket_id]

    def delete(self, ticket_id: UUID) -> bool:
        with self._lock:
            if ticket_id not in self._tickets:
                return False

            del self._tickets[ticket_id]
            return True

    def clear(self) -> None:
        with self._lock:
            self._tickets.clear()
            self._classification_logs.clear()


ticket_repository = TicketRepository()
