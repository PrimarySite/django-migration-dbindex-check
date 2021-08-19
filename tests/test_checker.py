# -*- coding: utf-8 -*-
"""Tests for the checker class."""
import configparser
import os
from configparser import ConfigParser
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from django_migration_dbindex_check.checker import DBIndexChecker


class TestWalkFiles(TestCase):
    """Tests for the _walk_files function."""

    def setUp(self) -> None:  # noqa: D102
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
                        "example_migrations/other_service/" "migrations/0002_did_some_stuff.py",
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

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work

    def test_function_returns_the_correct_create_model_nodes_for_example_file(self):
        """Should return the correct CreateModel nodes for the example file."""
        checker = DBIndexChecker()
        (
            create_models,
            alter_fields,
            add_fields,
        ) = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py",
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
            "Change_Actual",
            "Change_Signoffs",
            "Change_Signoffs_Required",
            "Change_Status",
            "Change_Type",
        ]

    def test_function_returns_the_correct_alter_field_nodes_for_example_file(self):
        """Should return the correct AlterField nodes for the example file."""
        checker = DBIndexChecker()
        (
            create_models,
            alter_fields,
            add_fields,
        ) = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py",
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
            ["Change_Actual", "Change_Initiator"],
        ]

    def test_function_returns_the_correct_add_field_nodes_for_example_file(self):
        """Should return the correct AddField nodes for the example file."""
        checker = DBIndexChecker()
        (
            create_models,
            alter_fields,
            add_fields,
        ) = checker._get_all_relevant_operations_nodes_for_file(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py",
        )

        model_names = []
        for add_field in add_fields:
            assert add_field.func.attr == "AddField"

            try:
                model_name = [x.value.value for x in add_field.keywords if x.arg == "model_name"][
                    0
                ]
            except AttributeError:
                model_name = [x.value.s for x in add_field.keywords if x.arg == "model_name"][0]

            try:
                field_name = [x.value.value for x in add_field.keywords if x.arg == "name"][0]
            except AttributeError:
                field_name = [x.value.s for x in add_field.keywords if x.arg == "name"][0]

            model_names.append([model_name, field_name])

        assert model_names == [
            ["change_signoffs_required", "Parent_Change_Type"],
            ["change_signoffs_required", "Signoff_Pay_Grade_Required"],
            ["change_actual", "Change_Type"],
            ["change_actual", "Lines_Affected"],
            ["change_actual", "Machines_Affected"],
            ["change_actual", "Operations_Affected"],
            ["change_actual", "Status"],
            ["change_actual", "Variants_Affected"],
        ]

    def test_function_ignores_classes_that_are_not_migrations(self):
        """If there are other classes in the file, ignore them."""

        checker = DBIndexChecker()
        (
            create_models,
            alter_fields,
            add_fields,
        ) = checker._get_all_relevant_operations_nodes_for_file(
            "./specific_test_migrations/function_ignores_classes_that_are_not_migrations.py",
        )
        assert len(create_models) == 1
        try:
            model_name = [x.value.value for x in create_models[0].keywords if x.arg == "name"][0]
        except AttributeError:
            model_name = [x.value.s for x in create_models[0].keywords if x.arg == "name"][0]
        assert model_name == "Change_Actual"


class TestCheckForDBIndexInFieldObject(TestCase):
    """Tests for the _check_for_db_index_in_field_object function."""

    def setUp(self) -> None:
        """Create a fake field object."""
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


def get_create_models_list(file_path):
    """Get the create models list from the _get_all_relevant... function."""
    checker = DBIndexChecker()
    create, alter, add = checker._get_all_relevant_operations_nodes_for_file(file_path)
    return create


def get_alter_fields_list(file_path):
    """Get the create models list from the _get_all_relevant... function."""
    checker = DBIndexChecker()
    create, alter, add = checker._get_all_relevant_operations_nodes_for_file(file_path)
    return alter


def get_add_fields_list(file_path):
    """Get the create models list from the _get_all_relevant... function."""
    checker = DBIndexChecker()
    create, alter, add = checker._get_all_relevant_operations_nodes_for_file(file_path)
    return add


