import sys
from pathlib import Path
from typing import Optional

# Add project root to the Python path
# This is necessary for the script to be runnable directly
# and to be able to import from the ra_aid package.
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from ra_aid.database.connection import DatabaseManager
from ra_aid.database.repositories.session_repository import SessionRepositoryManager


def main(project_state_dir: Optional[str] = None):
    """
    Extracts the plan from the latest session and prints it to standard output.
    """
    db_manager = DatabaseManager(base_dir=project_state_dir)
    with db_manager as db:
        with SessionRepositoryManager(db) as repo:
            # get_latest_session() is suitable here as it fetches the most
            # recent session record from the database.
            latest_session = repo.get_latest_session()

            if latest_session and latest_session.plan:
                print(latest_session.plan)
            else:
                print("No plan found for the latest session.", file=sys.stderr)


if __name__ == "__main__":
    main()
