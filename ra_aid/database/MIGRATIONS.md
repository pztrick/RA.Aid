# Database Migrations with Peewee-Migrate

This project uses `peewee-migrate` to manage database schema changes. A custom `MigrationManager` and helper scripts are provided to simplify the process and ensure it works correctly within the application's context.

## Why Migrations?

When you change a database model in `ra_aid/database/models.py` (e.g., add a new field to the `Session` model), the database schema needs to be updated to reflect that change. Migrations are version-controlled scripts that apply these changes incrementally and reversibly. This ensures that all developers and production environments have a consistent database schema.

## How to Use Migrations

All migration commands are run through `make`.

### Checking Migration Status

Before making changes, it's good practice to see if there are any pending migrations.

```bash
make migrate-status
```

This command will show you how many migrations have been applied and how many are pending.

### Creating a New Migration

After you have changed a model in `ra_aid/database/models.py`, you need to create a migration file that contains the instructions to alter the database.

1.  **Modify your model file(s)** (e.g., add a `TextField` to a model).

2.  **Run the `migrate-create` command**, giving your migration a descriptive name.

    ```bash
    make migrate-create name=add_plan_to_session_model
    ```

    *   Use a short, descriptive, snake_case name.
    *   This command uses the `MigrationManager`'s auto-discovery feature to inspect your models and generate the migration script automatically.
    *   A new migration file will be created in `ra_aid/database/migrations/`. You should commit this file to version control.

### Applying Migrations

To apply all pending migrations to your local database, run:

```bash
make migrate
```

This command will:
1.  Check for any migration scripts that haven't been run yet.
2.  Execute them in order to update your database schema.
3.  The application automatically runs this on startup to ensure the database is always up-to-date.

## The Workflow in Practice

Here is a typical workflow:

1.  Pull the latest changes from the main branch.
2.  Run `make migrate` to apply any new migrations from other developers.
3.  Make your changes to a model in `ra_aid/database/models.py`.
4.  Run `make migrate-create name=my_descriptive_change` to generate a new migration file.
5.  Commit your model changes and the new migration file.
6.  Push your changes.
