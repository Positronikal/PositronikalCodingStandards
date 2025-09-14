#!/usr/bin/env python3
"""
Command-line interface for Positronikal Standards Checker.
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Add parent directory to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from positronikal_standards_check import PositronikalStandardsChecker


def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s"
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate repository compliance with Positronikal coding standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all standards in current directory
  positronikal-check .
  
  # Check specific repository
  positronikal-check /path/to/repo
  
  # Check only file requirements
  positronikal-check . --check files
  
  # Include forensic tool standards
  positronikal-check . --forensic
  
  # Verbose output showing all passing checks
  positronikal-check . --verbose
  
  # Use custom configuration
  positronikal-check . --config custom-standards.yaml
  
  # Exit with non-zero status on failure
  positronikal-check . --strict

Available check types:
  all      - Run all standard checks (default)
  files    - Check file requirements only
  build    - Check build system only
  code     - Check code formatting standards only
  security - Check security requirements only
  forensic - Check forensic tool standards only
        """
    )
    
    parser.add_argument(
        "repository",
        help="Path to repository to validate (default: current directory)",
        nargs="?",
        default="."
    )
    
    parser.add_argument(
        "--check",
        choices=["all", "files", "build", "code", "security", "forensic"],
        default="all",
        help="Type of checks to run (default: all)"
    )
    
    parser.add_argument(
        "--forensic",
        action="store_true",
        help="Include forensic tool standards in validation"
    )
    
    parser.add_argument(
        "--config",
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including passing checks"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any checks fail"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if not args.quiet:
        setup_logging(args.verbose)
    else:
        logging.disable(logging.CRITICAL)
        
    # Set environment variable for verbose output
    if args.verbose:
        os.environ["VERBOSE"] = "true"
        
    try:
        # Initialize checker
        checker = PositronikalStandardsChecker(
            args.repository,
            config_path=args.config
        )
        
        # Run appropriate checks
        if args.check == "all":
            results = checker.check_all(include_forensic=args.forensic)
        elif args.check == "files":
            results = checker.check_files()
        elif args.check == "build":
            results = checker.check_build()
        elif args.check == "code":
            results = checker.check_code()
        elif args.check == "security":
            results = checker.check_security()
        elif args.check == "forensic":
            results = checker.check_forensic()
        else:
            print(f"Unknown check type: {args.check}", file=sys.stderr)
            sys.exit(1)
            
        # Output results
        if args.json:
            import json
            output = {
                "repository": str(checker.repo_path),
                "summary": results.get_summary(),
                "passed": results.passed,
                "failed": results.failed,
                "warnings": results.warnings,
                "errors": results.errors
            }
            print(json.dumps(output, indent=2))
        elif not args.quiet:
            results.print_report()
            
        # Exit with appropriate code
        if args.strict and not results.is_passing:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()