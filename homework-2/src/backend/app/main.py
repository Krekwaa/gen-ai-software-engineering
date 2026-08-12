from uuid import UUID

from fastapi import FastAPI, File, HTTPException, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from src.backend.app.classifier import ticket_classifier
from src.backend.app.importers import ImportParseError, parse_ticket_file
from src.backend.app.models import (
    ClassificationDecisionLog,
    ClassificationResult,
    ImportErrorDetail,
    ImportSummary,
    Ticket,
    TicketClassificationUpdate,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketStatus,
    TicketUpdate,
)
from src.backend.app.repository import ticket_repository


app = FastAPI(
    title="Intelligent Customer Support System",
    description="Customer support ticket API for Homework 2.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tickets", response_model=Ticket, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate) -> Ticket:
    ticket = ticket_repository.create(payload)
    if payload.auto_classify:
        return classify_and_store_ticket(ticket)

    return ticket


@app.get("/tickets", response_model=list[Ticket])
def list_tickets(
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    status: TicketStatus | None = None,
) -> list[Ticket]:
    return ticket_repository.list(category=category, priority=priority, status=status)


@app.post("/tickets/import", response_model=ImportSummary)
async def import_tickets(file: UploadFile = File(...)) -> ImportSummary:
    content = await file.read()

    try:
        records = parse_ticket_file(content, file.filename or "")
    except ImportParseError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    errors: list[ImportErrorDetail] = []
    successful = 0

    for index, record in enumerate(records, start=1):
        try:
            payload = TicketCreate.model_validate(record)
            ticket = ticket_repository.create(payload)
            if payload.auto_classify:
                classify_and_store_ticket(ticket)
            successful += 1
        except ValidationError as exc:
            errors.append(
                ImportErrorDetail(
                    record=index,
                    error=exc.errors()[0]["msg"],
                )
            )

    return ImportSummary(
        total_records=len(records),
        successful=successful,
        failed=len(errors),
        errors=errors,
    )


@app.post("/tickets/{ticket_id}/auto-classify", response_model=ClassificationResult)
def auto_classify_ticket(ticket_id: UUID) -> ClassificationResult:
    ticket = ticket_repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    result = ticket_classifier.classify(ticket)
    apply_classification_result(ticket, result)
    return result


@app.get("/tickets/{ticket_id}/classification-logs", response_model=list[ClassificationDecisionLog])
def list_classification_logs(ticket_id: UUID) -> list[ClassificationDecisionLog]:
    ticket = ticket_repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket_repository.list_classification_logs(ticket_id)


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: UUID) -> Ticket:
    ticket = ticket_repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket


@app.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: UUID, payload: TicketUpdate) -> Ticket:
    ticket = ticket_repository.update(ticket_id, payload)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket


@app.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: UUID) -> Response:
    deleted = ticket_repository.delete(ticket_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def classify_and_store_ticket(ticket: Ticket) -> Ticket:
    result = ticket_classifier.classify(ticket)
    return apply_classification_result(ticket, result)


def apply_classification_result(ticket: Ticket, result: ClassificationResult) -> Ticket:
    updated_ticket = ticket_repository.apply_classification(
        ticket.id,
        TicketClassificationUpdate(
            category=result.category,
            priority=result.priority,
            classification_confidence=result.confidence,
            classification_reasoning=result.reasoning,
            classification_keywords=result.keywords_found,
            classification_overridden=False,
        ),
    )
    ticket_repository.add_classification_log(ticket_classifier.create_log(ticket, result))

    if updated_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return updated_ticket
