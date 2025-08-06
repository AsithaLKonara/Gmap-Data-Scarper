# 🏺️ Gmap Lead Scraper - LeadTap Platform

A powerful and customizable web scraping tool built in Python to collect business leads from Google Maps. It extracts essential business information for multiple search queries and saves the data into a CSV file for use in outreach, research, or lead generation.

---

## 📚 **Documentation & Resources**

### 📄 **Complete Documentation**
- **[ALL_DOCUMENTATION.md](./ALL_DOCUMENTATION.md)** - Complete consolidated documentation (all project docs in one place)
- **[CONSOLIDATED_DEPLOYMENT_GUIDE.md](./CONSOLIDATED_DEPLOYMENT_GUIDE.md)** - Comprehensive deployment guide
- **[CONSOLIDATION_SUMMARY.md](./CONSOLIDATION_SUMMARY.md)** - Summary of file consolidation

### 🐳 **Docker Configuration**
- **[CONSOLIDATED_DOCKER_COMPOSE.yml](./CONSOLIDATED_DOCKER_COMPOSE.yml)** - Complete Docker Compose configuration
- **[CONSOLIDATED_DOCKERFILE](./CONSOLIDATED_DOCKERFILE)** - Multi-stage Dockerfile for all scenarios

---

## ✨ **Features**

* 🔍 Automates Google Maps searches
* 📅 Extracts multiple leads per query
* 📌 Captures:
  * Business Name
  * Category
  * Address
  * Phone Number
  * Website
  * Plus Code
* 📄 Saves data to CSV in `~/Documents`
* 💻 Works on Mac and cross-platform
* 🧠 Handles both multi-result lists and single business pages
* 🔁 Retries failed attempts automatically
* 🏢 **Multi-tenant SaaS platform**
* 🔐 **JWT Authentication & SSO**
* 📊 **Advanced Analytics & Lead Scoring**
* 🤖 **AI-powered lead management**

---

## 🚀 **Quick Start**

### **Option 1: Docker (Recommended)**
```bash
# Clone the repository
git clone https://github.com/your-repo/gmap-data-scraper.git
cd gmap-data-scraper

# Start development environment
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile development up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Option 2: Local Development**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Run the scraper
python3 app.py
```

---

## 🎯 **Deployment Scenarios**

### **Development Environment**
```bash
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile development up -d
```
- Hot reload for both frontend and backend
- SQLite database for simplicity
- Development debugging enabled

### **Simple Production**
```bash
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile simple up -d
```
- Optimized for production
- SQLite database (suitable for small to medium workloads)
- Fast startup time

### **Full Production**
```bash
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml --profile production up -d
```
- PostgreSQL database for scalability
- Redis caching for performance
- Nginx reverse proxy with SSL
- Prometheus monitoring
- Grafana dashboards

### **Backend Only**
```bash
docker-compose -f CONSOLIDATED_DOCKER_COMPOSE.yml up backend sqlite-db -d
```
- Minimal resource usage
- API-only access
- Suitable for microservices architecture

---

## 📁 **Project Structure**

```
gmap-data-scraper/
├── 📄 ALL_DOCUMENTATION.md              # Complete documentation
├── 📄 CONSOLIDATED_DEPLOYMENT_GUIDE.md  # Deployment guide
├── 📄 CONSOLIDATION_SUMMARY.md          # Consolidation summary
├── 🐳 CONSOLIDATED_DOCKER_COMPOSE.yml   # Docker Compose config
├── 🐳 CONSOLIDATED_DOCKERFILE           # Multi-stage Dockerfile
├── 📁 backend/                          # Python FastAPI backend
├── 📁 frontend/                         # React TypeScript frontend
├── 📁 docs/                             # Additional documentation
├── 📁 backup/old-files/                 # Archived original files
├── app.py                               # Original scraper script
├── search_queries.txt                   # Search terms input
└── gmap_all_leads.csv                   # Output file
```

---

## 🧰 **Requirements**