class TestCreateModelsToModelsDict(TestCase):
    """Tests for the _create_models_to_models_dict function."""

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work
        self.checker = DBIndexChecker()

    def test_function_adds_correct_information_from_sample_file(self):
        """Function should add the correct model information from the sample migration."""
        create_models = get_create_models_list(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py",
        )
        models_dict = {}
        self.checker._create_models_to_models_dict(
            models_dict=models_dict,
            create_models_list=create_models,
            migration_number=4,
        )

        assert models_dict == {
            "change_actual": {
                "id": {"is_index": False, "index_added": False},
                "change_initiation_date": {"is_index": False, "index_added": False},
                "change_description": {"is_index": False, "index_added": False},
                "change_risk_assesment": {"is_index": False, "index_added": False},
                "cut_in_number": {"is_index": False, "index_added": False},
                "cut_out_number": {"is_index": False, "index_added": False},
                "change_initiator": {"is_index": False, "index_added": False},
            },
            "change_signoffs": {
                "id": {"is_index": False, "index_added": False},
                "signature_date": {"is_index": False, "index_added": False},
                "changeover_department_required": {"is_index": False, "index_added": False},
                "parent_change_actual": {"is_index": False, "index_added": False},
                "signature_user": {"is_index": False, "index_added": False},
                "signoff_pay_grade_required": {"is_index": False, "index_added": False},
            },
            "change_signoffs_required": {
                "id": {"is_index": False, "index_added": False},
                "changeover_department_required": {"is_index": False, "index_added": False},
            },
            "change_status": {
                "id": {"is_index": False, "index_added": False},
                "status_name": {"is_index": False, "index_added": False},
            },
            "change_type": {
                "id": {"is_index": False, "index_added": False},
                "change_type_name": {"is_index": False, "index_added": False},
                "change_type_description": {"is_index": False, "index_added": False},
            },
        }


class TestAlterFieldsToModelsDict(TestCase):
    """Tests for the _alter_fields_to_models_dict function."""

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work
        self.checker = DBIndexChecker()
        self.base_models = {}
        self.checker._create_models_to_models_dict(
            self.base_models,
            get_create_models_list(
                "./example_migrations/important_functionality/"
                "migrations/0001_initial_migrations.py",
            ),
            1,
        )

    def get_alter_fields_list(self, file_path):
        """Get the alter fields list from the _get_all_relevant... function."""
        checker = self.checker
        create, alter, add = checker._get_all_relevant_operations_nodes_for_file(file_path)
        return alter

    def test_function_adds_correct_information_from_sample_file(self):
        """Function should add the correct model information from the sample migration."""
        alter_fields = self.get_alter_fields_list(
            "./example_migrations/important_functionality/migrations/0001_initial_migrations.py",
        )

        self.checker._alter_fields_to_models_dict(
            models_dict=self.base_models,
            alter_fields_list=alter_fields,
            migration_number=1,
        )

        assert self.base_models["change_actual"]["change_initiator"]["is_index"] is True

    def test_function_updates_migration_number_if_db_index_switched_on(self):
        """If the DB index is switched on then the migration number should be updated."""

        # Switch the index off in migration 1.
        alter_fields = self.get_alter_fields_list(
            "./specific_test_migrations/switch_db_index_off_in_alter_field.py",
        )
        self.checker._alter_fields_to_models_dict(
            models_dict=self.base_models,
            alter_fields_list=alter_fields,
            migration_number=1,
        )

        # Switch the index on in migration 2.
        alter_fields = self.get_alter_fields_list(
            "./specific_test_migrations/switch_db_index_on_in_alter_field.py",
        )
        self.checker._alter_fields_to_models_dict(
            models_dict=self.base_models,
            alter_fields_list=alter_fields,
            migration_number=2,
        )

        assert self.base_models["change_actual"]["change_initiator"]["is_index"] is True
        assert self.base_models["change_actual"]["change_initiator"]["index_added"] == 2

    def test_function_does_not_update_migration_number_if_db_index_still_on(self):
        """If the DB index remians on then the migration number should not be updated."""

        # Switch index on in migration 1.
        alter_fields = self.get_alter_fields_list(
            "./specific_test_migrations/switch_db_index_on_in_alter_field.py",
        )
        self.checker._alter_fields_to_models_dict(
            models_dict=self.base_models,
            alter_fields_list=alter_fields,
            migration_number=1,
        )

        # Index remains on in migration 2.
        alter_fields = self.get_alter_fields_list(
            "./specific_test_migrations/switch_db_index_on_in_alter_field.py",
        )
        self.checker._alter_fields_to_models_dict(
            models_dict=self.base_models,
            alter_fields_list=alter_fields,
            migration_number=2,
        )

        assert self.base_models["change_actual"]["change_initiator"]["is_index"] is True
        assert self.base_models["change_actual"]["change_initiator"]["index_added"] == 1

    def test_keyerror_raised_if_field_or_model_does_not_exist(self):
        """Function should raise an error if the model or field has not already been parsed."""
        alter = self.get_alter_fields_list(
            "specific_test_migrations/alter_a_non_existant_field.py",
        )
        with self.assertRaises(KeyError) as e:
            self.checker._alter_fields_to_models_dict(self.base_models, alter, 2)
        assert "change_status" in str(e.exception)
        assert "fake_field" in str(e.exception)


