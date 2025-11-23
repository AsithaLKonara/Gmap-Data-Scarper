# PostgreSQL Setup Guide for Windows

This guide will help you install and configure PostgreSQL for the Lead Intelligence Platform.

---

## Step 1: Install PostgreSQL

### Option A: Download Installer (Recommended)

1. **Download PostgreSQL**:
   - Visit: https://www.postgresql.org/download/windows/
   - Or use direct link: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Download the latest version (15.x or 16.x)

2. **Run the Installer**:
   - Run the downloaded `.exe` file
   - Follow the installation wizard
   - **Important**: Remember the password you set for the `postgres` superuser
   - Default port: `5432` (keep this)
   - Default installation directory: `C:\Program Files\PostgreSQL\{version}`

3. **Complete Installation**:
   - The installer will also install pgAdmin (database management tool)
   - Finish the installation

### Option B: Using Chocolatey (if you have it)

```powershell
choco install postgresql
```

---

## Step 2: Verify Installation

Open PowerShell and check:

```powershell
# Check if PostgreSQL service is running
Get-Service -Name "*postgresql*"

# Check if psql is available (may need to add to PATH)
psql --version
```

If `psql` is not found, add PostgreSQL bin directory to PATH:
```powershell
# Find your PostgreSQL installation (usually in Program Files)
$pgPath = "C:\Program Files\PostgreSQL\16\bin"  # Adjust version number
$env:Path += ";$pgPath"
```

---

## Step 3: Start PostgreSQL Service

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-16  # Adjust service name based on your version

# Or use Services GUI:
# Win + R → services.msc → Find "postgresql" → Right-click → Start
```

---

## Step 4: Create Database

### Using psql (Command Line)

```powershell
# Connect to PostgreSQL (default user is 'postgres')
psql -U postgres

# Or if you need to specify host:
psql -U postgres -h localhost
```

Then in the PostgreSQL prompt:

```sql
-- Create database
CREATE DATABASE lead_intelligence;

-- Create a user (optional, or use postgres user)
CREATE USER leadintel WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lead_intelligence TO leadintel;

-- Exit
\q
```

### Using pgAdmin (GUI)

1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to PostgreSQL server (use password you set during installation)
3. Right-click on **Databases** → **Create** → **Database**
4. Name: `lead_intelligence`
5. Click **Save**

---

## Step 5: Set Environment Variable

### For Current Session (Temporary)

```powershell
# Using postgres user (default)
$env:DATABASE_URL="postgresql://postgres:your_password@localhost:5432/lead_intelligence"

# Or using custom user
$env:DATABASE_URL="postgresql://leadintel:your_secure_password@localhost:5432/lead_intelligence"
```

### For Permanent (System-wide)

1. Open **System Properties**:
   - Win + R → `sysdm.cpl` → **Advanced** tab → **Environment Variables**

2. Under **User variables** or **System variables**, click **New**:
   - Variable name: `DATABASE_URL`
   - Variable value: `postgresql://postgres:your_password@localhost:5432/lead_intelligence`

3. Click **OK** on all dialogs

4. **Restart PowerShell/terminal** for changes to take effect

### Create .env File (Recommended for Development)

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/lead_intelligence
```

**Note**: Make sure `.env` is in `.gitignore` (already configured)

---

## Step 6: Test Connection

```powershell
# Test from Python
python -c "from backend.models.database import get_engine; engine = get_engine(); print('Connection OK!')"
```

---

## Step 7: Initialize Database Tables

```powershell
# Run the initialization script
python scripts/init_database.py
```

This will create all required tables:
- `leads`
- `tasks`
- `push_subscriptions`

---

## Troubleshooting

### "psql: command not found"

**Solution**: Add PostgreSQL bin directory to PATH or use full path:
```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

### "Connection refused" or "Connection timeout"

**Solutions**:
1. Check if PostgreSQL service is running:
   ```powershell
   Get-Service -Name "*postgresql*"
   ```

2. Start the service:
   ```powershell
   Start-Service postgresql-x64-16  # Adjust service name
   ```

3. Check if port 5432 is in use:
   ```powershell
   netstat -ano | findstr :5432
   ```

### "Authentication failed"

**Solutions**:
1. Verify password is correct
2. Check `pg_hba.conf` file (usually in `C:\Program Files\PostgreSQL\{version}\data\`)
3. Ensure `trust` or `md5` authentication is enabled for localhost

### "Database does not exist"

**Solution**: Create the database first (see Step 4)

---

## Quick Reference

### Common Commands

```powershell
# Start PostgreSQL service
Start-Service postgresql-x64-16

# Stop PostgreSQL service
Stop-Service postgresql-x64-16

# Connect to PostgreSQL
psql -U postgres -d lead_intelligence

# List all databases
psql -U postgres -c "\l"

# List tables in database
psql -U postgres -d lead_intelligence -c "\dt"
```

---

## Next Steps

After PostgreSQL is set up:

1. ✅ Set `DATABASE_URL` environment variable
2. ✅ Run `python scripts/init_database.py`
3. ✅ Start backend: `python backend/main.py`
4. ✅ Frontend should already be running on http://localhost:3000

---

## Need Help?

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- pgAdmin Documentation: https://www.pgadmin.org/docs/
- Check application logs for detailed error messages

