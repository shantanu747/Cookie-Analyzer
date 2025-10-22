# Quick Start Guide

## Installation (5 minutes)

1. **Prerequisites**: Python 3.9+ installed

2. **Clone and setup**:
```bash
# Clone the repository
git clone https://github.com/shantanu747/Cookie-Analyzer.git
cd Cookie-Analyzer

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage Examples

### Basic Usage
```bash
# Find most active cookie for a specific day
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-09
```

Output:
```
AtY0laUfhglK3lC7
```

### With Verbose Logging
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-09 -v
```

### Different Date
```bash
python src/most_active_cookie.py -f test_inputs/cookie_log.csv -d 2018-12-08
```

Output (when there's a tie - order may vary):
```
SAZuXPGUrfbcn5UA
4sMM2LxV07bPJzwf
fbcn5UAVanZf6UtG
```

### Testing with Multiple Winners
```bash
# Test file with 3 cookies tied for most visits
python src/most_active_cookie.py -f test_inputs/cookie_log_1.csv -d 2018-12-15
```

Output (order may vary):
```
AtY0laUfhglK3lC7
SAZuXPGUrfbcn5UA
5UAVanZf6UtGyKVS
```

### Help
```bash
python src/most_active_cookie.py --help
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test class
pytest tests/test_most_active_cookie.py::TestCookieLogAnalyzer -v

# Run specific test
pytest tests/test_most_active_cookie.py::TestCookieLogAnalyzer::test_single_most_active_cookie -v
```

## Common Issues

### Issue: "No module named pytest"
**Solution**: Make sure you're in the virtual environment and ran `pip install -r requirements.txt`

### Issue: "Permission denied"
**Solution**: Make script executable: `chmod +x src/most_active_cookie.py`

### Issue: "File not found"
**Solution**: Check the file path is correct. Use absolute path if needed:
```bash
python src/most_active_cookie.py -f /full/path/to/cookie_log.csv -d 2018-12-09
```

### Issue: Log files filling up disk space
**Solution**: Log files are stored in `src/most_active_cookie Logs/`. Clean up old logs periodically:
```bash
rm -rf "src/most_active_cookie Logs"/*.txt
```

## Code Quality Checks

```bash
# Linting
ruff check .

# Type checking
mypy src/most_active_cookie.py

# Auto-format
ruff format .

# Run all quality checks
ruff check . && mypy src/most_active_cookie.py && pytest
```

## Project Structure
```
.
├── src/
│   ├── most_active_cookie.py         # Main script
│   └── most_active_cookie Logs/      # Log files (auto-created)
├── tests/
│   └── test_most_active_cookie.py    # Comprehensive test suite
├── test_inputs/
│   ├── cookie_log.csv                # Original sample data (9 rows)
│   ├── cookie_log_1.csv              # Test: Multiple cookies with same max (150 rows)
│   ├── cookie_log_2.csv              # Test: Performance - same day (1,000 rows)
│   └── cookie_log_3.csv              # Test: Large scale - 30 days (10,000 rows)
├── requirements.txt                  # Dependencies
├── pyproject.toml                    # Project config
├── QUICKSTART.md                     # This file
└── README.md                         # Documentation
```

## Test Input Files

The project includes multiple test input files for different scenarios:

| File | Rows | Purpose | Key Features |
|------|------|---------|-------------|
| `cookie_log.csv` | 9 | Original sample | Basic functionality test |
| `cookie_log_1.csv` | 150 | Edge case testing | 3 cookies tied for max, close competitors |
| `cookie_log_2.csv` | 1,000 | Performance test | All entries on same day, tests full file scan |
| `cookie_log_3.csv` | 10,000 | Scale test | 30 days of data, tests early-exit optimization |

### Example Test Runs

```bash
# Test with tie scenario (3 winners)
python src/most_active_cookie.py -f test_inputs/cookie_log_1.csv -d 2018-12-15

# Test performance with 1,000 records
python src/most_active_cookie.py -f test_inputs/cookie_log_2.csv -d 2018-12-10

# Test scale with 10,000 records
python src/most_active_cookie.py -f test_inputs/cookie_log_3.csv -d 2018-12-15
```

## Logging

The application logs all operations to files in `src/most_active_cookie Logs/`:
- **Normal operation**: INFO level messages logged to file
- **Errors**: Logged to both file AND stderr
- **Verbose mode** (`-v` flag): DEBUG level messages shown

Log file format: `YYYYMMDD_HHMMSS.txt`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review the code to understand the algorithm
- Try modifying the code to add new features
- Run the tests to see comprehensive examples
- Experiment with different test input files to understand edge cases
