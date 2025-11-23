"""Tests for CSV writer utility."""
import csv
import os
from pathlib import Path

import pytest

from utils.csv_writer import write_row_incremental, write_rows_incremental


def test_write_row_creates_file_with_header(temp_csv_file: Path):
    """Test that writing first row creates file with header."""
    header = ["Name", "URL", "Phone"]
    row = {"Name": "Test Business", "URL": "https://example.com", "Phone": "123-456-7890"}
    
    write_row_incremental(str(temp_csv_file), header, row)
    
    assert temp_csv_file.exists()
    with open(temp_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Name"] == "Test Business"
        assert rows[0]["URL"] == "https://example.com"


def test_write_row_appends_to_existing_file(temp_csv_file: Path):
    """Test that writing multiple rows appends correctly."""
    header = ["Name", "URL"]
    
    # Write first row
    write_row_incremental(str(temp_csv_file), header, {"Name": "Business 1", "URL": "url1"})
    
    # Write second row
    write_row_incremental(str(temp_csv_file), header, {"Name": "Business 2", "URL": "url2"})
    
    with open(temp_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["Name"] == "Business 1"
        assert rows[1]["Name"] == "Business 2"


def test_write_row_creates_parent_directory(temp_csv_file: Path):
    """Test that parent directories are created if they don't exist."""
    nested_path = temp_csv_file.parent / "nested" / "deep" / "file.csv"
    header = ["Name"]
    row = {"Name": "Test"}
    
    write_row_incremental(str(nested_path), header, row)
    
    assert nested_path.exists()
    assert nested_path.parent.exists()


def test_write_rows_incremental(temp_csv_file: Path):
    """Test writing multiple rows at once."""
    header = ["Name", "URL"]
    rows = [
        {"Name": "Business 1", "URL": "url1"},
        {"Name": "Business 2", "URL": "url2"},
        {"Name": "Business 3", "URL": "url3"},
    ]
    
    write_rows_incremental(str(temp_csv_file), header, rows)
    
    with open(temp_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        read_rows = list(reader)
        assert len(read_rows) == 3


def test_write_row_ignores_extra_fields(temp_csv_file: Path):
    """Test that extra fields not in header are ignored."""
    header = ["Name", "URL"]
    row = {"Name": "Test", "URL": "url", "Extra": "should be ignored"}
    
    write_row_incremental(str(temp_csv_file), header, row)
    
    with open(temp_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert "Extra" not in rows[0]
        assert rows[0]["Name"] == "Test"

