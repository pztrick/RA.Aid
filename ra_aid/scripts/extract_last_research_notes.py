import sys
from pathlib import Path

# Add project root to the Python path
# This is necessary for the script to be runnable directly
# and to be able to import from the ra_aid package.
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from ra_aid.database.connection import DatabaseManager
from ra_aid.database.repositories.session_repository import SessionRepositoryManager
from ra_aid.database.repositories.research_note_repository import ResearchNoteRepositoryManager


def main():
    """
    Extracts research notes from the latest session and prints them to standard output.
    """
    db_manager = DatabaseManager()
    with db_manager as db:
        with SessionRepositoryManager(db) as session_repo:
            latest_session = session_repo.get_latest_session()

            if not latest_session:
                print("No sessions found.", file=sys.stderr)
                return

            with ResearchNoteRepositoryManager(db) as research_note_repo:
                notes = research_note_repo.get_notes_by_session(latest_session.id)
                if notes:
                    for note in notes:
                        print(f"## Research Note {note.id}")
                        print(f"**Created At:** {note.created_at}")
                        print("---")
                        print(note.content)
                        print("---")
                else:
                    print("No research notes found for the latest session.", file=sys.stderr)


if __name__ == "__main__":
    main()
