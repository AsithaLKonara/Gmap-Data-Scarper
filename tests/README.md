# Testing Guide

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov --cov-report=html
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Platform-specific tests
pytest tests/platform/

# CLI tests
pytest tests/cli/

# Error handling tests
pytest tests/error_handling/
```

### Run specific test file
```bash
pytest tests/unit/test_csv_writer.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with markers
```bash
# Run only fast tests
pytest -m "not slow"

# Run only unit tests
pytest -m unit
```

## Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interactions
- `tests/platform/` - Platform-specific scraper tests
- `tests/cli/` - CLI functionality tests
- `tests/error_handling/` - Error handling and edge cases
- `tests/fixtures/` - Test data and fixtures

## Writing Tests

### Example Unit Test
```python
def test_my_function():
    result = my_function("input")
    assert result == "expected_output"
```

### Using Fixtures
```python
def test_with_fixture(temp_dir):
    file_path = temp_dir / "test.txt"
    file_path.write_text("test")
    assert file_path.exists()
```

### Mocking External Dependencies
```python
from unittest.mock import patch

@patch("module.external_dependency")
def test_with_mock(mock_dependency):
    mock_dependency.return_value = "mocked"
    result = my_function()
    assert result == "mocked"
```

## Coverage Goals

- Target: 80% code coverage
- Critical paths: 100% coverage
- Error handling: All error paths tested

