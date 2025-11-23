"""Tests for main.py CLI."""
import sys
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(pytest.importorskip("pathlib").Path(__file__).parent.parent.parent))


def test_cli_help_output(capsys):
    """Test that --help shows all options."""
    from main import main
    
    with pytest.raises(SystemExit):
        sys.argv = ["main.py", "--help"]
        main()
    
    output = capsys.readouterr().out
    assert "--platforms" in output
    assert "--no-headless" in output
    assert "--skip-gmaps" in output


def test_cli_invalid_platform(capsys):
    """Test that invalid platform shows error."""
    from main import main
    
    with patch("main.read_config", return_value={"enabled_platforms": []}):
        sys.argv = ["main.py", "--platforms", "invalid_platform"]
        main()
    
    output = capsys.readouterr().out
    assert "ERROR" in output or "Invalid" in output


def test_cli_valid_platforms(capsys):
    """Test that valid platforms are accepted."""
    from main import main
    
    with patch("main.read_config", return_value={"enabled_platforms": []}), \
         patch("main.read_queries", return_value=["test query"]), \
         patch("main.get_scraper_instances", return_value=[]), \
         patch("main.load_processed_keys", return_value=set()):
        
        sys.argv = ["main.py", "--platforms", "facebook,instagram"]
        try:
            main()
        except (SystemExit, AttributeError):
            pass  # Expected to fail when trying to run scrapers
    
    output = capsys.readouterr().out
    assert "facebook" in output.lower() or "instagram" in output.lower()


def test_cli_no_headless_flag(capsys):
    """Test that --no-headless flag is processed."""
    from main import main
    
    with patch("main.read_config", return_value={"headless": True, "enabled_platforms": []}), \
         patch("main.read_queries", return_value=["test query"]), \
         patch("main.get_scraper_instances", return_value=[]), \
         patch("main.load_processed_keys", return_value=set()):
        
        sys.argv = ["main.py", "--no-headless", "--platforms", "facebook"]
        try:
            main()
        except (SystemExit, AttributeError):
            pass
    
    output = capsys.readouterr().out
    assert "visible" in output.lower() or "headless" in output.lower()

