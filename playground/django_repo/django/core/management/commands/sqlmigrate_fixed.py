import sys

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.core.management.sql import sql_flush
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader


class Command(BaseCommand):
    help = "Prints the SQL statements for the named migration."

    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument(
            "app_label",
            help="App label of the application containing the migration.",
        )
        parser.add_argument(
            "migration_name", help="Migration name to print the SQL for."
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help=(
                "Nominates a database to print the SQL for. Defaults to the "
                '"default" database.'
            ),
        )
        parser.add_argument(
            "--backwards",
            action="store_true",
            help="Creates SQL to unapply the migration, rather than to apply it",
        )

    def execute(self, *args, **options):
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        # Get the database we're operating from
        connection = connections[options["database"]]

        # Load up all migrations
        loader = MigrationLoader(connection)

        # Get the migration
        try:
            migration = loader.get_migration_by_prefix(
                options["app_label"], options["migration_name"]
            )
        except KeyError:
            raise CommandError(
                "Cannot find a migration matching '%s' from app '%s'. Is it in "
                "INSTALLED_APPS?" % (options["migration_name"], options["app_label"])
            )
        # Fixed: Check both migration.atomic and connection.features.can_rollback_ddl
        self.output_transaction = migration.atomic and connection.features.can_rollback_ddl

        # Make a plan that represents just the requested migration and print SQL for it
        plan = [(migration, options["backwards"])]
        sql_list = []
        for migration, backwards in plan:
            with connection.schema_editor(
                atomic=self.output_transaction, collect_sql=True
            ) as editor:
                if not backwards:
                    migration.apply(editor)
                else:
                    migration.unapply(editor)
                sql_list.extend(editor.collected_sql)

        # Display the SQL
        for sql in sql_list:
            self.stdout.write(sql)