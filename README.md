# Most Active Cookie Analyzer

A command-line tool to find the most active cookie(s) for a specific day from a cookie log file.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-ruff-purple.svg)](https://github.com/astral-sh/ruff)

## Overview

This tool analyzes cookie log files to identify which cookie(s) had the most activity on a given date. It's designed to be efficient, handling large files through optimized algorithms and early-exit strategies.

**Key Features:**
- 🚀 **Fast**: Optimized for performance with early-exit when log is sorted by timestamp
- 📊 **Handles Ties**: Returns all cookies with the maximum visit count
- 🛡️ **Robust**: Comprehensive error handling and input validation
- 📝 **Well-Tested**: 90% code coverage with 21 comprehensive tests
- 🔍 **Production-Ready**: Professional logging, type hints, and documentation

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
# Install
pip install -r requirements.txt

# Run
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-09

# Output
AtY0laUfhglK3lC7
```

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Algorithm & Design](#algorithm--design)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Code Quality](#code-quality)
- [Performance](#performance)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Setup

```bash
# Clone the repository
git clone https://github.com/shantanu747/Cookie-Analyzer.git
cd Cookie-Analyzer

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- **pytest** (8.3.3): Testing framework
- **pytest-cov** (5.0.0): Test coverage reporting
- **ruff** (0.8.4): Fast Python linter and formatter
- **mypy** (1.13.0): Static type checker

## Usage

### Basic Usage

```bash
python src/most_active_cookie.py -f <log_file> -d <date>
```

**Arguments:**
- `-f, --file FILENAME`: Path to the cookie log CSV file (required)
- `-d, --date YYYY-MM-DD`: Target date in YYYY-MM-DD format (required)
- `-v, --verbose`: Enable verbose logging (optional)
- `--version`: Show program version
- `--help`: Show help message

### Examples

#### Single Winner
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-09
```
Output:
```
AtY0laUfhglK3lC7
```

#### Multiple Winners (Tie)
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-08
```
Output (sorted alphabetically):
```
4sMM2LxV07bPJzwf
SAZuXPGUrfbcn5UA
fbcn5UAVanZf6UtG
```

#### Verbose Mode
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-09 -v
```
Shows detailed debug information including parsing details and decision points.

#### No Results
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-01
```
Output: (empty - no cookies found for that date)

### Input File Format

The input CSV file must have the following format:

```csv
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
```

**Requirements:**
- Header row: `cookie,timestamp`
- Timestamps in ISO 8601 format with timezone: `YYYY-MM-DDTHH:MM:SS+00:00`
- Sorted by timestamp (newest first) for optimal performance
- UTF-8 encoding

## Algorithm & Design

### Core Algorithm

The tool uses a single-pass counting algorithm with early-exit optimization:

1. **Validation**: Verify date format and file existence
2. **Streaming Parse**: Read file line-by-line (memory efficient)
3. **Date Filtering**: Extract date from timestamp and filter matches
4. **Counting**: Use `Counter` to track cookie occurrences
5. **Early Exit**: Stop scanning once we pass the target date (assumes sorted data)
6. **Tie Handling**: Return all cookies with maximum count

### Time Complexity

- **Best Case**: O(k) where k = number of entries on target date (early exit)
- **Worst Case**: O(n) where n = total entries (target date at end or not found)
- **Space**: O(u) where u = unique cookies on target date

### Design Decisions

#### Why Counter?
- O(1) insertions and lookups
- Clean, Pythonic API
- Built-in max/most_common operations

#### Why Single-Pass?
- Memory efficient for large files
- No need to load entire file into memory
- Streaming approach scales to any file size

#### Why Early Exit?
- Exploits sorted nature of logs (newest first)
- Dramatically improves performance for recent dates
- Falls back gracefully if not sorted

#### Why Pathlib?
- Cross-platform path handling
- Object-oriented interface
- Better type safety

### Architecture

```
┌─────────────────────────────────────────┐
│          Command Line Interface         │
│     (parse_arguments, main function)    │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│        CookieLogAnalyzer Class          │
│  ┌───────────────────────────────────┐  │
│  │  find_most_active_cookies()       │  │
│  │  - Validates date format          │  │
│  │  - Opens file in streaming mode   │  │
│  │  - Parses and counts cookies      │  │
│  │  - Returns sorted results         │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  _parse_line()                    │  │
│  │  - Splits CSV line                │  │
│  │  - Validates format               │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  _extract_date()                  │  │
│  │  - Parses ISO 8601 timestamp      │  │
│  │  - Extracts date component        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│          Logging System                 │
│  - File logging (all levels)           │
│  - stderr handler (errors only)        │
│  - Structured format with timestamps   │
└─────────────────────────────────────────┘
```

## Testing

The project includes a comprehensive test suite with 21 tests covering:

- ✅ Happy path scenarios
- ✅ Edge cases (ties, empty files, invalid data)
- ✅ Error handling (missing files, invalid dates)
- ✅ Performance considerations
- ✅ Command-line interface

### Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=src --cov-report=html

# Run specific test class
pytest tests/test_most_active_cookie.py::TestCookieLogAnalyzer -v

# Run specific test
pytest tests/test_most_active_cookie.py::TestCookieLogAnalyzer::test_single_most_active_cookie -v
```

### Test Coverage

Current coverage: **90%**

```
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/__init__.py                 0      0   100%
src/most_active_cookie.py     117     12    90%
-----------------------------------------------
TOTAL                         117     12    90%
```

View detailed coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Input Files

The project includes multiple test files for different scenarios:

| File | Rows | Purpose | Expected Result |
|------|------|---------|-----------------|
| `cookie_log.csv` | 9 | Original sample | Tests basic functionality |
| `cookie_log_1.csv` | 150 | Edge case testing | 3 cookies tied at 15 visits each |
| `cookie_log_2.csv` | 1,000 | Performance test | Single day, full file scan |
| `cookie_log_3.csv` | 10,000 | Scale test | 30 days, early-exit optimization |

## Project Structure

```
Cookie-Analyzer/
├── src/
│   ├── __init__.py                   # Package initialization
│   ├── most_active_cookie.py         # Main application
│   └── most_active_cookie Logs/      # Log files (auto-created)
│       └── YYYYMMDD_HHMMSS.txt       # Timestamped log files
├── tests/
│   ├── __init__.py                   # Test package initialization
│   └── test_most_active_cookie.py    # Comprehensive test suite
├── test_inputs/
│   ├── cookie_log.csv                # Original sample (9 rows)
│   ├── cookie_log_1.csv              # Edge case test (150 rows)
│   ├── cookie_log_2.csv              # Performance test (1,000 rows)
│   └── cookie_log_3.csv              # Scale test (10,000 rows)
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project configuration
├── QUICKSTART.md                     # Quick start guide
├── README.md                         # This file
└── .gitignore                        # Git ignore patterns
```

## Code Quality

### Type Hints

The codebase uses Python type hints throughout for better IDE support and static analysis:

```python
def find_most_active_cookies(self, target_date: str) -> List[str]:
    """Find the most active cookie(s) for a specific date."""
    ...
```

### Linting & Formatting

```bash
# Check code quality
ruff check .

# Auto-format code
ruff format .

# Type checking
mypy src/most_active_cookie.py
```

### Code Style

- **Docstrings**: Google-style docstrings for all public functions
- **Type Hints**: Full type coverage for function signatures
- **Error Handling**: Specific exception types with descriptive messages
- **Logging**: Structured logging at appropriate levels (DEBUG, INFO, ERROR)
- **Comments**: Inline comments explaining complex logic

## Performance

### Benchmarks

Tests conducted on M3 Mac:

| File Size | Records | Date Position | Time | Memory |
|-----------|---------|---------------|------|--------|
| 1 KB | 9 | Middle | <1 ms | <5 MB |
| 20 KB | 150 | Middle | <5 ms | <5 MB |
| 150 KB | 1,000 | All same day | ~15 ms | <10 MB |
| 1.5 MB | 10,000 | Early (day 15/30) | ~50 ms | <15 MB |
| 1.5 MB | 10,000 | Late (day 1/30) | ~80 ms | <15 MB |

### Performance Characteristics

**Strengths:**
- ✅ Memory efficient (streaming, doesn't load entire file)
- ✅ Early-exit optimization for sorted logs
- ✅ O(1) lookups via Counter
- ✅ Single-pass algorithm

**Scalability:**
- Handles 10,000+ records easily
- Linear time complexity O(n) worst case
- Constant memory per unique cookie O(u)
- Suitable for log files up to several GB

## API Documentation

### Class: CookieLogAnalyzer

The main analyzer class for processing cookie log files.

#### Constructor

```python
CookieLogAnalyzer(log_file: Path)
```

**Parameters:**
- `log_file` (Path): Path to the cookie log CSV file

**Raises:**
- `FileNotFoundError`: If log file doesn't exist

**Example:**
```python
from pathlib import Path
from src.most_active_cookie import CookieLogAnalyzer

analyzer = CookieLogAnalyzer(Path("test_inputs/cookie_log.csv"))
```

#### Method: find_most_active_cookies

```python
find_most_active_cookies(target_date: str) -> List[str]
```

Find the most active cookie(s) for a specific date.

**Parameters:**
- `target_date` (str): Date string in YYYY-MM-DD format (UTC)

**Returns:**
- `List[str]`: Sorted list of cookie IDs with maximum visits. Empty list if no cookies found.

**Raises:**
- `ValueError`: If date format is invalid
- `IOError`: If file cannot be read

**Example:**
```python
cookies = analyzer.find_most_active_cookies("2018-12-09")
print(cookies)  # ['AtY0laUfhglK3lC7']
```

### Function: main

```python
main() -> int
```

Main entry point for the command-line tool.

**Returns:**
- `int`: Exit code (0 for success, 1 for error)

**Example:**
```python
import sys
from src.most_active_cookie import main

sys.argv = ['prog', '-f', 'cookie_log.csv', '-d', '2018-12-09']
exit_code = main()
```

## Logging

The application provides comprehensive logging for debugging and audit trails.

### Log Locations

- **File Logs**: `src/most_active_cookie Logs/YYYYMMDD_HHMMSS.txt`
- **Error Logs**: stderr (for ERROR and CRITICAL levels)

### Log Levels

| Level | Where | When |
|-------|-------|------|
| DEBUG | File only | Verbose mode (`-v` flag) - detailed parsing info |
| INFO | File only | Normal operations, results |
| WARNING | File only | Recoverable issues (malformed lines) |
| ERROR | File + stderr | Errors (file not found, invalid date) |
| CRITICAL | File + stderr | Unexpected exceptions |

### Log Format

```
2025-10-18 13:13:19,007 - __main__ - ERROR - Log file not found: missing.csv
```

Format: `timestamp - logger_name - level - message`

### Example Log Output

```
2025-10-18 12:47:49,884 - __main__ - INFO - Initialized analyzer with file: cookie_log.csv
2025-10-18 12:47:49,884 - __main__ - DEBUG - cookie_id: AtY0laUfhglK3lC7, parsed_date: 2018-12-09
2025-10-18 12:47:49,884 - __main__ - INFO - Found 1 cookie(s) with 2 occurrence(s) on 2018-12-09
```

## Contributing

### Development Setup

```bash
# Clone and setup
git clone https://github.com/shantanu747/Cookie-Analyzer.git
cd Cookie-Analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest -v

# Check code quality
ruff check .
mypy src/most_active_cookie.py
```

### Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public APIs
- Maintain test coverage above 85%
- Add tests for new features
- Update documentation

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

MIT License - See LICENSE file for details.

## Author

**Shantanu Patil**
- GitHub: [@shantanu747](https://github.com/shantanu747)

## Acknowledgments

- Python community for excellent tooling (pytest, ruff, mypy)
- Contributors and users of this project

---

**Need help?** See [QUICKSTART.md](QUICKSTART.md) or open an issue.
