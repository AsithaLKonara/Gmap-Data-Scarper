# TODOs Progress Update

**Date:** 2025-01-17  
**Status:** Significant Progress Made

---

## ✅ Completed

### 1. Git Commit & Push ✅
- Committed and pushed all changes

### 2. Admin Checks for Hard Delete Endpoints ✅
- **File:** `backend/routes/soft_delete.py`
- **Changes:**
  - Added `check_admin_access()` function
  - Checks `ADMIN_USER_IDS` environment variable
  - Added admin check to both hard delete endpoints
- **Status:** Complete and tested

### 3. Update Reports Routes ✅
- **File:** `backend/routes/reports.py`
- **Endpoints Updated:** 2
  - `list_scheduled_reports()` ✅
  - `delete_scheduled_report()` ✅
- **Status:** Complete

### 4. Update Workflows Routes ✅
- **File:** `backend/routes/workflows.py`
- **Endpoints Updated:** 6
  - `create_workflow()` ✅
  - `list_workflows()` ✅
  - `get_workflow()` ✅
  - `update_workflow()` ✅
  - `delete_workflow()` ✅
  - `get_workflow_executions()` ✅
- **Status:** Complete

---

## ⏳ Remaining

### 1. Apply Database Migration ⚠️
- **Issue:** Alembic not installed
- **Solution:** 
  ```bash
  pip install alembic>=1.13.0
  alembic upgrade head
  ```
- **Status:** Blocked until Alembic is installed

### 2. Update Payments Routes
- **File:** `backend/routes/payments.py`
- **Endpoints:** 4 endpoints still use `get_session()`
- **Note:** Has comment about complex logic - may need careful review
- **Status:** Pending

### 3. Update Legal Routes
- **File:** `backend/routes/legal.py`
- **Endpoints:** Some endpoints already updated, some still pending
- **Status:** Partially done

### 4. Update Scraper Route
- **File:** `backend/routes/scraper.py`
- **Endpoints:** 1 endpoint partially updated
- **Status:** Partially done

### 5. Replace print() Statements
- **Count:** 68 instances across 19 files
- **Status:** Pending

### 6. Update Deprecated Code
- Pydantic V2 validators
- SQLAlchemy declarative_base
- FastAPI lifespan events
- **Status:** Pending

### 7. Add Soft Delete Filtering
- Review all queries for `deleted_at IS NULL` filter
- **Status:** Pending

---

## Summary

- **Completed:** 3 tasks (admin checks, reports routes, workflows routes)
- **In Progress:** Route updates (payments, legal, scraper)
- **Blocked:** Migration (needs Alembic installation)
- **Remaining:** ~5 tasks

**Progress:** ~40% of high-priority items complete

---

## Next Steps

1. Install Alembic and apply migration
2. Update remaining routes (payments, legal, scraper)
3. Replace print() statements
4. Update deprecated code
5. Add soft delete filtering

