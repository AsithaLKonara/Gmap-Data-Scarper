# Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the Lead Intelligence Platform.

## Test Structure

```
tests/
├── backend/          # Backend WebSocket tests
├── classification/   # Business/job classification tests
├── cli/              # CLI command tests
├── config/           # Test configuration
├── data_validation/  # Data validation tests
├── e2e/              # End-to-end tests
├── enrichment/       # Enrichment service tests
├── error_handling/   # Error handling tests
├── extractors/       # Phone extraction tests
├── fixtures/         # Test data fixtures
├── integration/      # Integration tests
├── intelligence/     # Lead intelligence tests
├── legal/            # GDPR compliance tests
├── normalize/        # Phone normalization tests
├── ocr/              # OCR tests
├── performance/      # Performance and load tests
├── phone/            # Phone extraction tests
├── platform/         # Platform scraper tests
├── security/         # Security tests
└── unit/             # Unit tests
```

## Running Tests

### All Tests
```bash
python run_tests_local.py
```

### Specific Test Categories
```bash
# Backend tests only
pytest tests/backend/ -v

# Integration tests
pytest tests/integration/ -v

# Security tests
pytest tests/security/ -v

# GDPR compliance tests
pytest tests/legal/ -v

# Frontend tests
cd frontend && npm test
```

### With Coverage
```bash
pytest tests/ --cov=backend --cov-report=html
```

## Test Configuration

Test environment variables are configured in `tests/config/test_config.py`.

Key environment variables:
- `TESTING=true` - Enables test mode (bypasses rate limiting, etc.)
- `TEST_DATABASE_URL` - Test database connection string
- `API_URL` - Backend API URL for integration tests
- `DISABLE_RATE_LIMIT=true` - Disables rate limiting in tests

## Test Fixtures

Test data fixtures are available in `tests/fixtures/test_data.py`:
- `TEST_USERS` - Sample user accounts
- `SAMPLE_LEADS` - Sample lead data
- `SAMPLE_TASKS` - Sample task data
- `TEST_API_KEYS` - Test API keys (not real)

## CI/CD Integration

Tests run automatically on push/PR via GitHub Actions (`.github/workflows/test.yml`).

## Test Coverage Goals

- Overall: 80%+
- Critical paths: 90%+
- Security tests: 100% of critical security features
- GDPR compliance: 100% of GDPR endpoints
