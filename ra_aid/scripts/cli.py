#!/usr/bin/env python3
"""
Command-line interface for RA.Aid scripts.

This module provides command-line entry points for various RA.Aid utilities.
"""

import sys
import json
import argparse
from ra_aid.scripts.last_session_usage import get_latest_session_usage
from ra_aid.scripts.all_sessions_usage import get_all_sessions_usage
from ra_aid.scripts.extract_plan import get_plan_for_session


def run_latest_session_usage(args):
    """
    Handles the 'latest' command.
    """
    result, status_code = get_latest_session_usage(
        project_dir=args.project_dir,
        db_path=args.db_path
    )
    print(json.dumps(result, indent=2))
    return status_code

def run_all_sessions_usage(args):
    """
    Handles the 'all' command.
    """
    results, status_code = get_all_sessions_usage(
        project_dir=args.project_dir,
        db_path=args.db_path
    )
    print(json.dumps(results, indent=2))
    return status_code

def run_extract_plan(args):
    """
    Handles the 'extract-plan' command.
    """
    plan = get_plan_for_session(args.session_id)
    if plan:
        print(f"Plan for session {args.session_id}:")
        print(plan)
    else:
        print(f"No plan found for session {args.session_id}.")
    return 0

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="RA.Aid utility scripts")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # latest session command
    parser_latest = subparsers.add_parser("latest", help="Get usage statistics for the latest session")
    parser_latest.add_argument("--project-dir", help="Directory containing the .ra-aid folder (defaults to current directory)")
    parser_latest.add_argument("--db-path", help="Direct path to the database file (takes precedence over project-dir)")
    parser_latest.set_defaults(func=run_latest_session_usage)

    # all sessions command
    parser_all = subparsers.add_parser("all", help="Get usage statistics for all sessions")
    parser_all.add_argument("--project-dir", help="Directory containing the .ra-aid folder (defaults to current directory)")
    parser_all.add_argument("--db-path", help="Direct path to the database file (takes precedence over project-dir)")
    parser_all.set_defaults(func=run_all_sessions_usage)

    # extract-plan command
    parser_extract_plan = subparsers.add_parser(
        "extract-plan", help="Extract the plan for a given session."
    )
    parser_extract_plan.add_argument(
        "session_id", type=int, help="The ID of the session."
    )
    parser_extract_plan.set_defaults(func=run_extract_plan)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
