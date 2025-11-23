# CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment pipelines for the Lead Intelligence Platform.

## Overview

The project uses GitHub Actions for CI/CD automation with the following workflows:

1. **CI Pipeline** - Runs on every push and PR
2. **CD Pipeline** - Deploys to staging/production
3. **E2E Tests** - End-to-end testing with Playwright
4. **Performance Tests** - Performance regression testing
5. **Code Quality** - Code quality and security checks
6. **Dependency Updates** - Automated dependency update checks

## CI Pipeline

**File**: `.github/workflows/ci.yml`

### Jobs

1. **Lint Backend (Python)**
   - Format check with Black
   - Import sorting with isort
   - Linting with Flake8
   - Type checking with MyPy

2. **Lint Frontend (TypeScript/Next.js)**
   - ESLint checks
   - TypeScript type checking

3. **Test Backend (Python)**
   - Unit tests with pytest
   - Coverage reporting
   - Uploads coverage to Codecov

4. **Test Frontend (Jest)**
   - Jest test suite
   - Coverage reporting
   - Uploads coverage to Codecov

5. **Integration Tests**
   - FastAPI + Chrome integration tests
   - PostgreSQL service for database tests

6. **Security Scan**
   - Bandit for Python security
   - npm audit for frontend dependencies

7. **Build Docker**
   - Validates Docker image builds successfully

### Running Locally

```bash
# Backend linting
black --check backend/ extractors/ tests/
isort --check-only backend/ extractors/ tests/
flake8 backend/ extractors/ tests/

# Frontend linting
cd frontend
npm run lint
npx tsc --noEmit

# Backend tests
pytest tests/unit/ -v --cov

# Frontend tests
cd frontend
npm test
```

## CD Pipeline

**File**: `.github/workflows/cd.yml`

### Triggers

- Push to `main` branch → Deploy to staging
- Tag push (`v*`) → Deploy to production
- Manual workflow dispatch

### Jobs

1. **Build and Push Docker Image**
   - Builds Docker image
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with branch, SHA, and semantic version

2. **Deploy to Staging**
   - Runs on pushes to `main`
   - Deploys to staging environment
   - Runs health checks

3. **Deploy to Production**
   - Runs on version tags (`v*`)
   - Requires manual approval (if configured)
   - Deploys to production environment
   - Runs health checks and smoke tests

### Environment Variables

Configure these secrets in GitHub:

- `STAGING_URL` - Staging environment URL
- `PRODUCTION_URL` - Production environment URL
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

## E2E Tests

**File**: `.github/workflows/e2e-tests.yml`

### Features

- Runs Playwright tests
- Starts backend and frontend servers
- Tests complete user workflows
- Uploads test reports and videos on failure
- Runs on schedule (daily at 2 AM UTC)

### Running Locally

```bash
cd frontend
npm run test:e2e
```

## Performance Tests

**File**: `.github/workflows/performance-tests.yml`

### Features

- Runs pytest-benchmark tests
- Load testing with Locust
- Performance regression detection
- Runs weekly (Sundays at 3 AM UTC)

### Running Locally

```bash
# Benchmarks
pytest tests/performance/ -v --benchmark-only

# Load tests
locust -f tests/performance/locustfile.py --headless --users 10 --spawn-rate 2 --run-time 5m
```

## Code Quality

**File**: `.github/workflows/code-quality.yml`

### Checks

- Pylint for Python code quality
- Radon for code complexity analysis
- Code duplication detection
- SonarCloud integration (optional)

## Dependency Updates

**File**: `.github/workflows/dependency-updates.yml`

### Features

- Weekly dependency update checks
- Security vulnerability scanning
- Creates GitHub issues for available updates

## Configuration

### Required Secrets

Configure these in GitHub repository settings:

1. **Codecov** (optional)
   - `CODECOV_TOKEN` - For coverage reporting

2. **SonarCloud** (optional)
   - `SONAR_TOKEN` - For code quality analysis

3. **Deployment** (if using custom deployment)
   - `STAGING_URL` - Staging environment URL
   - `PRODUCTION_URL` - Production environment URL
   - `DEPLOY_KEY` - SSH key for deployment (if needed)

### Environment Configuration

Update environment-specific settings in workflow files:

- Docker image registry
- Deployment commands
- Health check URLs
- Test environment URLs

## Best Practices

1. **Always run tests locally before pushing**
   ```bash
   pytest tests/ -v
   cd frontend && npm test
   ```

2. **Check linting before committing**
   ```bash
   black backend/ extractors/ tests/
   isort backend/ extractors/ tests/
   cd frontend && npm run lint
   ```

3. **Review CI results before merging PRs**
   - All checks must pass
   - Coverage should not decrease
   - No security vulnerabilities

4. **Use semantic versioning for releases**
   - `v1.0.0` for major releases
   - `v1.1.0` for minor releases
   - `v1.1.1` for patch releases

5. **Monitor performance tests**
   - Review weekly performance reports
   - Investigate regressions immediately
   - Set performance budgets

## Troubleshooting

### CI Failures

1. **Linting failures**
   - Run formatters locally: `black .` and `isort .`
   - Fix reported issues

2. **Test failures**
   - Run tests locally to reproduce
   - Check test logs in GitHub Actions

3. **Build failures**
   - Verify Dockerfile is correct
   - Check dependency versions

### CD Failures

1. **Deployment failures**
   - Check environment variables
   - Verify deployment scripts
   - Review deployment logs

2. **Health check failures**
   - Verify services are running
   - Check service URLs
   - Review service logs

## Future Enhancements

- [ ] Add automated rollback on deployment failure
- [ ] Implement canary deployments
- [ ] Add database migration automation
- [ ] Set up monitoring and alerting
- [ ] Add automated security scanning
- [ ] Implement blue-green deployments