* Python 3.8 or higher
* Google Chrome browser (latest)
* ChromeDriver (managed automatically)
* Docker and Docker Compose (for containerized deployment)

---

## 📖 **Documentation Sections**

The complete documentation includes:

1. **Project Overview** - Features, architecture, and capabilities
2. **Production Status** - Current deployment readiness
3. **Implementation Status** - Development progress and features
4. **API Documentation** - Complete API reference and examples
5. **Deployment Guide** - Step-by-step deployment instructions
6. **User Navigation Flow** - User journey and interface guide
7. **Security & Audit** - Security considerations and audit reports
8. **Roadmap & Planning** - Future development plans
9. **Troubleshooting** - Common issues and solutions
10. **Monitoring & Analytics** - Performance monitoring and metrics

---

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file for configuration:
```bash
# Core configuration
ENVIRONMENT=development
DEBUG=true
DEPLOYMENT_TYPE=development

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET=your-jwt-secret

# Database
DATABASE_URL=sqlite:///./leadtap.db

# Frontend
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### **Search Queries**
Create `search_queries.txt` with your search terms:
```
restaurant in Nuwara Eliya
auto parts shop in Badulla
furniture shop in Polonnaruwa
salon in Anuradhapura
```

---

## 📊 **Output Format**

CSV columns:
* Search Query
* Business Name
* Category
* Address
* Phone
* Website
* Plus Code

Example row:
```
restaurant in Nuwara Eliya,Green Hills Restaurant,Restaurant,No.10 Gregory Road,+94 77 123 4567,www.greenhills.lk,PX9W+V3 Nuwara Eliya
```

---

## 🏗️ **Architecture**

### **Backend (FastAPI)**
- **Port:** 8000
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** JWT + bcrypt
- **Multi-tenancy:** Fully implemented
- **Modules:** 30+ integrated modules

### **Frontend (React + TypeScript)**
- **Port:** 3000
- **Framework:** React + Vite
- **UI:** Modern, responsive design
- **Components:** 50+ reusable components
- **Real-time:** WebSocket ready

### **Database**
- **Development:** SQLite
- **Production:** PostgreSQL 15
- **Caching:** Redis (production)
- **Migrations:** Alembic

---

## 🔒 **Security Features**

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Password Hashing** - bcrypt encryption
- ✅ **Multi-tenancy** - Data isolation by organization
- ✅ **SSO/SAML Support** - Enterprise authentication
- ✅ **CORS Protection** - Cross-origin security
- ✅ **Input Validation** - Pydantic models
- ✅ **SQL Injection Protection** - Parameterized queries

---

## 📈 **Monitoring & Analytics**

### **Health Checks**
- Backend: `http://localhost:8000/api/health`
- Frontend: `http://localhost:3000/`
- Database: Automatic health checks
- Redis: Automatic health checks

### **Production Monitoring**
- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3001`
- **Logs:** Structured logging
- **Metrics:** Performance tracking

---

## 🆘 **Support & Troubleshooting**

### **Quick Help**
1. Check **[CONSOLIDATED_DEPLOYMENT_GUIDE.md](./CONSOLIDATED_DEPLOYMENT_GUIDE.md)** for deployment issues
2. Review **[ALL_DOCUMENTATION.md](./ALL_DOCUMENTATION.md)** for comprehensive information
3. Check Docker logs: `docker-compose logs -f`
4. Verify health checks: `docker-compose ps`

### **Common Issues**
- **Port conflicts:** Check if ports 8000, 3000, 80, 443 are available
- **Database issues:** Restart database container
- **Build errors:** Rebuild Docker images
- **Memory issues:** Increase Docker memory limit

---

## 👨‍💻 **Author**

**Asitha L Konara**

---

## ⚠️ **Disclaimer**

This tool is intended for personal or educational use. Please use responsibly and in accordance with Google Maps' terms of service.

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated:** $(date)  
**Status:** ✅ Production Ready  
**Version:** 1.0.0 