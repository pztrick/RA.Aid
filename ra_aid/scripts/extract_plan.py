from typing import Optional
import peewee
from ra_aid.database.models import Session
from ra_aid.database.connection import DatabaseManager # Changed import

def get_plan_for_session(session_id: int, project_state_dir: Optional[str] = None) -> str | None:
    """
    Extracts the plan for a given session ID from the database.

    Args:
        session_id: The ID of the session.

    Returns:
        The plan as a string, or None if not found.
    """
    # Initialize database connection using DatabaseManager context
    with DatabaseManager(base_dir=project_state_dir) as db:
        try:
            session = Session.get_by_id(session_id)
            return session.plan
        except peewee.DoesNotExist:
            return None

if __name__ == "__main__":
    # This __main__ block is for direct script execution,
    # not used when called as a module function.
    # Replace with the actual session ID you want to inspect
    session_id_to_check = 1 # Example session ID
    # Example project_state_dir, normally None or path to .ra-aid parent
    project_dir = None
    plan = get_plan_for_session(session_id_to_check, project_state_dir=project_dir)

    if plan:
        print(f"Plan for session {session_id_to_check}:")
        print(plan)
    else:
        print(f"No plan found for session {session_id_to_check}.")
