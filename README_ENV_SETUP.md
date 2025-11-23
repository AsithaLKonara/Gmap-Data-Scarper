# Environment Variables Setup Guide

This guide explains how to configure all environment variables for the Lead Intelligence Platform.

## Quick Start

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your API keys and configuration.

3. Restart the application.

---

## Required Variables

### Database
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/lead_intelligence
```

### API Configuration
```bash
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

---

## Optional but Recommended

### AI Services
- **OPENAI_API_KEY**: For AI query generation, enrichment, sentiment analysis
- **ANTHROPIC_API_KEY**: Alternative to OpenAI (Claude)

### Payment Processing
- **STRIPE_SECRET_KEY**: For subscription management
- **STRIPE_PUBLISHABLE_KEY**: For frontend checkout
- **STRIPE_WEBHOOK_SECRET**: For webhook verification

### Phone Verification
- **TWILIO_ACCOUNT_SID**: For phone number verification
- **TWILIO_AUTH_TOKEN**: Twilio authentication token

### Business Enrichment
- **CLEARBIT_API_KEY**: For company data enrichment
- **GOOGLE_PLACES_API_KEY**: For location data
- **CRUNCHBASE_API_KEY**: For funding data

---

## Enterprise Features

### SSO (Single Sign-On)
- **SAML_CERT_PATH**: Path to SAML certificate
- **SAML_ISSUER**: SAML issuer URL
- **OAUTH_CLIENT_ID**: OAuth client ID (Google/Microsoft)
- **OAUTH_CLIENT_SECRET**: OAuth client secret

### Email (Scheduled Reports)
- **SMTP_HOST**: SMTP server (e.g., smtp.gmail.com)
- **SMTP_PORT**: SMTP port (usually 587)
- **SMTP_USER**: Email address
- **SMTP_PASSWORD**: Email password or app password

### AWS S3 (Report Storage)
- **AWS_ACCESS_KEY_ID**: AWS access key
- **AWS_SECRET_ACCESS_KEY**: AWS secret key
- **AWS_REGION**: AWS region (e.g., us-east-1)
- **S3_BUCKET**: S3 bucket name for reports

---

## Workflow Integrations

### CRM Integrations
- **HUBSPOT_API_KEY**: HubSpot CRM integration
- **ZOHO_CLIENT_ID**, **ZOHO_CLIENT_SECRET**, **ZOHO_REFRESH_TOKEN**: Zoho CRM
- **PIPEDRIVE_API_TOKEN**: Pipedrive CRM

### Other Integrations
- **TELEGRAM_BOT_TOKEN**: For Telegram notifications
- **SENDGRID_API_KEY**: For email workflows
- **GOOGLE_SHEETS_CREDENTIALS_PATH**: Path to Google service account JSON

---

## Security

- **JWT_SECRET**: Secret key for JWT tokens (change in production!)
- **JWT_ALGORITHM**: Usually HS256
- **JWT_EXPIRATION_HOURS**: Token expiration (default 24)

---

## Feature Flags

Enable/disable features:
- **ENABLE_AI_FEATURES**: Enable AI features (default: true)
- **ENABLE_SSO**: Enable SSO authentication (default: true)
- **ENABLE_WHITE_LABEL**: Enable white-label branding (default: true)
- **ENABLE_SCHEDULED_REPORTS**: Enable scheduled reports (default: true)

---

## Getting API Keys

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy to `OPENAI_API_KEY`

### Stripe
1. Go to https://dashboard.stripe.com/apikeys
2. Copy Secret key to `STRIPE_SECRET_KEY`
3. Copy Publishable key to `STRIPE_PUBLISHABLE_KEY`

### Twilio
1. Go to https://console.twilio.com/
2. Copy Account SID and Auth Token

### Clearbit
1. Go to https://dashboard.clearbit.com/api
2. Generate API key

---

## Testing Configuration

After setting up `.env`, test your configuration:

```bash
# Test database connection
python backend/scripts/create_migrations.py

# Test API
python -m pytest tests/test_new_endpoints.py -v
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET` to a strong random string
- [ ] Set `DEBUG=false`
- [ ] Use production database URL
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup strategy
- [ ] Set up monitoring (Sentry, etc.)

