# LeadTap API Usage & Code Examples

This guide provides practical examples for using the LeadTap API. For the full OpenAPI/Swagger docs, visit `/docs` or `/redoc` on your deployment.

---

## Authentication (Login)

**Endpoint:** `POST /api/auth/login`

**Request (JSON):**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Curl:**
```bash
curl -X POST https://your-leadtap-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

**Response (JSON):**
```json
{
  "access_token": "...jwt...",
  "token_type": "bearer"
}
```

---

## Create a Job

**Endpoint:** `POST /api/scrape/jobs`

**Request (JSON):**
```json
{
  "queries": ["coffee shops in New York", "bookstores in San Francisco"]
}
```

**Curl:**
```bash
curl -X POST https://your-leadtap-domain.com/api/scrape/jobs \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"queries": ["coffee shops in New York", "bookstores in San Francisco"]}'
```

**Response (JSON):**
```json
{
  "job_id": 123,
  "status": "pending"
}
```

---

## Get Job Results

**Endpoint:** `GET /api/scrape/jobs/{job_id}/results`

**Curl:**
```bash
curl -X GET https://your-leadtap-domain.com/api/scrape/jobs/123/results \
  -H "Authorization: Bearer <your_token>"
```

**Response (JSON):**
```json
{
  "result": [
    {"name": "Cafe One", "address": "123 Main St", "phone": "555-1234"},
    {"name": "Book Haven", "address": "456 Elm St", "phone": "555-5678"}
  ]
}
```

---

## Add a Lead to CRM

**Endpoint:** `POST /api/crm/leads`

**Request (JSON):**
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "phone": "+1234567890",
  "company": "Acme Inc.",
  "website": "https://acme.com"
}
```

**Curl:**
```bash
curl -X POST https://your-leadtap-domain.com/api/crm/leads \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Smith", "email": "alice@example.com", "phone": "+1234567890", "company": "Acme Inc.", "website": "https://acme.com"}'
```

**Response (JSON):**
```json
{
  "id": 456,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "company": "Acme Inc.",
  "status": "new"
}
```

---

## Webhook Setup & Test

**Get Webhook URL:**

```bash
curl -X GET https://your-leadtap-domain.com/api/webhooks \
  -H "Authorization: Bearer <your_token>"
```

**Response:**
```json
{
  "url": "https://your-leadtap-domain.com/webhook/abc123"
}
```

**Test Webhook (send event):**

```bash
curl -X POST https://your-leadtap-domain.com/api/webhooks/test \
  -H "Authorization: Bearer <your_token>"
```

---

## Using LeadTap with Zapier

You can connect LeadTap to Zapier using webhooks to automate workflows with thousands of apps.

### Step 1: Create a Webhook in LeadTap
- Go to the Integrations page in your dashboard.
- Copy your unique webhook URL (or create one if needed).
- Choose the event(s) you want to trigger (e.g., `lead.created`, `job.completed`).

### Step 2: Set Up a Zap in Zapier
- In Zapier, create a new Zap.
- For the trigger, search for and select "Webhooks by Zapier".
- Choose "Catch Hook" as the trigger event.
- Paste your LeadTap webhook URL into the Zapier setup.
- Test the trigger by clicking "Test Webhook" in LeadTap.
- Continue building your Zap with any action (e.g., add to Google Sheets, send Slack message).

### Supported Events
- `lead.created` – New lead added
- `job.completed` – Job finished
- `lead.updated` – Lead updated
- `lead.deleted` – Lead deleted

### Example Payload
```json
{
  "event": "lead.created",
  "lead_id": 123,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "company": "Acme Inc.",
  "status": "new",
  "created_at": "2024-06-01T12:34:56Z"
}
```

### Security
- Webhook payloads can be signed with a secret. See the Integrations page for details.

For more details, see the Integrations page in your dashboard or contact support.

---

## Python Example: Create a Job

```