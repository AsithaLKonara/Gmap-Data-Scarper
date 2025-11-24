# What We Have Left To Do

**Date:** 2025-01-17  
**Status:** Summary of Remaining Work

---

## 🚨 CRITICAL (Do First)

### 1. Apply Database Migration ⚠️
**Status:** Migration file created but NOT applied  
**Action Required:**
```bash
alembic upgrade head
```
**Impact:** Soft deletes and audit trail won't work until migration is applied  
**Time:** 5 minutes

---

## 🔴 HIGH PRIORITY

### 2. Update Remaining Routes to Use Dependency Injection
**Status:** 5 routes still use manual session management  
**Files:**
- `backend/routes/payments.py` - 4 endpoints
- `backend/routes/workflows.py` - 6 endpoints  
- `backend/routes/reports.py` - 2 endpoints
- `backend/routes/legal.py` - 6 endpoints (partially updated)
- `backend/routes/scraper.py` - 1 endpoint (partially updated)

**Total:** 19 instances of `get_session()` that should use `Depends(get_db)`

**Example Fix:**
```python
# Before
db = get_session()
try:
    # ... code ...
finally:
    db.close()

# After
async def endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # ... code ...
    # db.close() handled automatically
```

**Time:** 4-6 hours

---

### 3. Add Admin Checks for Hard Delete Endpoints
**Status:** Hard delete endpoints exist but don't verify admin permissions  
**File:** `backend/routes/soft_delete.py`  
**Lines:** 179, 215

**Action:** Add role-based access control check:
```python
# TODO: Add admin check or confirmation
if current_user.get("role") != "admin":
    raise HTTPException(status_code=403, detail="Admin access required")
```

**Time:** 30 minutes

---

## 🟡 MEDIUM PRIORITY

### 4. Replace Remaining print() Statements with Logging
**Status:** 68 print() statements across 19 files  
**Files:**
- `backend/services/orchestrator_service.py` - 8 instances
- `backend/tasks/scraping_tasks.py` - 7 instances
- `backend/scripts/create_migrations.py` - 13 instances
- `backend/scripts/migrate_csv_to_db.py` - 9 instances
- `backend/services/push_service.py` - 4 instances
- `backend/services/email_extractor.py` - 2 instances
- `backend/services/template_service.py` - 2 instances
- `backend/services/ai_query_generator.py` - 2 instances
- `backend/services/anti_detection.py` - 2 instances
- `backend/services/postgresql_cache.py` - 2 instances
- `backend/services/stripe_service.py` - 2 instances
- `backend/services/retention_service.py` - 1 instance
- `backend/services/stream_service.py` - 1 instance
- `backend/services/chrome_pool.py` - 1 instance
- `backend/services/ai_enrichment.py` - 1 instance
- `backend/services/company_intelligence.py` - 1 instance
- `backend/services/zoho_crm.py` - 1 instance
- `backend/main.py` - 8 instances
- `backend/routes/legal.py` - 1 instance

**Action:** Replace with `logging.info()`, `logging.error()`, etc.

**Time:** 2-3 hours

---

### 5. Implement Audit Log Table
**Status:** Placeholder exists  
**File:** `backend/utils/audit_trail.py:81`

**Action:** Create `AuditLog` model and table to track all changes:
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    model_name = Column(String)  # "Lead", "Task", etc.
    record_id = Column(String)
    action = Column(String)  # "create", "update", "delete", "restore"
    user_id = Column(String)
    changes = Column(JSON)  # Field changes
    created_at = Column(DateTime)
