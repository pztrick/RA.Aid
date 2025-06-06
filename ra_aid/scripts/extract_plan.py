import peewee
from ra_aid.database.models import Session, initialize_database
import argparse

def get_plan_for_session(session_id: int) -> str | None:
    """
    Extracts the plan for a given session ID from the database.

    Args:
        session_id: The ID of the session.

    Returns:
        The plan as a string, or None if not found.
    """
    initialize_database()
    try:
        session = Session.get_by_id(session_id)
        return session.plan
    except peewee.DoesNotExist:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract the plan for a given session.")
    parser.add_argument("session_id", type=int, help="The ID of the session to extract the plan for.")
    args = parser.parse_args()

    plan = get_plan_for_session(args.session_id)

    if plan:
        print(f"Plan for session {args.session_id}:")
        print(plan)
    else:
        print(f"No plan found for session {args.session_id}.")