class TestAddFieldsToModelsDict(TestCase):
    """Tests for the _add_fields_to_models_dict function."""

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work
        self.checker = DBIndexChecker()
        self.base_models = {}
        self.checker._create_models_to_models_dict(
            self.base_models,
            get_create_models_list(
                "./example_migrations/important_functionality/"
                "migrations/0001_initial_migrations.py",
            ),
            1,
        )

    def test_function_adds_new_field_to_existing_model(self):
        """Function should add the correct model information from the sample migration."""
        add_fields = get_add_fields_list("./specific_test_migrations/add_field_wth_db_index_on.py")
        self.checker._add_fields_to_models_dict(
            models_dict=self.base_models,
            add_fields_list=add_fields,
            migration_number=4,
        )

        assert self.base_models["change_actual"]["madeupfield"] == {
            "is_index": True,
            "index_added": 4,
        }


important_functionality_models_list = {
    "change_actual": {
        "id": {"is_index": False, "index_added": False},
        "change_initiation_date": {"is_index": False, "index_added": False},
        "change_description": {"is_index": False, "index_added": False},
        "change_risk_assesment": {"is_index": False, "index_added": False},
        "cut_in_number": {"is_index": False, "index_added": False},
        "cut_out_number": {"is_index": False, "index_added": False},
        "change_initiator": {"is_index": True, "index_added": "0001"},
        "change_type": {"is_index": False, "index_added": False},
        "lines_affected": {"is_index": False, "index_added": False},
        "machines_affected": {"is_index": False, "index_added": False},
        "operations_affected": {"is_index": False, "index_added": False},
        "status": {"is_index": False, "index_added": False},
        "variants_affected": {"is_index": False, "index_added": False},
    },
    "change_signoffs": {
        "id": {"is_index": False, "index_added": False},
        "signature_date": {"is_index": False, "index_added": False},
        "changeover_department_required": {"is_index": False, "index_added": False},
        "parent_change_actual": {"is_index": False, "index_added": False},
        "signature_user": {"is_index": False, "index_added": False},
        "signoff_pay_grade_required": {"is_index": False, "index_added": False},
    },
    "change_signoffs_required": {
        "id": {"is_index": False, "index_added": False},
        "changeover_department_required": {"is_index": False, "index_added": False},
        "parent_change_type": {"is_index": False, "index_added": False},
        "signoff_pay_grade_required": {"is_index": False, "index_added": False},
    },
    "change_status": {
        "id": {"is_index": False, "index_added": False},
        "status_name": {"is_index": False, "index_added": False},
        "all_signatures_required": {"is_index": True, "index_added": "0003"},
    },
    "change_type": {
        "id": {"is_index": False, "index_added": False},
        "change_type_name": {"is_index": False, "index_added": False},
        "change_type_description": {"is_index": False, "index_added": False},
    },
}


