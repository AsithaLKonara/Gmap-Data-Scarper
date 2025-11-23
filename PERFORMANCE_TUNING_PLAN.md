# Performance Tuning Plan - Lead Intelligence Platform

## Overview

This document outlines the performance optimizations implemented for the Lead Intelligence Platform to support bulk operations (100K+ records) and enterprise-scale usage.

## Implemented Optimizations

### 1. Async Scraping Service

**File**: `backend/services/async_scraper_service.py`

- **httpx Integration**: Uses `httpx.AsyncClient` for async HTTP requests
- **Connection Pooling**: Reuses connections with configurable pool size
- **Concurrency Control**: Semaphore-based limiting (max 5 concurrent per platform)
- **Request Batching**: Supports batch processing with configurable batch sizes
- **Retry Logic**: Exponential backoff with configurable attempts
- **Timeout Management**: Configurable request timeouts

**Usage**:
```python
async with AsyncScraperService(max_concurrent=5) as scraper:
    results = await scraper.scrape_batch(urls, scrape_func, delay_seconds=1.0)
```

### 2. Chrome Instance Pool

**File**: `backend/services/chrome_pool.py`

- **Pool Management**: Reuses Chrome instances across tasks
- **Tab Isolation**: One tab per task for isolation
- **Resource Management**: Automatic cleanup of idle instances (5-minute timeout)
- **Port Allocation**: Integrates with dynamic port allocation
- **Configurable Pool Size**: Default 10 instances, configurable

**Features**:
- Reduces Chrome startup overhead
- Better memory management
- Faster task initialization
- Automatic idle cleanup

### 3. Resource Optimization

**File**: `backend/services/resource_optimizer.py`

- **Image Compression**: JPEG/PNG/WEBP compression with quality control
- **Screenshot Optimization**: Target size-based compression (default 200KB)
- **Text Compression**: Gzip/Brotli compression for WebSocket streams
- **Memory Efficiency**: Reduces memory footprint for large datasets

**Usage**:
```python
optimizer = get_resource_optimizer()
compressed = optimizer.optimize_screenshot(screenshot_data, target_size_kb=200)
```

### 4. PostgreSQL Cache

**File**: `backend/services/postgresql_cache.py`

- **Database-Backed Cache**: Migrates from SQLite to PostgreSQL
- **Connection Pooling**: Thread-safe connection pool (2-10 connections)
- **Indexed Queries**: Fast lookups with proper indexes
- **Deduplication**: Database-level unique constraints
- **Automatic Cleanup**: Configurable retention period (default 30 days)

**Benefits**:
- Better performance at scale
- Concurrent access support
- Reduced memory usage
- Persistent cache across restarts

### 5. Data Archival (Planned)

**Status**: Architecture defined, implementation pending

- **Table Partitioning**: Partition by date for efficient queries
- **Cold Storage**: Archive old records to separate tables
- **Automated Process**: Scheduled archival jobs
- **Query Optimization**: Faster queries on recent data

## Performance Benchmarks

### Before Optimization

- **Concurrent Tasks**: 1-2 tasks
- **Memory Usage**: ~2GB per Chrome instance
- **Request Throughput**: ~10 requests/second
- **Cache Lookup**: ~50ms (SQLite)
- **Screenshot Size**: ~500KB average

### After Optimization (Expected)

- **Concurrent Tasks**: 10+ tasks (with pool)
- **Memory Usage**: ~500MB per Chrome instance (shared)
- **Request Throughput**: ~50 requests/second (with async)
- **Cache Lookup**: ~5ms (PostgreSQL with indexes)
- **Screenshot Size**: ~200KB average (compressed)

## Configuration

### Environment Variables

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/lead_intelligence

# Chrome Pool
CHROME_POOL_SIZE=10
CHROME_IDLE_TIMEOUT=300

# Async Scraper
ASYNC_MAX_CONCURRENT=5
ASYNC_TIMEOUT=30.0
ASYNC_MAX_CONNECTIONS=100

# Resource Optimization
SCREENSHOT_TARGET_SIZE_KB=200
IMAGE_COMPRESSION_QUALITY=85
```

## Migration Guide

### From SQLite to PostgreSQL

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create Database**:
   ```sql
   CREATE DATABASE lead_intelligence;
   ```

3. **Set Environment Variable**:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost:5432/lead_intelligence
   ```

4. **Migrate Data** (if needed):
   ```python
   # Migration script would go here
   # Migrates existing SQLite cache to PostgreSQL
   ```

### Enabling Chrome Pool

1. **Update Orchestrator**:
   ```python
   from backend.services.chrome_pool import get_chrome_pool
   
   pool = get_chrome_pool()
   driver = pool.acquire(task_id)
   # Use driver...
   pool.release(task_id, driver)
   ```

2. **Configure Pool Size**:
   ```python
   pool = ChromePool(pool_size=10, headless=True)
   ```

## Monitoring

### Key Metrics

- **Chrome Pool Utilization**: Active instances / Pool size
- **Cache Hit Rate**: Cache hits / Total requests
- **Request Latency**: Average response time
- **Memory Usage**: Per-instance and total
- **Throughput**: Requests per second

### Monitoring Endpoints

- `/api/health` - System health
- `/api/metrics` - Performance metrics
- Cache stats available via `get_cache_stats()`

## Best Practices

1. **Chrome Pool**:
   - Use pool for multiple concurrent tasks
   - Release instances promptly after use
   - Monitor pool utilization

2. **Async Scraping**:
   - Use for HTTP-based scrapers only
   - Keep Selenium-based scrapers sequential
   - Configure appropriate concurrency limits

3. **Resource Optimization**:
   - Compress screenshots before WebSocket streaming
   - Use appropriate quality settings
   - Monitor bandwidth usage

4. **PostgreSQL Cache**:
   - Regular cleanup of old records
   - Monitor cache hit rates
   - Adjust retention period as needed

## Future Enhancements

- [ ] Redis cache layer for hot data
- [ ] CDN for static assets
- [ ] Horizontal scaling with load balancer
- [ ] Database read replicas
- [ ] Advanced query optimization
- [ ] Automated performance testing

## Troubleshooting

### High Memory Usage

- Reduce Chrome pool size
- Enable headless mode
- Reduce screenshot quality
- Clean up old cache records

### Slow Cache Lookups

- Check PostgreSQL indexes
- Monitor connection pool usage
- Consider Redis for hot cache

### Chrome Pool Exhaustion

- Increase pool size
- Reduce concurrent tasks
- Improve task completion rate
- Check for resource leaks

## References

- [httpx Documentation](https://www.python-httpx.org/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
- [Selenium Best Practices](https://www.selenium.dev/documentation/webdriver/)

