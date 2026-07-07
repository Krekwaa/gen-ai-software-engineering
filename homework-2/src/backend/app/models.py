from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class TicketCategory(StrEnum):
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL_ISSUE = "technical_issue"
    BILLING_QUESTION = "billing_question"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"


class TicketPriority(StrEnum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketSource(StrEnum):
    WEB_FORM = "web_form"
    EMAIL = "email"
    API = "api"
    CHAT = "chat"
    PHONE = "phone"


class DeviceType(StrEnum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class TicketMetadata(BaseModel):
    source: TicketSource = TicketSource.API
    browser: str | None = Field(default=None, max_length=100)
    device_type: DeviceType | None = None

    model_config = ConfigDict(use_enum_values=True)


class ClassificationResult(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    confidence: float = Field(ge=0, le=1)
    reasoning: str = Field(min_length=1, max_length=1000)
    keywords_found: list[str] = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("keywords_found")
    @classmethod
    def normalize_keywords(cls, value: list[str]) -> list[str]:
        return [keyword.strip().lower() for keyword in value if keyword.strip()]


class ClassificationDecisionLog(ClassificationResult):
    ticket_id: UUID
    created_at: datetime


class ImportErrorDetail(BaseModel):
    record: int | None = None
    error: str


class ImportSummary(BaseModel):
    total_records: int
    successful: int
    failed: int
    errors: list[ImportErrorDetail] = Field(default_factory=list)


class TicketBase(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr
    customer_name: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: TicketCategory = TicketCategory.OTHER
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.NEW
    assigned_to: str | None = Field(default=None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator(
        "customer_id",
        "customer_name",
        "subject",
        "description",
        "assigned_to",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for tag in value:
            clean_tag = tag.strip().lower()
            if clean_tag and clean_tag not in seen:
                normalized.append(clean_tag)
                seen.add(clean_tag)

        return normalized


class TicketCreate(TicketBase):
    auto_classify: bool = False


class TicketUpdate(BaseModel):
    customer_id: str | None = Field(default=None, min_length=1, max_length=100)
    customer_email: EmailStr | None = None
    customer_name: str | None = Field(default=None, min_length=1, max_length=100)
    subject: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None
    metadata: TicketMetadata | None = None

    model_config = ConfigDict(use_enum_values=True)

    @field_validator(
        "customer_id",
        "customer_name",
        "subject",
        "description",
        "assigned_to",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()

        for tag in value:
            clean_tag = tag.strip().lower()
            if clean_tag and clean_tag not in seen:
                normalized.append(clean_tag)
                seen.add(clean_tag)

        return normalized


class TicketClassificationUpdate(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    classification_confidence: float = Field(ge=0, le=1)
    classification_reasoning: str = Field(min_length=1, max_length=1000)
    classification_keywords: list[str] = Field(default_factory=list)
    classification_overridden: bool = False

    model_config = ConfigDict(use_enum_values=True)


class Ticket(TicketBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    resolved_at: datetime | None = None
    classification_confidence: float | None = Field(default=None, ge=0, le=1)
    classification_reasoning: str | None = Field(default=None, max_length=1000)
    classification_keywords: list[str] = Field(default_factory=list)
    classification_overridden: bool = False

    @model_validator(mode="after")
    def set_resolved_at_for_resolved_status(self) -> "Ticket":
        if self.status in {TicketStatus.RESOLVED, TicketStatus.CLOSED} and self.resolved_at is None:
            self.resolved_at = utc_now()

        if self.status not in {TicketStatus.RESOLVED, TicketStatus.CLOSED}:
            self.resolved_at = None

        return self

    def apply_update(self, update: TicketUpdate) -> "Ticket":
        update_data = update.model_dump(exclude_unset=True)
        current_data = self.model_dump()
        classification_changed = (
            ("category" in update_data and update_data["category"] != self.category)
            or ("priority" in update_data and update_data["priority"] != self.priority)
        )
        current_data.update(update_data)
        if classification_changed:
            current_data["classification_overridden"] = True
        current_data["updated_at"] = utc_now()
        return Ticket.model_validate(current_data)

    def apply_classification(self, update: TicketClassificationUpdate) -> "Ticket":
        current_data = self.model_dump()
        current_data.update(update.model_dump())
        current_data["updated_at"] = utc_now()
        return Ticket.model_validate(current_data)