class TestMapModels(TestCase):
    """Tests for the _map_models function."""

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work
        self.checker = DBIndexChecker()

    def test_function_raises_error_if_no_migrations(self):
        """Function should raise an error if the input doct has no migrations."""
        with self.assertRaises(ValueError) as e:
            self.checker._map_models({}, "")
        assert str(e.exception) == (
            "There are no migrations files in this app. Have you passed the "
            "all_apps dict instead of a specific app instance?"
        )

    @patch(
        "django_migration_dbindex_check.checker.DBIndexChecker."
        "_get_all_relevant_operations_nodes_for_file",
    )
    def test_function_calls_get_all_relevant_operations_with_correct_path(self, mock_get):
        """Function should call _get_relevant_operations... with all filepaths."""
        self.checker = DBIndexChecker()  # Re-init with patch
        mock_get.return_value = [], [], []
        app_dict = {
            "migration_files": [
                ["0001_test.py", "fake/path/0001_test.py"],
                ["0002_test_again.py", "fake/path/0002_test_again.py"],
            ],
        }
        self.checker._map_models(app_dict, "/fake/root")
        calls = [
            call("/fake/root/fake/path/0001_test.py"),
            call("/fake/root/fake/path/0002_test_again.py"),
        ]
        assert mock_get.call_args_list == calls

    @patch("django_migration_dbindex_check.checker.DBIndexChecker._alter_fields_to_models_dict")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._add_fields_to_models_dict")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._create_models_to_models_dict")
    @patch(
        "django_migration_dbindex_check.checker.DBIndexChecker."
        "_get_all_relevant_operations_nodes_for_file",
    )
    def test_function_calls_mutators_with_correct_args(
        self,
        mock_get,
        mock_create,
        mock_add,
        mock_alter,
    ):
        """Function should mutate a blank dict with the ops from each migration file."""
        self.checker = DBIndexChecker()  # Re-init with patch
        mock_get.return_value = ["create_ops"], ["alter_ops"], ["add_ops"]
        app_dict = {
            "migration_files": [
                ["0001_test.py", "fake/path/0001_test.py"],
                ["0002_test_again.py", "fake/path/0002_test_again.py"],
            ],
        }

        returned_models = self.checker._map_models(app_dict, "/fake/root")

        mock_create_calls = [
            call({}, ["create_ops"], "0001"),
            call({}, ["create_ops"], "0002"),
        ]
        assert mock_create.call_args_list == mock_create_calls

        mock_add_calls = [
            call({}, ["add_ops"], "0001"),
            call({}, ["add_ops"], "0002"),
        ]
        assert mock_add.call_args_list == mock_add_calls

        mock_alter_calls = [
            call({}, ["alter_ops"], "0001"),
            call({}, ["alter_ops"], "0002"),
        ]
        assert mock_alter.call_args_list == mock_alter_calls
        assert returned_models == {}

    def test_integration_function_outputs_correct_data_from_sample_files(self):
        """Function outputs the correct data from the sample migrations."""
        root_path = "./example_migrations/important_functionality"
        app_dict = self.checker._walk_files(root_path)
        models_dict = self.checker._map_models(app_dict["important_functionality"], "")

        assert models_dict == important_functionality_models_list


class TestAnalyseModels(TestCase):
    """Tests for the _analyse_models function."""

    def setUp(self) -> None:  # noqa: D102
        self.example_app = {
            "change_actual": {
                "test1": {"is_index": True, "index_added": "0001"},
                "test2": {"is_index": True, "index_added": "0003"},
                "test3": {"is_index": False, "index_added": False},
            },
        }
        self.checker = DBIndexChecker()

    def test_function_returns_error_in_correct_format(self):
        """Should return one error for each dbindex."""
        result = self.checker._analyse_models(self.example_app)
        assert result == [
            {"model": "change_actual", "field": "test1", "migration": "0001"},
            {"model": "change_actual", "field": "test2", "migration": "0003"},
        ]

    def test_function_ignores_migrations_before_specified(self):
        """Should ignore all migrations before the specified ignore int."""
        result = self.checker._analyse_models(self.example_app, 2)
        assert result == [
            {"model": "change_actual", "field": "test2", "migration": "0003"},
        ]


class TestGetConfig(TestCase):
    """Tests for the get_config function."""

    def setUp(self) -> None:  # noqa: D102
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)  # Make the relative imports work

    @patch("django_migration_dbindex_check.checker.configparser.ConfigParser.read")
    def test_sets_path_correctly_based_on_project_root(self, mock_read):
        """Should look for the file in the root directory."""
        checker = DBIndexChecker()
        checker.get_config("abc")
        expected_path = os.path.join(os.getcwd(), "abc/migrations_check.cfg")
        mock_read.assert_called_once_with(expected_path)

    def test_reads_config_correctly(self):
        """Function should read and return a ConfigParser object with correct settings."""
        checker = DBIndexChecker()
        config = checker.get_config("example_migrations")

        assert isinstance(config, ConfigParser)

        expected_list = [["important_functionality", 4], ["other_service", 4], ["the_app", 4]]
        for items in expected_list:
            assert int(config["DJANGO_MIGRATION_DBINDEX_CHECK"][items[0]]) == items[1]

    def test_sends_blank_config_back_if_no_file_found(self):
        """Test should return a blank ConfigParser if no config file found."""
        checker = DBIndexChecker()
        config = checker.get_config("not_there")

        assert config == configparser.ConfigParser()


