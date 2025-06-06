import peewee
from peewee_migrate import Migrator

def migrate(migrator: Migrator, database: peewee.Database, fake=False, **kwargs):
    field = peewee.TextField(null=True)
    migrator.add_fields('session', plan=field)


def rollback(migrator: Migrator, database: peewee.Database, fake=False, **kwargs):
    migrator.remove_fields('session', 'plan')
