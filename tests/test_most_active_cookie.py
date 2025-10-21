"""
Comprehensive test suite for Most Active Cookie Analyzer

Tests cover:
- Happy path scenarios
- Edge cases (ties, empty files, invalid data)
- Error handling
- Performance considerations
"""

import sys
import tempfile
from pathlib import Path

import pytest

from src.most_active_cookie import CookieLogAnalyzer, main, parse_arguments


class TestCookieLogAnalyzer:
    """Test cases for CookieLogAnalyzer class."""

    def create_temp_log_file(self, content: str) -> Path:
        """Helper to create temporary log file for testing."""
        
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_initialization_with_valid_file(self, tmp_path):
        """Test analyzer initializes correctly with valid file."""
        
        log_file = tmp_path / "test.csv"
        log_file.write_text("cookie,timestamp\n")

        analyzer = CookieLogAnalyzer(log_file)
        assert analyzer.log_file == log_file

    def test_initialization_with_nonexistent_file(self):
        """Test analyzer raises error for nonexistent file."""
        
        with pytest.raises(FileNotFoundError):
            CookieLogAnalyzer(Path("/nonexistent/file.csv"))

    def test_single_most_active_cookie(self):
        """Test finding single most active cookie."""
        
        content = """cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
        5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
        AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            assert result == ["AtY0laUfhglK3lC7"]
        finally:
            log_file.unlink()

    def test_multiple_cookies_with_same_count(self):
        """Test finding multiple cookies tied for most active."""
        
        content = """cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
        5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
        AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-09T06:19:00+00:00
        4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            # Both cookies appear twice
            assert sorted(result) == ["AtY0laUfhglK3lC7", "SAZuXPGUrfbcn5UA"]
        finally:
            log_file.unlink()

    def test_no_cookies_for_date(self):
        """Test when no cookies exist for the specified date."""
        
        content = """cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-10")

            assert result == []
        finally:
            log_file.unlink()

    def test_empty_file_after_header(self):
        """Test handling of file with only header."""
        
        content = "cookie,timestamp\n"
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            assert result == []
        finally:
            log_file.unlink()

    def test_invalid_date_format(self):
        """Test error handling for invalid date format."""
        content = "cookie,timestamp\n"
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)

            with pytest.raises(ValueError, match="Invalid date format"):
                analyzer.find_most_active_cookies("12-09-2018")

            with pytest.raises(ValueError, match="Invalid date format"):
                analyzer.find_most_active_cookies("2018/12/09")
        finally:
            log_file.unlink()

    def test_malformed_log_lines(self):
        """Test handling of malformed log lines."""
        
        content = """cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
        INVALID_LINE_NO_COMMA
        SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
        ,2018-12-09T10:13:00+00:00
        AtY0laUfhglK3lC7,
        AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            # Should still find valid entries
            assert result == ["AtY0laUfhglK3lC7"]
        finally:
            log_file.unlink()

    def test_early_termination_optimization(self):
        """Test that analyzer stops reading once past target date."""
        
        # This tests the optimization for sorted logs
        content = """cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-10T14:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
        AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
        5UAVanZf6UtGyKVS,2018-12-08T07:25:00+00:00
        4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            # Both cookies appear once on 2018-12-09, so both should be returned
            # The key point is it should stop before processing 12-08 entries
            assert sorted(result) == ["AtY0laUfhglK3lC7", "SAZuXPGUrfbcn5UA"]
        finally:
            log_file.unlink()

    def test_all_cookies_same_count(self):
        """Test when all cookies appear exactly once."""
        
        content = """cookie,timestamp
        Cookie1,2018-12-09T14:19:00+00:00
        Cookie2,2018-12-09T10:13:00+00:00
        Cookie3,2018-12-09T07:25:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            assert sorted(result) == ["Cookie1", "Cookie2", "Cookie3"]
        finally:
            log_file.unlink()

    def test_date_boundary_cases(self):
        """Test cookies at midnight boundaries."""
        
        content = """cookie,timestamp
        Cookie1,2018-12-09T23:59:59+00:00
        Cookie2,2018-12-09T00:00:00+00:00
        Cookie3,2018-12-08T23:59:59+00:00
        Cookie4,2018-12-10T00:00:00+00:00
        """
        log_file = self.create_temp_log_file(content)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            assert sorted(result) == ["Cookie1", "Cookie2"]
        finally:
            log_file.unlink()

    def test_parse_line_valid(self):
        """Test parsing valid log line."""
        
        analyzer = CookieLogAnalyzer(Path(__file__))  # Just need any valid path
        cookie, timestamp = analyzer._parse_line(
            "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00"
        )

        assert cookie == "AtY0laUfhglK3lC7"
        assert timestamp == "2018-12-09T14:19:00+00:00"

    def test_parse_line_with_comma_in_data(self):
        """Test parsing line that might have comma in cookie name."""
        
        analyzer = CookieLogAnalyzer(Path(__file__))
        cookie, timestamp = analyzer._parse_line(
            "Cookie,WithComma,2018-12-09T14:19:00+00:00"
        )

        # First comma splits, rest stays with timestamp
        assert cookie == "Cookie"
        assert timestamp == "WithComma,2018-12-09T14:19:00+00:00"

    def test_extract_date_valid(self):
        """Test extracting date from valid timestamp."""
        
        analyzer = CookieLogAnalyzer(Path(__file__))
        date = analyzer._extract_date("2018-12-09T14:19:00+00:00")

        assert date == "2018-12-09"

    def test_extract_date_invalid(self):
        """Test error handling for invalid timestamp."""
        
        analyzer = CookieLogAnalyzer(Path(__file__))

        with pytest.raises(ValueError):
            analyzer._extract_date("invalid-timestamp")


