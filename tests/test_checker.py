# -*- coding: utf-8 -*-
"""Tests for the checker class."""
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile

from django_migration_dbindex_check.checker import DBIndexChecker


class TestWalkFiles(TestCase):
    """Tests for the _walk_files function."""

    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work

    def test_walk_files_returns_correct_files(self):
        """Function should return the correct data from the sample files."""
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
                        "0002_renamed_a_field.py",
                        "example_migrations/important_functionality/migrations"
                        "/0002_renamed_a_field.py",
                    ],
                    [
                        "0003_added_new_field_db_index.py",
                        "example_migrations/important_functionality/migrations/"
                        "0003_added_new_field_db_index.py",
                    ],
                ],
            },
            "other_service": {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/other_service/"
                        "migrations/0001_initial_migrations.py",
                    ],
                    [
                        "0002_did_some_stuff.py",
                        "example_migrations/other_service/"
                        "migrations/0002_did_some_stuff.py",
                    ],
                ],
            },
            "the_app": {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/the_app/" "migrations/0001_initial_migrations.py",
                    ],
                    [
                        "0002_added_index_to_existing_field.py",
                        "example_migrations/the_app/"
                        "migrations/0002_added_index_to_existing_field.py",
                    ],
                ],
            },
        }


class TestGetAllRelevantOperations(TestCase):
    """Tests for the _get_all_relevant_operations_nodes_for_file."""

    def setUp(self) -> None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work

    def test_function_returns_the_correct_create_model_nodes_for_example_file(self):
        """Should return the correct CreateModel nodes for the example file."""
        checker = DBIndexChecker()
        create_models, alter_fields, add_fields = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py"
        )

        model_names = []
        for create_model in create_models:
            assert create_model.func.attr == "CreateModel"
            try:
                model_name = [x.value.value for x in create_model.keywords if x.arg == "name"][0]
            except AttributeError:
                model_name = [x.value.s for x in create_model.keywords if x.arg == "name"][0]
            model_names.append(model_name)

        assert model_names == [
            'Change_Actual',
            "Change_Signoffs",
            "Change_Signoffs_Required",
            "Change_Status",
            "Change_Type",
        ]

    def test_function_returns_the_correct_alter_field_nodes_for_example_file(self):
        """Should return the correct AlterField nodes for the example file."""
        checker = DBIndexChecker()
        create_models, alter_fields, add_fields = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py"
        )

        model_names = []
        for alter_field in alter_fields:
            assert alter_field.func.attr == "AlterField"

            try:
                model_name = [
                    x.value.value for x in alter_field.keywords if x.arg == "model_name"
                ][0]
            except AttributeError:
                model_name = [x.value.s for x in alter_field.keywords if x.arg == "model_name"][0]

            try:
                field_name = [x.value.value for x in alter_field.keywords if x.arg == "name"][0]
            except AttributeError:
                field_name = [x.value.s for x in alter_field.keywords if x.arg == "name"][0]

            model_names.append([model_name, field_name])

        assert model_names == [
            ['change_actual', "Variants_affected"],
        ]

    def test_function_returns_the_correct_add_field_nodes_for_example_file(self):
        """Should return the correct AddField nodes for the example file."""
        checker = DBIndexChecker()
        create_models, alter_fields, add_fields = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py"
        )

        model_names = []
        for add_field in add_fields:
            assert add_field.func.attr == "AddField"

            try:
                model_name = [
                    x.value.value for x in add_field.keywords if x.arg == "model_name"
                ][0]
            except AttributeError:
                model_name = [x.value.s for x in add_field.keywords if x.arg == "model_name"][0]

            try:
                field_name = [x.value.value for x in add_field.keywords if x.arg == "name"][0]
            except AttributeError:
                field_name = [x.value.s for x in add_field.keywords if x.arg == "name"][0]

            model_names.append([model_name, field_name])

        assert model_names == [
            ['change_signoffs_required', "Parent_Change_Type"],
            ['change_signoffs_required', "Signoff_Pay_Grade_Required"],
            ['change_actual', "Change_Type"],
            ['change_actual', "Lines_Affected"],
            ['change_actual', "Machines_Affected"],
            ['change_actual', "Operations_Affected"],
            ['change_actual', "Status"],
            ['change_actual', "Variants_Affected"],
        ]

    def test_function_ignores_classes_that_are_not_migrations(self):
        """If there are other classes in the file, ignore them."""

        checker = DBIndexChecker()
        create_models, alter_fields, add_fields = checker._get_all_relevant_operations_nodes_for_file(
            "./specific_test_migrations/function_ignores_classes_that_are_not_migrations.py"
        )
        assert len(create_models) == 1
        try:
            model_name = [x.value.value for x in create_models[0].keywords if x.arg == "name"][0]
        except AttributeError:
            model_name = [x.value.s for x in create_models[0].keywords if x.arg == "name"][0]
        assert model_name == "Change_Actual"


class TestCheckForDBIndexInFieldObject(TestCase):
    def setUp(self) -> None:
        """Create a fake field object"""
        self.field_object = MagicMock()
        self.field_object.keywords = [
            MagicMock(value=MagicMock(value=False)),
        ]
        self.field_object.keywords[0].arg = "db_index"

    def test_function_returns_false_if_db_index_is_false(self):
        """Function should return False if db_index=False explicitly."""
        checker = DBIndexChecker()
        result = checker._check_for_db_index_in_field_object(self.field_object)
        assert result is False

    def test_function_returns_true_if_db_index_is_true(self):
        """Function should return False if db_index=True explicitly."""
        checker = DBIndexChecker()
        self.field_object.keywords[0].value.value = True
        result = checker._check_for_db_index_in_field_object(self.field_object)
        assert result is True

    def test_function_returns_false_of_no_db_index_kwarg(self):
        """Function should return False if there is no db_index kwarg."""
        checker = DBIndexChecker()
        self.field_object.keywords[0].value.value = True
        self.field_object.keywords[0].arg = "not_db_index"
        result = checker._check_for_db_index_in_field_object(self.field_object)
        assert result is False


class TestCreateModelsToModelsDict(TestCase):
    pass


