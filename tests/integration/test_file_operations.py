"""Integration tests for file operations."""
import pytest
import os
import tempfile
import shutil
from pathlib import Path
import csv

# Import file operation utilities
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.csv_writer import write_row_incremental


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


class TestFileOperations:
    """Test file operations (CSV writing, etc.)."""
    
    def test_csv_writer_creates_file(self, temp_dir):
        """Test that CSV writer creates file if it doesn't exist."""
        csv_path = temp_dir / "test.csv"
        fieldnames = ["Name", "Phone", "Email"]
        data = {
            "Name": "Test Business",
            "Phone": "+1234567890",
            "Email": "test@example.com"
        }
        
        write_row_incremental(str(csv_path), fieldnames, data)
        
        assert csv_path.exists()
        
        # Verify content
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["Name"] == "Test Business"
    
    def test_csv_writer_appends_rows(self, temp_dir):
        """Test that CSV writer appends rows correctly."""
        csv_path = temp_dir / "test_append.csv"
        fieldnames = ["Name", "Phone"]
        
        # Write first row
        write_row_incremental(str(csv_path), fieldnames, {
            "Name": "Business 1",
            "Phone": "+1111111111"
        })
        
        # Write second row
        write_row_incremental(str(csv_path), fieldnames, {
            "Name": "Business 2",
            "Phone": "+2222222222"
        })
        
        # Verify both rows
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["Name"] == "Business 1"
            assert rows[1]["Name"] == "Business 2"
    
    def test_csv_writer_handles_missing_fields(self, temp_dir):
        """Test that CSV writer handles missing fields gracefully."""
        csv_path = temp_dir / "test_missing.csv"
        fieldnames = ["Name", "Phone", "Email"]
        data = {
            "Name": "Test",
            "Phone": "+1234567890"
            # Email is missing
        }
        
        write_row_incremental(str(csv_path), fieldnames, data)
        
        # Should still write successfully
        assert csv_path.exists()
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["Email"] == ""  # Empty for missing field


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

