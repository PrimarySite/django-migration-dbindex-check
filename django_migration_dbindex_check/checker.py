"""Checker for migrations files with a new db_index."""

import ast
import os
from operator import itemgetter
from pathlib import Path

import parso


class DBIndexChecker:
    """Check and report on migrations with a new db_index."""

    def _walk_files(self, root_path: str):
        """
        Find all migrations files within the given path.
        Assumes that the standard django rules are followed, i.e:
         - There are a number of app folders, each containing a directory called migrations.
         - The migrations folder contains a number of .py files beginning with a four digit integer.

        returns a list of dicts of all migration files:
            {
                "<app_name>": {
                    "migration_files": [
                        ["0001_initial_migrations.py", <full_filepath>],
                        ["0002_added_a_new_model.py", <full_filepath>],
                        ["0003_added_a_new_field.py", <full_filepath>],
                        ...
                    ]
                }
            }
        """
        apps_list = {}
        for root, dirs, files in os.walk(root_path):
            if root.split(os.sep)[-1] != "migrations":
                continue

            app_name = root.split(os.sep)[-2]
            if app_name not in apps_list.keys():
                apps_list[app_name] = {"migration_files": []}

            for file in files:
                # Migration files start with a four digit integer
                try:
                    int(file[:4])
                except ValueError:
                    continue

                if file in [x[0] for x in apps_list[app_name]["migration_files"]]:
                    continue

                apps_list[app_name]["migration_files"].append(
                    [file, os.path.join(root, file)]
                )

            apps_list[app_name]["migration_files"].sort(key=itemgetter(0))

        return apps_list

    def _get_all_relevant_operations_nodes_for_file(self, file_path):
        """Get all the classes within the operations list for a given file."""
        relevant_nodes = []

        with open(file_path) as file:
            node = ast.parse(file.read())
            classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

            for cls in classes:
                # There should only be one of these per file, but loop anyway
                if cls.name != "Migration":
                    continue

                # We're looking for two types of class, either migrations.CreateModel
                # or migrations.AlterField. Check for both and parse each case
                for assigns in [n for n in cls.body if isinstance(n, ast.Assign)]:
                    if assigns.targets[0].id != "operations":
                        continue

                    return [
                        x
                        for x in assigns.value.elts
                        if x.func.attr == "CreateModel" or x.func.attr == "AlterField"
                    ]

    def _map_models(self, app_dict: dict, root_path: str):
        """
        Re-create the models and fields from the migration files of a given app.

        returns a dict of dicts:
        {
            model_name: {
                "field_name": {
                    is_index=True,   <- As of latest migration
                    index_added=0031,   <- Migration numbe
                },
                ...
            },
            ...
        }
        """
        models = {}

        if "migration_files" not in app_dict.keys():
            raise ValueError(
                "There are no migrations files in this app. Have you passed the "
                "all_apps dict instead of a specific app instance?"
            )

        for migration_file in app_dict["migration_files"]:
            path = os.path.join(root_path, migration_file[1])
            nodes = self._get_all_relevant_operations_nodes_for_file(path)
