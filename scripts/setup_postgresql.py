#!/usr/bin/env python3
"""
PostgreSQL setup script for Lead Intelligence Platform.
This script helps set up the database and configure connection.
"""

import os
import sys
import subprocess
import getpass

def check_postgresql_installed():
    """Check if PostgreSQL is installed and accessible."""
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try common Windows paths
    common_paths = [
        r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ PostgreSQL found at: {path}")
            return True, path
    
    print("❌ PostgreSQL not found in PATH or common locations")
    return False, None

def test_connection(host="localhost", port=5432, user="postgres", password=None, database="postgres"):
    """Test PostgreSQL connection."""
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        conn_string = f"host={host} port={port} user={user} dbname={database}"
        if password:
            conn_string += f" password={password}"
        
        conn = psycopg2.connect(conn_string)
        conn.close()
        print("✅ Connection successful!")
        return True
    except ImportError:
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_database(host="localhost", port=5432, user="postgres", password=None, dbname="lead_intelligence"):
    """Create the lead_intelligence database."""
    try:
        import psycopg2
        from psycopg2 import OperationalError, errors
        
        # Connect to default postgres database
        conn_string = f"host={host} port={port} user={user} dbname=postgres"
        if password:
            conn_string += f" password={password}"
        
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (dbname,)
        )
        
        if cursor.fetchone():
            print(f"✅ Database '{dbname}' already exists")
            cursor.close()
            conn.close()
            return True
        
        # Create database
        cursor.execute(f'CREATE DATABASE "{dbname}"')
        print(f"✅ Database '{dbname}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except errors.DuplicateDatabase:
        print(f"✅ Database '{dbname}' already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_env_file(host="localhost", port=5432, user="postgres", password=None, dbname="lead_intelligence"):
    """Create or update .env file with DATABASE_URL."""
    env_file = ".env"
    
    # Build DATABASE_URL
    if password:
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    else:
        database_url = f"postgresql://{user}@{host}:{port}/{dbname}"
    
    # Read existing .env if it exists
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Update DATABASE_URL
    env_vars['DATABASE_URL'] = database_url
    
    # Write to .env
    with open(env_file, 'w') as f:
        f.write("# Database Configuration\n")
        f.write(f"DATABASE_URL={database_url}\n\n")
        
        # Write other existing vars (excluding DATABASE_URL to avoid duplicates)
        for key, value in env_vars.items():
            if key != 'DATABASE_URL':
                f.write(f"{key}={value}\n")
    
    print(f"✅ DATABASE_URL saved to {env_file}")
    print(f"   {database_url.replace(password or '', '***') if password else database_url}")

def main():
    """Main setup function."""
    print("=" * 60)
    print("PostgreSQL Setup for Lead Intelligence Platform")
    print("=" * 60)
    print()
    
    # Check if PostgreSQL is installed
    pg_check = check_postgresql_installed()
    if not pg_check or (isinstance(pg_check, tuple) and not pg_check[0]):
        print()
        print("❌ PostgreSQL is not installed or not in PATH.")
        print()
        print("Please install PostgreSQL first:")
        print("1. Download from: https://www.postgresql.org/download/windows/")
        print("2. Run the installer")
        print("3. Remember the password you set for 'postgres' user")
        print("4. Run this script again after installation")
        print()
        print("See docs/POSTGRESQL_SETUP.md for detailed instructions.")
        sys.exit(1)
    
    print()
    print("Please provide PostgreSQL connection details:")
    print("(Press Enter to use defaults)")
    print()
    
    # Get connection details
    host = input("Host [localhost]: ").strip() or "localhost"
    port = input("Port [5432]: ").strip() or "5432"
    user = input("Username [postgres]: ").strip() or "postgres"
    password = getpass.getpass("Password: ").strip()
    dbname = input("Database name [lead_intelligence]: ").strip() or "lead_intelligence"
    
    print()
    print("Testing connection...")
    if not test_connection(host, int(port), user, password):
        print()
        print("❌ Connection test failed. Please check:")
        print("   - PostgreSQL service is running")
        print("   - Username and password are correct")
        print("   - Port is correct (default: 5432)")
        sys.exit(1)
    
    print()
    print("Creating database...")
    if not create_database(host, int(port), user, password, dbname):
        print()
        print("❌ Failed to create database.")
        sys.exit(1)
    
    print()
    print("Setting up environment...")
    setup_env_file(host, int(port), user, password, dbname)
    
    print()
    print("=" * 60)
    print("✅ PostgreSQL setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Initialize database tables: python scripts/init_database.py")
    print("2. Start backend: python backend/main.py")
    print("3. Frontend should already be running on http://localhost:3000")
    print()

if __name__ == "__main__":
    main()

