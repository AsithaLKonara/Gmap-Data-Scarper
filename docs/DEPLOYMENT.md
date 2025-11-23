# Deployment Guide
## Lead Intelligence Platform - Production Deployment

This guide covers deploying the Lead Intelligence Platform to production.

---

## Prerequisites

- Server with Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose (optional, for containerized deployment)
- PostgreSQL 12+ database
- Redis server
- Nginx (for reverse proxy)
- SSL certificate (Let's Encrypt recommended)
- Domain name configured

---

## 1. Server Setup

### 1.1 System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB disk space

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD disk space

### 1.2 Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+
sudo apt install python3.9 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx
sudo apt install nginx -y

# Install Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 1.3 Create Application User

```bash
sudo useradd -m -s /bin/bash leadintel
sudo su - leadintel
```

---

## 2. Application Deployment

### 2.1 Clone Repository

```bash
cd /home/leadintel
git clone <your-repo-url> lead-intelligence-platform
cd lead-intelligence-platform
```

### 2.2 Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate VAPID keys
python scripts/generate_vapid_keys.py

# Initialize database
python scripts/init_database.py
```

### 2.3 Frontend Setup

```bash
cd frontend
npm install
npm run build
cd ..
```

### 2.4 Environment Configuration

Create `/home/leadintel/lead-intelligence-platform/.env`:

```env
# Database
DATABASE_URL=postgresql://leadintel:secure_password@localhost:5432/lead_intelligence

# VAPID Keys
VAPID_PRIVATE_KEY=your_private_key
VAPID_PUBLIC_KEY=your_public_key
VAPID_EMAIL=admin@yourdomain.com

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# External Services (optional)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
OPENAI_API_KEY=your_openai_key
```

Create `frontend/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_vapid_public_key_base64
```

---

## 3. Database Setup

### 3.1 Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE lead_intelligence;
CREATE USER leadintel WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE lead_intelligence TO leadintel;
\q
```

### 3.2 Initialize Database

```bash
cd /home/leadintel/lead-intelligence-platform
source venv/bin/activate
python scripts/init_database.py
```

---

## 4. Systemd Services

### 4.1 Backend Service

Create `/etc/systemd/system/lead-intelligence-api.service`:

```ini
[Unit]
Description=Lead Intelligence Platform API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=leadintel
WorkingDirectory=/home/leadintel/lead-intelligence-platform
Environment="PATH=/home/leadintel/lead-intelligence-platform/venv/bin"
ExecStart=/home/leadintel/lead-intelligence-platform/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.2 Celery Worker Service

Create `/etc/systemd/system/lead-intelligence-celery.service`:

```ini
[Unit]
Description=Lead Intelligence Platform Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=leadintel
WorkingDirectory=/home/leadintel/lead-intelligence-platform
Environment="PATH=/home/leadintel/lead-intelligence-platform/venv/bin"
ExecStart=/home/leadintel/lead-intelligence-platform/venv/bin/celery -A backend.celery_app worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.3 Celery Beat Service

Create `/etc/systemd/system/lead-intelligence-celery-beat.service`:

```ini
[Unit]
Description=Lead Intelligence Platform Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=leadintel
WorkingDirectory=/home/leadintel/lead-intelligence-platform
Environment="PATH=/home/leadintel/lead-intelligence-platform/venv/bin"
ExecStart=/home/leadintel/lead-intelligence-platform/venv/bin/celery -A backend.celery_app beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.4 Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable lead-intelligence-api
sudo systemctl enable lead-intelligence-celery
sudo systemctl enable lead-intelligence-celery-beat
sudo systemctl start lead-intelligence-api
sudo systemctl start lead-intelligence-celery
sudo systemctl start lead-intelligence-celery-beat
```

Check status:
```bash
sudo systemctl status lead-intelligence-api
```

---

## 5. Nginx Configuration

### 5.1 API Reverse Proxy

Create `/etc/nginx/sites-available/lead-intelligence-api`:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 5.2 Frontend Configuration

Create `/etc/nginx/sites-available/lead-intelligence-frontend`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /home/leadintel/lead-intelligence-platform/frontend/out;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_next/static {
        alias /home/leadintel/lead-intelligence-platform/frontend/.next/static;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5.3 Enable Sites

```bash
sudo ln -s /etc/nginx/sites-available/lead-intelligence-api /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/lead-intelligence-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

Certbot will automatically configure Nginx for HTTPS.

---

## 7. Monitoring & Logging

### 7.1 Log Locations

- Backend logs: `/var/log/lead-intelligence-api.log` (if configured)
- Systemd logs: `sudo journalctl -u lead-intelligence-api -f`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### 7.2 Health Checks

```bash
# API health
curl https://api.yourdomain.com/api/health

# Database connection
sudo -u postgres psql -d lead_intelligence -c "SELECT COUNT(*) FROM leads;"
```

---

## 8. Backup Strategy

### 8.1 Database Backup

Create `/home/leadintel/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/leadintel/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U leadintel lead_intelligence > $BACKUP_DIR/db_backup_$DATE.sql
# Keep only last 7 days
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
```

Make executable:
```bash
chmod +x /home/leadintel/backup-db.sh
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /home/leadintel/backup-db.sh
```

---

## 9. Updates & Maintenance

### 9.1 Update Application

```bash
cd /home/leadintel/lead-intelligence-platform
git pull
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
sudo systemctl restart lead-intelligence-api
sudo systemctl restart lead-intelligence-celery
sudo systemctl restart lead-intelligence-celery-beat
```

### 9.2 Database Migrations

```bash
python scripts/init_database.py
```

---

## 10. Security Checklist

- [ ] Firewall configured (UFW recommended)
- [ ] SSH key authentication only
- [ ] Database password is strong
- [ ] VAPID keys are secure
- [ ] SSL certificates are valid
- [ ] CORS origins are restricted
- [ ] Rate limiting is enabled
- [ ] Secrets are in `.env` (not committed)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`

---

## 11. Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u lead-intelligence-api -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

### Database Connection Issues

```bash
# Test connection
psql -U leadintel -d lead_intelligence -c "SELECT 1;"

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Frontend Build Issues

```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

---

## Support

For deployment issues, check:
- System logs: `sudo journalctl -xe`
- Application logs: Check service status
- Nginx logs: `/var/log/nginx/error.log`


