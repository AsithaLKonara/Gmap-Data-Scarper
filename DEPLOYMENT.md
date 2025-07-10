# 🚀 LeadTap Deployment Guide

## 1. Prerequisites
- Docker & Docker Compose installed
- MySQL 8+ (or use Docker service)
- Node.js 18+ (for local frontend builds)
- Python 3.10+ (for local backend builds)
- GitHub repository (for CI/CD)

## 2. Environment Variables
Create a `.env` file in the project root with:
```
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=leadtap
MYSQL_USER=leadtap
MYSQL_PASSWORD=leadtap
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FRONTEND_URL=https://your-frontend-url
DATABASE_URL=mysql+pymysql://leadtap:leadtap@db/leadtap
ENVIRONMENT=production
SENTRY_DSN=your-sentry-dsn (optional)
```

## 3. Docker Compose (Production)
```
docker-compose up -d --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- MySQL: localhost:3306

## 4. Health Checks
- API: `GET /api/health` (returns `{ status: healthy }`)
- System: `GET /api/system/health` (system metrics)
- Docker Compose healthchecks are built-in

## 5. CI/CD (GitHub Actions)
- See `.github/workflows/ci-cd.yml` for build, test, lint, and deploy steps
- Customize the deploy step for your cloud/host

## 6. Monitoring & Error Tracking
- Sentry integration: set `SENTRY_DSN` in `.env` for backend error tracking
- System metrics: use `/api/system/health` and `/api/system/logs`
- Logs: Docker logs, FastAPI logs, and Sentry

## 7. Database Backups
- MySQL data is stored in the `db_data` Docker volume
- Use `docker exec leadtap-db mysqldump -u root -p$MYSQL_ROOT_PASSWORD leadtap > backup.sql` to backup

## 8. Updating & Scaling
- Pull latest code: `git pull`
- Rebuild: `docker-compose up -d --build`
- For scaling, use a reverse proxy (NGINX, Traefik) and load balancer

## 9. Security Best Practices
- Use strong secrets in `.env`
- Restrict database/network access in production
- Enable HTTPS/SSL for frontend/backend
- Monitor Sentry and system logs for errors

## 10. Troubleshooting
- Check container logs: `docker-compose logs backend` / `frontend` / `db`
- Check health endpoints for status
- For issues, see logs and Sentry dashboard

---

**LeadTap is now ready for production deployment!** 