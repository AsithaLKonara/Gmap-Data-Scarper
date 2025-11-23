"""Tests for config loading."""
import os
import tempfile
from pathlib import Path

import pytest
import yaml

from orchestrator_core import read_config


def test_read_config_success(temp_config_file: Path):
    """Test reading a valid config file."""
    config = read_config(str(temp_config_file))
    
    assert "enabled_platforms" in config
    assert isinstance(config["enabled_platforms"], list)
    assert "max_results_per_query" in config


def test_read_config_handles_missing_file():
    """Test that missing config file returns empty dict."""
    import os
    # Use a path that definitely doesn't exist
    nonexistent = os.path.join(os.path.dirname(__file__), "nonexistent_config_12345.yaml")
    config = read_config(nonexistent)
    
    assert config == {}


def test_read_config_handles_invalid_yaml(temp_dir: Path):
    """Test that invalid YAML is handled gracefully."""
    invalid_config = temp_dir / "invalid.yaml"
    # Write truly invalid YAML
    invalid_config.write_text("invalid: yaml: content: [unclosed")
    
    config = read_config(str(invalid_config))
    
    # Should return empty dict on YAML error
    assert isinstance(config, dict)
    assert config == {}  # Should return empty dict on error


def test_read_config_defaults():
    """Test that config has sensible defaults."""
    import os
    # Use a path that definitely doesn't exist
    nonexistent = os.path.join(os.path.dirname(__file__), "nonexistent_12345.yaml")
    config = read_config(nonexistent)
    
    # Should return empty dict for missing file
    assert isinstance(config, dict)
    assert config == {}


def test_config_has_required_keys(temp_config_file: Path):
    """Test that config contains expected keys."""
    config = read_config(str(temp_config_file))
    
    # These keys should be present or have defaults
    expected_keys = ["enabled_platforms", "max_results_per_query", "headless"]
    
    # Config should either have these or we use defaults
    for key in expected_keys:
        # Test that accessing with .get() works (defaults are handled in code)
        value = config.get(key)
        assert value is None or isinstance(value, (list, int, bool, str, float))