class TestCheckProject(TestCase):
    """Tests for the check_project function."""

    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._walk_files")
    def test_function_calls_walk_files_with_given_root_dir(self, mock_walk, mock_exit):
        """Function should call walk files with the specified root dir."""
        checker = DBIndexChecker()
        checker.check_project("my_root")
        mock_walk.assert_called_once_with("my_root")

    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker.get_config")
    def test_function_calls_get_config_with_given_root_dir(self, mock_config, mock_exit):
        """Function should call get_config with the specified root dir."""
        checker = DBIndexChecker()
        checker.check_project("my_root")
        mock_config.assert_called_once_with("my_root")

    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._map_models")
    def test_function_calls_map_models_with_each_found_file(self, mock_map, mock_exit):
        """Function should call _map_models with each found migration file location."""
        checker = DBIndexChecker()
        checker.check_project("example_migrations")
        expected_dict_args = [
            {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/important_functionality/migrations/"
                        "0001_initial_migrations.py",
                    ],
                    [
                        "0002_renamed_a_field.py",
                        "example_migrations/important_functionality/migrations/"
                        "0002_renamed_a_field.py",
                    ],
                    [
                        "0003_added_new_field_db_index.py",
                        "example_migrations/important_functionality/migrations/"
                        "0003_added_new_field_db_index.py",
                    ],
                ],
            },
            {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/the_app/migrations/0001_initial_migrations.py",
                    ],
                    [
                        "0002_added_index_to_existing_field.py",
                        "example_migrations/the_app/migrations/"
                        "0002_added_index_to_existing_field.py",
                    ],
                ],
            },
            {
                "migration_files": [
                    [
                        "0001_initial_migrations.py",
                        "example_migrations/other_service/migrations/"
                        "0001_initial_migrations.py",
                    ],
                    [
                        "0002_did_some_stuff.py",
                        "example_migrations/other_service/migrations/"
                        "0002_did_some_stuff.py",
                    ],
                ],
            },
        ]
        dict_call_args_list = [x[1]["app_dict"] for x in mock_map.call_args_list]
        assert dict_call_args_list == expected_dict_args
        root_paths = [x[1]["root_path"] for x in mock_map.call_args_list]
        for paths in root_paths:
            assert paths == os.getcwd()

    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._analyse_models")
    def test_function_calls_analyse_models_with_all_found_models(self, mock_analyse, mock_exit):
        """Function should call _analyse_models with all models found from migration files."""
        checker = DBIndexChecker()
        checker.check_project("example_migrations/important_functionality")
        mock_analyse.assert_called_once()
        assert mock_analyse.call_args_list[0][0][0] == important_functionality_models_list

    @patch("django_migration_dbindex_check.checker.DBIndexChecker.get_config")
    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._analyse_models")
    def test_function_does_not_ignore_migrations_if_no_config(
        self, mock_analyse, mock_exit, mock_config,
    ):
        """Function should report indices from all migrations if no config found."""
        checker = DBIndexChecker()
        mock_config.return_value = {}
        checker.check_project("example_migrations/important_functionality")
        mock_analyse.assert_called_once()
        assert mock_analyse.call_args_list[0][0][1] == 0

    @patch("django_migration_dbindex_check.checker.sys.exit")
    @patch("django_migration_dbindex_check.checker.DBIndexChecker._analyse_models")
    def test_function_honors_ignore_migrations_config(self, mock_analyse, mock_exit):
        """Function should honor ignore migration files config."""
        checker = DBIndexChecker()
        checker.check_project("example_migrations")
        assert mock_analyse.call_args_list[0][0][1] == 4

    @patch("django_migration_dbindex_check.checker.print")
    @patch("django_migration_dbindex_check.checker.sys.exit")
    def test_function_prints_all_found_errors(self, mock_exit, mock_print):
        """Function should print all found indices to sys.stderr."""
        checker = DBIndexChecker()
        checker.check_project("example_migrations/important_functionality")

        expected_prints = [
            "A new db_index was added to field:change_initiator in model:change_actual in app:"
            "important_functionality. This was added in migration 0001.",
            "A new db_index was added to field:all_signatures_required in model:change_status"
            " in app:important_functionality. This was added in migration 0003.",
        ]

        calls = [x[0][0] for x in mock_print.call_args_list]
        calls.pop(0)
        assert calls == expected_prints

    @patch("django_migration_dbindex_check.checker.sys.exit")
    def test_function_exists_with_error_code_1_if_errors(self, mock_exit):
        """Function should exit with error code 1 (for CI check) if indices found."""
        checker = DBIndexChecker()
        checker.check_project("example_migrations/important_functionality")

        mock_exit.assert_called_with(1)

    @patch("django_migration_dbindex_check.checker.DBIndexChecker._analyse_models")
    @patch("django_migration_dbindex_check.checker.sys.exit")
    def test_function_exists_with_error_code_0_if_no_errors(self, mock_exit, mock_analyse):
        """Function should exit with error code 0 (for CI check) if no indices found."""
        checker = DBIndexChecker()
        mock_analyse.return_value = []
        checker.check_project("example_migrations/important_functionality")

        mock_exit.assert_called_with()
