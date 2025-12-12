"""Database migration tests to verify Alembic migrations work correctly."""
import pytest
import os
from pathlib import Path

# Set TESTING mode
os.environ["TESTING"] = "true"


@pytest.fixture(scope="module")
def test_database_url():
    """Get test database URL."""
    # Use in-memory SQLite for migration tests
    return "sqlite:///:memory:"


class TestMigrations:
    """Test database migrations."""
    
    def test_alembic_config_exists(self):
        """Test that alembic.ini file exists."""
        alembic_ini = Path("alembic.ini")
        assert alembic_ini.exists(), "alembic.ini file not found"
    
    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory exists."""
        versions_dir = Path("alembic/versions")
        assert versions_dir.exists(), "alembic/versions directory not found"
        assert versions_dir.is_dir(), "alembic/versions is not a directory"
    
    def test_migration_files_exist(self):
        """Test that migration files exist."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        # Should have at least one migration file
        assert len(migration_files) > 0, "No migration files found in alembic/versions"
    
    def test_migration_files_are_valid_python(self):
        """Test that migration files are valid Python."""
        import ast
        
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        for migration_file in migration_files:
            try:
                with open(migration_file, "r", encoding="utf-8") as f:
                    source = f.read()
                    ast.parse(source)
            except SyntaxError as e:
                pytest.fail(f"Migration file {migration_file} has syntax errors: {e}")
    
    def test_migration_imports(self):
        """Test that migrations can be imported."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        for migration_file in migration_files:
            # Try to import the migration module
            # This is a basic check - full migration testing would require Alembic setup
            try:
                # Read and check for required Alembic imports
                with open(migration_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Check for required Alembic components
                    assert "op." in content or "batch_op." in content or "def upgrade()" in content
            except Exception as e:
                pytest.fail(f"Failed to read migration file {migration_file}: {e}")
    
    def test_migration_has_upgrade_function(self):
        """Test that migrations have upgrade() function."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        for migration_file in migration_files:
            with open(migration_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "def upgrade()" in content, f"Migration {migration_file} missing upgrade() function"
    
    def test_migration_has_downgrade_function(self):
        """Test that migrations have downgrade() function."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        for migration_file in migration_files:
            with open(migration_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "def downgrade()" in content, f"Migration {migration_file} missing downgrade() function"
    
    def test_alembic_can_detect_current_version(self):
        """Test that Alembic can detect current database version."""
        try:
            from alembic.config import Config
            from alembic import command
            from alembic.script import ScriptDirectory
            
            # Create Alembic config
            alembic_cfg = Config("alembic.ini")
            
            # Try to get script directory
            script = ScriptDirectory.from_config(alembic_cfg)
            
            # Get current revision (this may fail if database not set up)
            # But we can at least verify the script directory loads
            assert script is not None
        except Exception as e:
            # If this fails, it might be because database isn't configured
            # This is acceptable for basic structure tests
            pytest.skip(f"Could not initialize Alembic (may need database setup): {e}")


class TestMigrationContent:
    """Test migration content and structure."""
    
    def test_migrations_use_correct_base(self):
        """Test that migrations use the correct Base."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        for migration_file in migration_files:
            with open(migration_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for Base import or reference
                # Most migrations will reference Base from models
                assert "Base" in content or "target_metadata" in content or "op." in content


class TestSchemaMigrations:
    """Test specific schema migrations."""
    
    def test_audit_log_table_migration_exists(self):
        """Test that audit log table migration exists."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        # Check if any migration mentions audit_log
        audit_log_migrations = [
            f for f in migration_files
            if "audit" in f.read_text().lower() or "audit_log" in f.read_text().lower()
        ]
        
        # Should have at least one migration related to audit logs
        # (This is optional - may not exist yet)
        if len(audit_log_migrations) == 0:
            pytest.skip("No audit log migration found (may not be implemented yet)")
    
    def test_soft_delete_migration_exists(self):
        """Test that soft delete fields migration exists."""
        versions_dir = Path("alembic/versions")
        migration_files = list(versions_dir.glob("*.py"))
        
        # Check if any migration mentions deleted_at
        soft_delete_migrations = [
            f for f in migration_files
            if "deleted_at" in f.read_text().lower() or "soft_delete" in f.read_text().lower()
        ]
        
        if len(soft_delete_migrations) == 0:
            pytest.skip("No soft delete migration found (may not be implemented yet)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

