"""
Most Active Cookie Analyzer

Command-line tool to find the most active cookie(s) for a specific day
from a cookie log file.

Author: Shantanu Patil
Date: October 18, 2025
"""

import argparse
import logging
import sys
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Configure logging
log_folder = os.path.join(os.path.dirname(__file__), "most_active_cookie Logs")
if not os.path.exists(log_folder):
    os.makedirs(log_folder, exist_ok=True)

log_file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file_path = os.path.join(log_folder, log_file_name)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_file_path
)
logger = logging.getLogger(__name__)

# Add stderr handler for ERROR and CRITICAL level messages
# This is for good UNIX behavior of outputs going to stdout and errors/criticals
# going to stderr
# Use stream=None to get sys.stderr dynamically, which helps with pytest capsys
stderr_handler = logging.StreamHandler()  # Defaults to sys.stderr
stderr_handler.setLevel(logging.ERROR)
stderr_formatter = logging.Formatter('Error: %(message)s')
stderr_handler.setFormatter(stderr_formatter)
logger.addHandler(stderr_handler)

class CookieLogAnalyzer:
    """Analyzes cookie log files to find most active cookies."""
    
    DATE_FORMAT = "%Y-%m-%d"
    TIMESTAMP_FORMAT_WITH_TZ = "%Y-%m-%dT%H:%M:%S%z"
    
    def __init__(self, log_file: Path):
        """
        Initialize the analyzer with a log file.
        
        Args:
            log_file: Path to the cookie log CSV file
            
        Raises:
            FileNotFoundError: If log file doesn't exist
        """
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        self.log_file = log_file
        logger.info(f"Initialized analyzer with file: {log_file}")
    
    def find_most_active_cookies(self, target_date: str) -> List[str]:
        """
        Find the most active cookie(s) for a specific date.
        
        Since the log is sorted by timestamp (most recent first), we can
        optimize by stopping once we've passed the target date.
        
        Args:
            target_date: Date string in YYYY-MM-DD format (UTC)
            
        Returns:
            List of cookie IDs that were most active on the target date.
            Returns empty list if no cookies found for that date.
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            # Validate date format
            datetime.strptime(target_date, self.DATE_FORMAT)
        except ValueError as e:
            raise ValueError(
                f"Invalid date format '{target_date}'. Expected YYYY-MM-DD"
            ) from e
        
        # initialize our Counter container for keeping track of each cookie on date
        # could also use defaultdict(int)
        cookie_counts = Counter()
        found_target_date = False
        
        # Ideally I would use pandas read_csv here but we're trying not to make it too easy
        try:
            with open(self.log_file, 'r', encoding='utf-8') as file:
                # Skip header line
                header = file.readline().strip()
                if not header:
                    logger.warning("Empty file")
                    return []
                
                # the following block might need to change if we might expect CSVs in different structures
                # with similar content 
                if header != "cookie,timestamp":
                    logger.warning(f"Unexpected header: {header}")
                
                # start parsing the main data part of our file
                for line_num, line in enumerate(file, start=2):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        cookie_id, timestamp_str = self._parse_line(line)
                        log_date = self._extract_date(timestamp_str)
                        logger.debug(f"cookie_id: {cookie_id}, parsed_date: {log_date}")
                        
                        if log_date == target_date:
                            # found a cookie id on our desired day - increment its counter
                            logger.debug(f"cookie_id: {cookie_id} was added to Counter")
                            cookie_counts[cookie_id] += 1
                            found_target_date = True
                        elif log_date < target_date:
                            # Since log is sorted newest first, we can stop
                            # once we hit dates before our target
                            logger.debug(f"Reached dates before target at line {line_num}, stopping")
                            break
                        # If log_date > target_date, continue searching
                        
                    except ValueError as e:
                        logger.warning(f"Skipping invalid line {line_num}: {e}")
                        continue
        
        except IOError as e:
            logger.error(f"Error reading file: {e}")
            raise
        
        if not found_target_date:
            logger.info(f"No cookies found for date: {target_date}")
            return []
        
        # Find maximum count
        max_count = max(cookie_counts.values())
        most_active = [
            cookie for cookie, count in cookie_counts.items() 
            if count == max_count
        ]
        
        logger.info(
            f"Found {len(most_active)} cookie(s) with {max_count} "
            f"occurrence(s) on {target_date}"
        )
        
        return sorted(most_active)  # Sort for consistent output
    
    def _parse_line(self, line: str) -> tuple[str, str]:
        """
        Parse a log line into cookie ID and timestamp.
        
        Args:
            line: Raw line from log file
            
        Returns:
            Tuple of (cookie_id, timestamp_string)
            
        Raises:
            ValueError: If line format is invalid
        """
        parts = line.split(',', maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Invalid line format: {line}")
        
        cookie_id, timestamp = parts
        
        if not cookie_id or not timestamp:
            raise ValueError("Cookie ID or timestamp is empty")
        
        return cookie_id.strip(), timestamp.strip()
    
    def _extract_date(self, timestamp_str: str) -> str:
        """
        Extract date from timestamp string.
        
        Args:
            timestamp_str: ISO 8601 timestamp with timezone
            
        Returns:
            Date string in YYYY-MM-DD format
            
        Raises:
            ValueError: If timestamp format is invalid
        """
        try:
            # Parse timestamp with timezone
            dt = datetime.strptime(timestamp_str, self.TIMESTAMP_FORMAT_WITH_TZ)
            return dt.strftime(self.DATE_FORMAT)
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Find the most active cookie for a specific day",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -f cookie_log.csv -d 2018-12-09
  %(prog)s --file cookie_log.csv --date 2018-12-09 --verbose
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        type=Path,
        required=True,
        metavar='FILENAME',
        help='Path to the cookie log CSV file'
    )
    
    parser.add_argument(
        '-d', '--date',
        type=str,
        required=True,
        metavar='YYYY-MM-DD',
        help='Target date in YYYY-MM-DD format (UTC)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the command-line tool.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    logger.debug("Parsing command line arguments...")
    args = parse_arguments()
    
    # Adjust logging level based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.getLogger().setLevel(log_level)
    logger.debug("Arguments: file=%s, date=%s", args.file, args.date)
    
    try:
        # Initialize CookieLogAnalyzer with provided file
        analyzer = CookieLogAnalyzer(args.file)
        # return most active cookie(s)
        most_active_cookies = analyzer.find_most_active_cookies(args.date)
        
        # Output results to stdout
        for cookie in most_active_cookies:
            print(cookie)
            logger.info(f"Returned cookie: {cookie}")
        
        # all went well
        # return 0 because it is good coding practice for running on Unix/Linux envs
        # helpful in CLI tools for CRON jobs, CI/CD, monitoring, or orchestration
        return 0
        
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        logger.error(str(e))
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"Error: An unexpected error occurred: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())