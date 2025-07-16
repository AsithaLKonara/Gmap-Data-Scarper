# 📚 LeadTap Documentation

Welcome to the LeadTap documentation site! Here you'll find guides, API references, and support resources for using and integrating LeadTap.

## Structure

- `getting-started/` — Quick start, onboarding, first job, CRM setup
- `features/` — Google Maps scraping, CRM management, lead collection, WhatsApp automation
- `api/` — Authentication, endpoints, webhooks, integrations
- `support/` — FAQ, troubleshooting, contact

## How to Extend
- Add new markdown files to the relevant subdirectory.
- Use clear headings and code examples.
- Keep API docs in sync with backend OpenAPI docs.

## Example
```
docs/
├── getting-started/
│   ├── quick-start.md
│   ├── first-job.md
│   └── crm-setup.md
├── features/
│   ├── google-maps-scraping.md
│   ├── crm-management.md
│   ├── lead-collection.md
│   └── whatsapp-automation.md
├── api/
│   ├── authentication.md
│   ├── endpoints.md
│   └── webhooks.md
├── support/
│   ├── faq.md
│   └── contact.md
└── README.md
```

## Webhook API Documentation

### Supported Events
- `job.completed`: Triggered when a scraping job is completed.
- `lead.created`: Triggered when a new lead is created in the CRM.

### Example Payloads

#### job.completed
```json
{
  "job_id": 123,
  "status": "completed",
  "user_id": 42,
  "queries": "[\"pizza in New York\",\"coffee in LA\"]",
  "completed_at": "2024-05-01T12:34:56.789Z"
}
```

#### lead.created
```json
{
  "lead_id": 456,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+1-555-1234",
  "company": "Acme Inc.",
  "website": "https://acme.com",
  "address": "123 Main St, NY",
  "source": "manual",
  "status": "new",
  "user_id": 42,
  "created_at": "2024-05-01T13:00:00.000Z"
}
```

### Security: Webhook Signing
- If you set a `secret` when creating a webhook, each POST will include an `X-Webhook-Signature` header.
- The signature is an HMAC SHA256 of the raw JSON body, using your secret as the key.
- Example (Python):
```python
import hmac, hashlib, json
body = json.dumps(payload).encode()
signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
```
- Always verify the signature before processing the webhook.

### Example: Test with curl
```bash
curl -X POST https://yourapp.com/webhook \
  -H 'Content-Type: application/json' \
  -H 'X-Webhook-Signature: <signature>' \
  -d '{"job_id":123,"status":"completed",...}'
```

### Example: Zapier Integration
- Use the "Webhooks by Zapier" trigger.
- Set the event type in the Zap filter to `job.completed` or `lead.created`.
- Parse the JSON payload as needed.

### Example: Postman
- Import a POST request to your webhook URL.
- Set headers and body as above.
- Use the "Pre-request Script" to generate a signature if needed.

---
For more details, see the `/api/webhooks` endpoints in the API docs.

---

For more, see the [DEPLOYMENT.md](../DEPLOYMENT.md) and in-app Knowledge Base. 

## Referral Program

### How It Works
- Invite friends to LeadTap using your unique referral code or link (found on your Profile page).
- When a friend signs up and applies your code, both of you receive rewards (e.g., bonus leads, credits).
- You can track the status of your referrals in your Profile.

### How to Share
- Copy your referral code or link from the Profile page.
- Share it via email, social media, or direct message.
- Example referral link: `https://your-leadtap-domain.com/register?ref=ABCD1234`

### How to Apply a Code
- On the Profile page, enter a referral code in the "Apply Code" field and submit.
- If valid and unused, rewards are granted to both users.

### Rewards
- Typical rewards: +50 leads, +100 credits (subject to change).
- Rewards are shown in your Profile under "Your Referrals".

### FAQ
- **Can I use my own code?** No, you cannot use your own referral code.
- **How many friends can I refer?** Unlimited! The more you refer, the more you earn.
- **Where do I see my rewards?** In your Profile, under the Referral Program section.
- **What if my code is already used?** Each code can only be used once per friend.

For more details, visit your Profile page or contact support. 

## Affiliate Program

### How It Works
- Join the affiliate program from your Settings or Affiliate Portal page.
- Share your unique affiliate code or link with others (found in the Affiliate Portal).
- When someone signs up and makes a paid purchase using your link/code, you earn a commission (e.g., $20 per paid conversion).
- Track your earnings and commissions in the Affiliate Portal.
- Request payouts once you reach the minimum threshold (admin review required).

### How to Share
- Copy your affiliate code or link from the Affiliate Portal.
- Share it via email, social media, or your website/blog.
- Example affiliate link: `https://your-leadtap-domain.com/register?aff=ABCD1234`

### Commissions & Payouts
- Earn a fixed commission (e.g., $20) for each paid signup via your link/code.
- Commissions are tracked and shown in your Affiliate Portal.
- Request a payout from the portal; payouts are processed after admin review.

### FAQ
- **How do I join?** Go to Settings → Affiliate Portal and generate your code.
- **How do I get paid?** Request a payout in the portal; payouts are processed monthly.
- **Is there a minimum payout?** Yes, see the portal for the current threshold.
- **Can I refer myself?** No, self-referrals are not allowed.
- **Where do I see my stats?** All stats and commissions are in the Affiliate Portal.

For more details, visit your Affiliate Portal or contact support. 