# API Reference

Audience: API consumers integrating with the ticket service.

Base URL:

```text
http://127.0.0.1:8000
```

## Health

### GET /health

Returns service status.

Response:

```json
{
  "status": "ok"
}
```

cURL:

```bash
curl http://127.0.0.1:8000/health
```

## Data Models

### Ticket

```json
{
  "id": "UUID",
  "customer_id": "string",
  "customer_email": "customer@example.com",
  "customer_name": "string",
  "subject": "string, 1-200 characters",
  "description": "string, 10-2000 characters",
  "category": "account_access | technical_issue | billing_question | feature_request | bug_report | other",
  "priority": "urgent | high | medium | low",
  "status": "new | in_progress | waiting_customer | resolved | closed",
  "created_at": "datetime",
  "updated_at": "datetime",
  "resolved_at": "datetime or null",
  "assigned_to": "string or null",
  "tags": ["string"],
  "metadata": {
    "source": "web_form | email | api | chat | phone",
    "browser": "string or null",
    "device_type": "desktop | mobile | tablet or null"
  },
  "classification_confidence": 0.85,
  "classification_reasoning": "string or null",
  "classification_keywords": ["string"],
  "classification_overridden": false
}
```

### Classification Result

```json
{
  "category": "account_access",
  "priority": "urgent",
  "confidence": 0.85,
  "reasoning": "Classified as account_access with urgent priority based on keywords: cannot access.",
  "keywords_found": ["cannot access"]
}
```

### Import Summary

```json
{
  "total_records": 2,
  "successful": 1,
  "failed": 1,
  "errors": [
    {
      "record": 2,
      "error": "value is not a valid email address"
    }
  ]
}
```

## Endpoints

### POST /tickets

Creates a ticket. Set `auto_classify` to `true` to run classification during creation.

Request:

```json
{
  "customer_id": "cust-001",
  "customer_email": "customer@example.com",
  "customer_name": "Ada Lovelace",
  "subject": "Cannot access account",
  "description": "I cannot access my account after password reset.",
  "category": "other",
  "priority": "medium",
  "status": "new",
  "assigned_to": null,
  "tags": ["login"],
  "metadata": {
    "source": "web_form",
    "browser": "Chrome",
    "device_type": "desktop"
  },
  "auto_classify": true
}
```

Success: `201 Created`

cURL:

```bash
curl -X POST http://127.0.0.1:8000/tickets \
  -H "Content-Type: application/json" \
  -d "{\"customer_id\":\"cust-001\",\"customer_email\":\"customer@example.com\",\"customer_name\":\"Ada Lovelace\",\"subject\":\"Cannot access account\",\"description\":\"I cannot access my account after password reset.\",\"auto_classify\":true}"
```

### GET /tickets

Lists tickets. Optional filters: `category`, `priority`, `status`.

Success: `200 OK`

cURL:

```bash
curl "http://127.0.0.1:8000/tickets?category=account_access&priority=urgent&status=new"
```

### GET /tickets/{ticket_id}

Returns one ticket by UUID.

Success: `200 OK`

cURL:

```bash
curl http://127.0.0.1:8000/tickets/00000000-0000-0000-0000-000000000000
```

### PUT /tickets/{ticket_id}

Updates one ticket. Partial updates are supported.

Request:

```json
{
  "status": "in_progress",
  "assigned_to": "Agent One"
}
```

Success: `200 OK`

cURL:

```bash
curl -X PUT http://127.0.0.1:8000/tickets/TICKET_ID \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"in_progress\",\"assigned_to\":\"Agent One\"}"
```

### DELETE /tickets/{ticket_id}

Deletes one ticket.

Success: `204 No Content`

cURL:

```bash
curl -X DELETE http://127.0.0.1:8000/tickets/TICKET_ID
```

### POST /tickets/import

Imports tickets from CSV, JSON, or XML. Upload the file with form field name `file`.

Success: `200 OK`

cURL:

```bash
curl -X POST http://127.0.0.1:8000/tickets/import \
  -F "file=@sample_data/sample_tickets.csv"
```

### POST /tickets/{ticket_id}/auto-classify

Runs classification for one ticket and stores the result on the ticket.

Success: `200 OK`

cURL:

```bash
curl -X POST http://127.0.0.1:8000/tickets/TICKET_ID/auto-classify
```

### GET /tickets/{ticket_id}/classification-logs

Returns classification decisions stored for one ticket.

Success: `200 OK`

cURL:

```bash
curl http://127.0.0.1:8000/tickets/TICKET_ID/classification-logs
```

## Error Responses

### Validation Error

Status: `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters"
    }
  ]
}
```

### Missing Ticket

Status: `404 Not Found`

```json
{
  "detail": "Ticket not found."
}
```

### Malformed Import File

Status: `400 Bad Request`

```json
{
  "detail": "Malformed JSON file: Expecting property name enclosed in double quotes."
}
```
