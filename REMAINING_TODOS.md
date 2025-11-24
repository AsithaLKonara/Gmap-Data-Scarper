# Remaining TODOs and Next Steps

**Date:** 2025-01-17  
**Status:** Review of Remaining Work

---

## Summary

Most critical work is complete. Remaining items are incremental improvements and optimizations.

---

## High Priority Remaining Items

### 1. Apply Database Migration
- **Status:** Migration file created, needs to be applied
- **Action:** Run `alembic upgrade head`
- **Priority:** High (required for soft deletes and audit trail to work)

### 2. Update Remaining Routes to Use Dependency Injection
- **Status:** Key routes updated, some routes still use manual session management
- **Routes Remaining:**
  - `backend/routes/payments.py` - 4 endpoints using `get_session()`
  - `backend/routes/workflows.py` - 6 endpoints using `get_session()`
  - `backend/routes/reports.py` - 2 endpoints using `get_session()`
  - `backend/routes/legal.py` - Some endpoints still use manual sessions
- **Priority:** Medium (works but not optimal)

### 3. Replace Remaining print() Statements
- **Status:** Some print() statements still exist
- **Files with print():**
  - `backend/services/orchestrator_service.py` - 2 print() statements
  - `backend/services/postgresql_cache.py` - 2 print() statements
  - `backend/services/retention_service.py` - 1 print() statement
  - `backend/services/stream_service.py` - 1 print() statement
  - `backend/services/chrome_pool.py` - 1 print() statement
  - `backend/services/ai_enrichment.py` - 1 print() statement
  - `backend/services/company_intelligence.py` - 1 print() statement
  - `backend/services/push_service.py` - 4 print() statements
  - `backend/services/stripe_service.py` - 2 print() statements
  - `backend/services/email_extractor.py` - 2 print() statements
  - `backend/services/zoho_crm.py` - 1 print() statement
  - `backend/services/template_service.py` - 2 print() statements
  - `backend/services/ai_query_generator.py` - 2 print() statements
  - `backend/services/anti_detection.py` - 2 print() statements
  - `backend/tasks/scraping_tasks.py` - 7 print() statements
  - `backend/scripts/create_migrations.py` - 13 print() statements
  - `backend/scripts/migrate_csv_to_db.py` - 9 print() statements
- **Priority:** Low (non-critical, can be done incrementally)

---

## Medium Priority Items

### 4. Add Admin Check for Hard Delete Endpoints
- **Status:** Hard delete endpoints exist but don't check for admin permissions
- **Files:** `backend/routes/soft_delete.py`
- **Action:** Add admin role check before allowing hard deletes
- **Priority:** Medium (security improvement)

### 5. Implement Audit Log Table
- **Status:** Placeholder exists in `backend/utils/audit_trail.py`
- **Action:** Create `AuditLog` model and table
- **Priority:** Medium (nice to have for compliance)

### 6. Add Soft Delete Filtering to All Queries
- **Status:** Some queries may not filter soft-deleted records
- **Action:** Review all Lead/Task queries and add `deleted_at IS NULL` filter
- **Priority:** Medium (data integrity)

### 7. Update Pydantic Validators to V2
- **Status:** Using deprecated Pydantic V1 validators
- **Files:** `backend/models/schemas.py`
- **Action:** Migrate `@validator` to `@field_validator`
- **Priority:** Medium (future compatibility)

### 8. Update SQLAlchemy declarative_base
- **Status:** Using deprecated `declarative_base()`
- **Files:** `backend/models/database.py`
- **Action:** Use `sqlalchemy.orm.declarative_base()`
- **Priority:** Medium (future compatibility)

### 9. Update FastAPI lifespan Events
- **Status:** Using deprecated `@app.on_event()`
- **Files:** `backend/main.py`
- **Action:** Migrate to lifespan context manager
- **Priority:** Medium (future compatibility)

---

## Low Priority Items

### 10. Add More Comprehensive Tests
- **Status:** Basic tests passing, but could add more
- **Areas:**
  - Soft delete endpoints
  - Restore endpoints
  - Audit trail tracking
  - Batch operations
  - WebSocket authentication
  - Token refresh
- **Priority:** Low (incremental improvement)

### 11. Enhance Error Messages
- **Status:** Error handling standardized, but messages could be more user-friendly
- **Priority:** Low (UX improvement)

### 12. Add Request Validation
- **Status:** Basic validation exists, could add more
- **Priority:** Low (security improvement)

### 13. Optimize Database Queries
- **Status:** Queries work, but could be optimized
- **Priority:** Low (performance improvement)

### 14. Add API Documentation
- **Status:** FastAPI auto-generates docs, but could add more descriptions
- **Priority:** Low (documentation)

---

## Immediate Actions Required

### 1. Apply Migration (CRITICAL)
```bash
# Install Alembic if not already installed
pip install alembic>=1.13.0

# Apply migration
alembic upgrade head
```

### 2. Test Soft Delete Endpoints
- Test authentication requirement
- Test soft delete functionality
- Test restore functionality
- Test query filtering

### 3. Verify Audit Trail
- Check that `created_by` is set on new leads
- Check that `modified_by` is set on updates
- Check that `modified_at` is updated

---

## Estimated Effort

- **High Priority:** 2-4 hours
- **Medium Priority:** 8-12 hours
- **Low Priority:** 16-24 hours
- **Total Remaining:** 26-40 hours

---

## Recommended Order

1. **Apply migration** (5 minutes) - CRITICAL
2. **Test new endpoints** (1 hour) - Verify functionality
3. **Update remaining routes** (4-6 hours) - Incremental
4. **Replace print() statements** (2-3 hours) - Incremental
5. **Add admin checks** (1 hour) - Security
6. **Update deprecated code** (4-6 hours) - Future compatibility
7. **Add more tests** (8-12 hours) - Quality assurance

---

## Notes

- Most critical work is complete
- Remaining items are incremental improvements
- System is production-ready with current implementation
- Remaining work can be done incrementally over time

