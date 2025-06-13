import peewee
from peewee_migrate import Migrator


def migrate(migrator: Migrator, database: peewee.Database, fake=False, **kwargs):
    columns = [col.name for col in database.get_columns("session")]
    if "plan" not in columns:
        field = peewee.TextField(null=True)
        migrator.add_fields("session", plan=field)


def rollback(migrator: Migrator, database: peewee.Database, fake=False, **kwargs):
    columns = [col.name for col in database.get_columns("session")]
    if "plan" in columns:
        migrator.remove_fields("session", "plan")
