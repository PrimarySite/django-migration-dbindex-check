"""Checker for migrations files with a new db_index."""

import ast
import configparser
import os, sys
from operator import itemgetter

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
        create_models = []
        alter_fields = []

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

                    create_models += [
                        x for x in assigns.value.elts if x.func.attr == "CreateModel"
                    ]

                    alter_fields += [
                        x for x in assigns.value.elts if x.func.attr == "AlterField"
                    ]

        return create_models, alter_fields

    def _check_for_db_index_in_field_object(self, field_object):
        """Check for db_index keyword in kwargs and return value."""
        dbindex = [x.value.value for x in field_object.keywords if x.arg == "db_index"]
        return dbindex[0] if len(dbindex) > 0 else False

    def _create_models_to_models_dict(
        self, models_dict: dict, create_models_list: list, migration_number: int
    ):
        """Turn a list of CreateModels classes to model dicts and add to overall dict."""

        for create_model in create_models_list:

            fields = {}
            try:
                model_name = [
                    x.value.value for x in create_model.keywords if x.arg == "name"
                ][0]
            except:
                model_name = [
                    x.value.s for x in create_model.keywords if x.arg == "name"
                ][0]

                fields_list = [x for x in create_model.keywords if x.arg == "fields"][0]

            for field in fields_list.value.elts:
                # This is now a list of tuples, first element is field ID, second is model class
                index_added = self._check_for_db_index_in_field_object(field.elts[1])
                fields[field.elts[0].value.lower()] = {
                    "is_index": index_added,
                    "index_added": migration_number if index_added else False,
                }

            models_dict[model_name.lower()] = fields

    def _alter_fields_to_models_dict(
        self,
        models_dict: dict,
        alter_fields_list: list,
        migration_number: int,
        strict_mode: bool,
    ):
        """
        Use the AlterField instances to mutate the models_dict.

        Strict mode is used here to determine whether to ignore potential broken migrations.
        If strict mode is on and we find an AlterField but there is no field in the dict,
        this will error.
        If strict mode is off, we'll just act as if we're creating the field from scratch.
        This helps for older codebases where migrations may have been corrupted.
        Looking at you, CMS....
        """
        for alter_field in alter_fields_list:
            model_name = [
                x.value.value for x in alter_field.keywords if x.arg == "model_name"
            ][0]
            field_name = [
                x.value.value for x in alter_field.keywords if x.arg == "name"
            ][0]
            field_object = [x.value for x in alter_field.keywords if x.arg == "field"][
                0
            ]
            is_index = self._check_for_db_index_in_field_object(field_object)

            try:
                models_dict[model_name][field_name]
            except KeyError:
                if strict_mode:
                    raise KeyError(
                        f"Cannot find the original model ({model_name}) or field ({field_name}) "
                        f"which is being changed. This most likely means your migrations are broken."
                    )
                else:
                    # This is now a list of tuples, first element is field ID, second is model class
                    models_dict[model_name][field_name.lower()] = {
                        "is_index": is_index,
                        "index_added": migration_number if is_index else False,
                    }

            if not models_dict[model_name][field_name]["is_index"] and is_index:
                models_dict[model_name][field_name]["index_added"] = migration_number

            models_dict[model_name][field_name]["is_index"] = is_index

    def _map_models(self, app_dict: dict, root_path: str, strict_mode: bool):
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
            (
                create_models,
                alter_fields,
            ) = self._get_all_relevant_operations_nodes_for_file(path)

            self._create_models_to_models_dict(
                models, create_models, migration_file[0][:4]
            )
            self._alter_fields_to_models_dict(
                models, alter_fields, migration_file[0][:4], strict_mode
            )

        return models

    def _analyse_models(self, app_dict: dict, ignore_before: int = 0):
        """
        Check for new db indices after a given migration for app.

        Returns a list of errors for new indeces.
        """
        errors = []
        for model in app_dict.keys():
            for field_name in app_dict[model].keys():
                field = app_dict[model][field_name]
                if field["is_index"] and int(field["index_added"]) >= ignore_before:
                    errors.append(
                        {
                            "model": model,
                            "field": field_name,
                            "migration": field["index_added"],
                        }
                    )

        return errors

    def get_config(self, project_root: str):
        """Get any config from a '.migrations_check_config.cfg file."""
        config = configparser.ConfigParser()

        # Failed reads are ignored
        full_path = os.path.join(os.getcwd(), project_root, "migrations_check.cfg")
        config.read(full_path)
        return config

    def check_project(self, project_root_dir: str):
        apps = self._walk_files(project_root_dir)
        config = self.get_config(project_root_dir)
        errors = []

        for app in apps.keys():
            models = self._map_models(
                app_dict=apps[app], root_path=os.getcwd(), strict_mode=False
            )

            try:
                ignore_before = config["DJANGO_MIGRATION_DBINDEX_CHECK"][app]
            except KeyError:
                ignore_before = 0

            errors_new = self._analyse_models(models, int(ignore_before))
            for items in errors_new:
                items["app"] = app
            errors += errors_new

        for error in errors:
            print(
                f"A new db_index was added to field:{error['field']} in model:{error['model']} "
                f"in app:{error['app']}. This was added in migration {error['migration']}.",
                file=sys.stderr
            )

