"""
Command-line interface for managing database migrations.

This script provides a simple CLI to interact with the MigrationManager,
allowing for the creation, application, and status checking of migrations.
"""

import sys

from rich.console import Console
from rich.table import Table

from ra_aid.database.migrations import (
    create_new_migration,
    ensure_migrations_applied,
    get_migration_status,
)


def main():
    """Main function to handle migration commands."""
    console = Console()
    if len(sys.argv) < 2:
        console.print(
            "[bold red]Error:[/bold red] No command specified. Use 'create', 'migrate', or 'status'."
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 3:
            console.print("[bold red]Error:[/bold red] Migration name not specified.")
            console.print(
                "Usage: make migrate-create name=<migration_name>"
            )
            sys.exit(1)
        name = sys.argv[2]
        console.print(f"Creating migration: [cyan]{name}[/cyan]")
        result = create_new_migration(name, auto=True)
        if result:
            console.print(
                f"[bold green]Successfully created migration:[/bold green] {result}"
            )
        else:
            console.print("[bold red]Failed to create migration.[/bold red]")
            sys.exit(1)

    elif command == "migrate":
        console.print("Applying pending migrations...")
        success = ensure_migrations_applied()
        if success:
            console.print(
                "[bold green]Migrations applied successfully (or no pending migrations).[/bold green]"
            )
        else:
            console.print("[bold red]Failed to apply migrations.[/bold red]")
            sys.exit(1)

    elif command == "status":
        console.print("Checking migration status...")
        status = get_migration_status()
        if "error" in status:
            console.print(
                f"[bold red]Error getting status:[/bold red] {status['error']}"
            )
            sys.exit(1)

        table = Table(title="Migration Status")
        table.add_column("Status", justify="right", style="cyan", no_wrap=True)
        table.add_column("Count", justify="left", style="magenta")

        table.add_row("Applied", str(status.get("applied_count", 0)))
        table.add_row("Pending", str(status.get("pending_count", 0)))

        console.print(table)

        if status.get("pending"):
            console.print("\n[bold yellow]Pending Migrations:[/bold yellow]")
            for p in status["pending"]:
                console.print(f"- {p}")
    else:
        console.print(
            f"[bold red]Error:[/bold red] Unknown command '{command}'. Use 'create', 'migrate', or 'status'."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