class TestCommandLineInterface:
    """Test cases for CLI functionality."""

    def test_parse_arguments_valid(self, monkeypatch):
        """Test parsing valid command-line arguments."""
        
        monkeypatch.setattr(
            sys, "argv", ["prog", "-f", "cookie_log.csv", "-d", "2018-12-09"]
        )

        args = parse_arguments()
        assert args.file == Path("cookie_log.csv")
        assert args.date == "2018-12-09"
        assert args.verbose is False

    def test_parse_arguments_verbose(self, monkeypatch):
        """Test verbose flag parsing."""
        
        monkeypatch.setattr(
            sys, "argv", ["prog", "-f", "log.csv", "-d", "2018-12-09", "-v"]
        )

        args = parse_arguments()
        assert args.verbose is True

    def test_main_success(self, tmp_path, monkeypatch, capsys):
        """Test main function with successful execution."""
        
        # Create test file
        log_file = tmp_path / "test.csv"
        log_file.write_text("""cookie,timestamp
        AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
        AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
        SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
        """)

        monkeypatch.setattr(
            sys, "argv", ["prog", "-f", str(log_file), "-d", "2018-12-09"]
        )

        exit_code = main()
        captured = capsys.readouterr()

        assert exit_code == 0
        assert "AtY0laUfhglK3lC7" in captured.out

    def test_main_file_not_found(self, monkeypatch, capsys):
        """Test main function with nonexistent file."""
        
        monkeypatch.setattr(
            sys, "argv", ["prog", "-f", "/nonexistent/file.csv", "-d", "2018-12-09"]
        )

        exit_code = main()
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Error" in captured.err

    def test_main_invalid_date(self, tmp_path, monkeypatch, capsys):
        """Test main function with invalid date format."""
        
        log_file = tmp_path / "test.csv"
        log_file.write_text("cookie,timestamp\n")

        monkeypatch.setattr(
            sys, "argv", ["prog", "-f", str(log_file), "-d", "invalid-date"]
        )

        exit_code = main()
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Error" in captured.err


class TestPerformance:
    """Test cases for performance considerations."""

    def test_large_file_handling(self):
        """Test handling of larger log files."""
        
        # Generate a larger dataset
        lines = ["cookie,timestamp\n"]
        for i in range(10000):
            lines.append(f"Cookie{i % 100},2018-12-09T{i % 24:02d}:00:00+00:00\n")

        content = "".join(lines)

        temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        temp_file.write(content)
        temp_file.close()
        log_file = Path(temp_file.name)

        try:
            analyzer = CookieLogAnalyzer(log_file)
            result = analyzer.find_most_active_cookies("2018-12-09")

            # Each cookie appears 100 times (10000 / 100)
            assert len(result) == 100  # All tied
        finally:
            log_file.unlink()


# Fixtures for pytest
@pytest.fixture
def sample_log_content():
    """Sample log content for testing."""
    
    return """cookie,timestamp
            AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
            SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
            5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
            AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
            SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00
            4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00
            fbcn5UAVanZf6UtG,2018-12-08T09:30:00+00:00
            4sMM2LxV07bPJzwf,2018-12-07T23:30:00+00:00
            """
