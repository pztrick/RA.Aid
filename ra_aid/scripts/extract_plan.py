import peewee
from ra_aid.database import DatabaseManager
from ra_aid.database.repositories.session_repository import SessionRepositoryManager
import argparse
import sys


def get_plan_for_session(session_id: int | None = None) -> tuple[str | None, int | None]:
    """
    Extracts the plan for a given session ID from the database.
    If session_id is None, it fetches the plan for the latest session.

    Args:
        session_id: The ID of the session, or None for the latest.

    Returns:
        A tuple containing (plan as a string, actual_session_id).
        If a specific session is not found, returns (None, session_id).
        If no sessions exist when fetching latest, returns (None, None).
    """
    try:
        with DatabaseManager() as db:
            with SessionRepositoryManager(db) as session_repo:
                if session_id is None:
                    # Get the latest session using the repository
                    session = session_repo.get_latest_session()
                    if session is None:
                        # No sessions found in the database
                        return None, None
                else:
                    # Get session by specific ID using the repository
                    session = session_repo.get_session_by_id(session_id)

                return session.plan, session.id
    except peewee.DoesNotExist:
        # This will catch the error if get_session_by_id does not find a session
        return None, session_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract the plan for a given session. Defaults to the latest session.")
    parser.add_argument("session_id", nargs='?', default=None, help="The ID of the session. If omitted, the latest session is used.")
    args = parser.parse_args()

    session_id_to_fetch = args.session_id
    if session_id_to_fetch is not None:
        try:
            session_id_to_fetch = int(session_id_to_fetch)
        except ValueError:
            print(f"Error: session_id must be an integer. Got '{session_id_to_fetch}'", file=sys.stderr)
            sys.exit(1)

    plan, found_session_id = get_plan_for_session(session_id_to_fetch)

    if plan:
        print(f"Plan for session {found_session_id}:")
        print(plan)
    else:
        if found_session_id is None:
            print("No sessions found in the database.")
        else:
            print(f"No plan found for session {found_session_id}.")
