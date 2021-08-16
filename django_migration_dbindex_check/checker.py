"""Checker for migrations files with a new db_index."""

import os
from operator import itemgetter


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
