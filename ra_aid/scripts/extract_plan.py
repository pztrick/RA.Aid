import peewee
from ra_aid.database.models import Session, initialize_database

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
    # Replace with the actual session ID you want to inspect
    session_id_to_check = 1
    plan = get_plan_for_session(session_id_to_check)

    if plan:
        print(f"Plan for session {session_id_to_check}:")
        print(plan)
    else:
        print(f"No plan found for session {session_id_to_check}.")