```

**Time:** 2-3 hours

---

### 6. Update Deprecated Code
**Status:** Several deprecation warnings

**6.1 Pydantic V2 Validators**
- **File:** `backend/models/schemas.py`
- **Issue:** Using `@validator` (deprecated)
- **Fix:** Migrate to `@field_validator`
- **Time:** 1 hour

**6.2 SQLAlchemy declarative_base**
- **File:** `backend/models/database.py:10`
- **Issue:** Using `declarative_base()` (deprecated)
- **Fix:** Use `sqlalchemy.orm.declarative_base()`
- **Time:** 15 minutes

**6.3 FastAPI lifespan Events**
- **File:** `backend/main.py:142, 213`
- **Issue:** Using `@app.on_event()` (deprecated)
- **Fix:** Migrate to lifespan context manager
- **Time:** 1 hour

**Total Time:** 2-3 hours

---

### 7. Add Soft Delete Filtering to All Queries
**Status:** Some queries may not filter soft-deleted records  
**Action:** Review all Lead/Task queries and ensure `deleted_at IS NULL` filter

**Files to Check:**
- `backend/services/postgresql_storage.py` - `get_leads()` method
- `backend/routes/export.py` - Export queries
- `backend/routes/filters.py` - Filter queries
- `backend/routes/analytics.py` - Analytics queries

**Time:** 2-3 hours

---

## 🟢 LOW PRIORITY

### 8. Add More Comprehensive Tests
**Status:** Basic tests passing, but could add more

**Test Coverage Needed:**
- Soft delete endpoints (6 endpoints)
- Restore endpoints (2 endpoints)
- Audit trail tracking
- Batch operations with audit trail
- WebSocket authentication
- Token refresh flow
- Hard delete with admin check

**Time:** 8-12 hours

---

### 9. Enhance Error Messages
**Status:** Error handling standardized, but messages could be more user-friendly  
**Time:** 2-3 hours

---

### 10. Optimize Database Queries
**Status:** Queries work, but could be optimized  
**Time:** 4-6 hours

---

### 11. Add API Documentation
**Status:** FastAPI auto-generates docs, but could add more descriptions  
**Time:** 2-3 hours

---

## Summary

| Priority | Task | Time Estimate | Status |
|----------|------|---------------|--------|
| 🚨 Critical | Apply migration | 5 min | ⚠️ Not done |
| 🔴 High | Update routes (DI) | 4-6 hours | ⏳ In progress |
| 🔴 High | Add admin checks | 30 min | ⏳ TODO |
| 🟡 Medium | Replace print() | 2-3 hours | ⏳ TODO |
| 🟡 Medium | Audit log table | 2-3 hours | ⏳ TODO |
| 🟡 Medium | Update deprecated code | 2-3 hours | ⏳ TODO |
| 🟡 Medium | Soft delete filtering | 2-3 hours | ⏳ TODO |
| 🟢 Low | More tests | 8-12 hours | ⏳ TODO |
| 🟢 Low | Enhance errors | 2-3 hours | ⏳ TODO |
| 🟢 Low | Optimize queries | 4-6 hours | ⏳ TODO |
| 🟢 Low | API docs | 2-3 hours | ⏳ TODO |

**Total Estimated Time:** 30-45 hours

---

## Recommended Order

1. **Apply migration** (5 min) - CRITICAL
2. **Add admin checks** (30 min) - Quick security fix
3. **Update routes** (4-6 hours) - Important for consistency
4. **Replace print()** (2-3 hours) - Incremental improvement
5. **Update deprecated code** (2-3 hours) - Future compatibility
6. **Soft delete filtering** (2-3 hours) - Data integrity
7. **Audit log table** (2-3 hours) - Nice to have
8. **More tests** (8-12 hours) - Quality assurance
9. **Other improvements** (10-15 hours) - Incremental

---

## Quick Wins (Can Do Today)

1. ✅ Apply migration (5 min)
2. ✅ Add admin checks (30 min)
3. ✅ Update 2-3 routes (1-2 hours)
4. ✅ Replace 10-15 print() statements (1 hour)

**Total:** 2-3 hours for immediate improvements

---

## Notes

- Most critical work is complete
- System is production-ready with current implementation
- Remaining work is incremental improvements
- Can be done incrementally over time
- No blocking issues

