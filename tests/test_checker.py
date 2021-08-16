"""Tests for the checker class."""
import os

from django_migration_dbindex_check.checker import DBIndexChecker


class TestChecker:
    def test_walk_files(self):
        checker = DBIndexChecker()
        result = checker._walk_files("example_migrations")

        assert result == {
            "important_functionality": {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/important_functionality/"
                        "migrations/0001_initial_migrations.py",
                    ],
                    [
                        "0002_added_some_new_field.py",
                        "example_migrations/important_functionality/migrations"
                        "/0002_added_some_new_field.py",
                    ],
                    [
                        "0003_added_new_field_db_index.py",
                        "example_migrations/important_functionality/migrations/"
                        "0003_added_new_field_db_index.py",
                    ],
                ]
            },
            "other_service": {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/other_service/"
                        "migrations/0001_initial_migrations.py",
                    ],
                ]
            },
            "the_app": {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/the_app/"
                        "migrations/0001_initial_migrations.py",
                    ],
                    [
                        "0002_added_index_to_existing_field.py",
                        "example_migrations/the_app/"
                        "migrations/0002_added_index_to_existing_field.py",
                    ],
                ]
            },
        }

    def test_map_models(self):
        checker = DBIndexChecker()
        checker.check_project("example_migrations")
