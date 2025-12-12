# Comprehensive QA Test Plan
**Date:** 2025-01-17  
**Perspectives:** QA Tester, Lead Collector User, Admin

---

## Test Categories

### 1. Authentication & Authorization
- [ ] User registration/login
- [ ] JWT token validation
- [ ] Token blacklist/revocation
- [ ] Role-based access control (Admin vs User)
- [ ] WebSocket authentication
- [ ] API endpoint protection

### 2. Lead Collection Workflows (Lead Collector Perspective)
- [ ] Start scraping task
- [ ] View task status
- [ ] Real-time progress updates
- [ ] Lead export (CSV, JSON, Excel)
- [ ] Filter leads
- [ ] View lead details
- [ ] Soft delete leads
- [ ] Restore leads

### 3. Admin Functions
- [ ] Hard delete leads (admin only)
- [ ] Hard delete tasks (admin only)
- [ ] View audit logs
- [ ] User management
- [ ] System health monitoring

### 4. Data Integrity
- [ ] Soft delete filtering (leads not visible after soft delete)
- [ ] Audit trail tracking
- [ ] Created/modified by fields
- [ ] Database migrations
- [ ] Data export accuracy

### 5. Error Handling
- [ ] Invalid input validation
- [ ] Network errors
- [ ] Database errors
- [ ] Authentication failures
- [ ] Rate limiting
- [ ] Timeout handling

### 6. Security
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input sanitization
- [ ] Rate limiting
- [ ] Security headers

### 7. Performance
- [ ] Database query optimization
- [ ] Batch operations
- [ ] Concurrent requests
- [ ] Memory usage
- [ ] Response times

---

## Issues to Check

1. **datetime.utcnow() deprecation** - Replace with datetime.now(timezone.utc)
2. **Soft delete filtering** - Ensure all queries exclude deleted records
3. **Admin access checks** - Verify all admin endpoints are protected
4. **Error handling** - Ensure proper error messages and logging
5. **Input validation** - Check all endpoints validate input
6. **Audit trail** - Verify all mutations are logged
7. **Database sessions** - Ensure proper session management


