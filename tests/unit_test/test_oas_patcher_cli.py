import pytest
import yaml
from click.testing import CliRunner
from oas_patch.oas_patcher_cli import cli


@pytest.fixture
def mock_load_file(mocker):
    """Mock the load_file function."""
    return mocker.patch("oas_patch.oas_patcher_cli.load_file")


@pytest.fixture
def mock_save_file(mocker):
    """Mock the save_file function."""
    return mocker.patch("oas_patch.oas_patcher_cli.save_file")


@pytest.fixture
def mock_apply_overlay(mocker):
    """Mock the apply_overlay function."""
    return mocker.patch("oas_patch.oas_patcher_cli.apply_overlay")


@pytest.fixture
def setup_mocks(mock_load_file, mock_apply_overlay):
    """Set up common mock behavior for load_file and apply_overlay."""
    mock_load_file.side_effect = [
        {"openapi": "3.0.3", "info": {"title": "Sample API"}},
        {"actions": [{"target": "$.info", "update": {"title": "Updated API"}}]},
    ]
    mock_apply_overlay.return_value = {
        "openapi": "3.0.3",
        "info": {"title": "Updated API"},
    }


def run_cli_with_args(args):
    """Helper function to run the CLI with specific arguments using CliRunner."""
    runner = CliRunner()
    return runner.invoke(cli, args)


def assert_load_file_calls(mock_load_file, sanitize=False):
    """Helper function to assert calls to load_file."""
    mock_load_file.assert_any_call("openapi.yaml", sanitize)
    mock_load_file.assert_any_call("overlay.yaml")


def assert_apply_overlay_call(mock_apply_overlay):
    """Helper function to assert calls to apply_overlay."""
    mock_apply_overlay.assert_called_once_with(
        {"openapi": "3.0.3", "info": {"title": "Sample API"}},
        {"actions": [{"target": "$.info", "update": {"title": "Updated API"}}]},
    )


def assert_save_file_call(mock_save_file, output_file):
    """Helper function to assert calls to save_file."""
    mock_save_file.assert_called_once_with(
        {"openapi": "3.0.3", "info": {"title": "Updated API"}}, output_file
    )


def test_cli_output_to_file(
    setup_mocks, mock_save_file, mock_load_file, mock_apply_overlay
):
    """Test the CLI with output to a file."""
    result = run_cli_with_args(
        ["overlay", "openapi.yaml", "overlay.yaml", "-o", "output.yaml"]
    )

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert_load_file_calls(mock_load_file, sanitize=False)
    assert_apply_overlay_call(mock_apply_overlay)
    assert_save_file_call(mock_save_file, "output.yaml")


def test_cli_output_to_console(setup_mocks, mock_load_file, mock_apply_overlay):
    """Test the CLI with output to the console."""
    result = run_cli_with_args(["overlay", "openapi.yaml", "overlay.yaml"])

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert_load_file_calls(mock_load_file, sanitize=False)
    assert_apply_overlay_call(mock_apply_overlay)

    assert yaml.safe_load(result.output) == {
        "openapi": "3.0.3",
        "info": {"title": "Updated API"},
    }


def test_cli_missing_required_arguments():
    """Test the CLI with missing required arguments."""
    result = run_cli_with_args([])

    # Click exits with code 2 for missing arguments or usage errors
    assert result.exit_code == 2


def test_cli_with_sanitize_flag(setup_mocks, mock_load_file, mock_apply_overlay):
    """Test the CLI with the --sanitize flag."""
    result = run_cli_with_args(
        ["overlay", "openapi.yaml", "overlay.yaml", "--sanitize"]
    )

    assert result.exit_code == 0, f"CLI command failed: {result.output}"
    assert_load_file_calls(mock_load_file, sanitize=True)
    assert_apply_overlay_call(mock_apply_overlay)


def test_help_command():
    """Test the CLI help message."""
    result = run_cli_with_args(["--help"])

    assert result.exit_code == 0, "Help command should exit with code 0"
    assert "OpenAPI overlay management tool" in result.output


# =============================================================================
# ENHANCED COMMANDS TESTS
# =============================================================================


@pytest.fixture
def mock_enhanced_features(mocker):
    """Mock enhanced features dependencies."""
    mock_bundle_manager = mocker.patch("oas_patch.oas_patcher_cli.BundleManager")
    mock_env_manager = mocker.patch("oas_patch.oas_patcher_cli.EnvironmentManager")
    mock_template_engine = mocker.patch("oas_patch.oas_patcher_cli.TemplateEngine")
    mock_cli_utils = mocker.patch("oas_patch.oas_patcher_cli.cli_utils")

    # Mock the ENHANCED_FEATURES_AVAILABLE flag
    mocker.patch("oas_patch.oas_patcher_cli.ENHANCED_FEATURES_AVAILABLE", True)

    return {
        "bundle_manager": mock_bundle_manager,
        "env_manager": mock_env_manager,
        "template_engine": mock_template_engine,
        "cli_utils": mock_cli_utils,
    }


@pytest.fixture
def mock_enhanced_file_operations(mocker):
    """Mock file operations for enhanced commands."""
    mock_load_file = mocker.patch("oas_patch.oas_patcher_cli.load_file")
    mock_save_file = mocker.patch("oas_patch.oas_patcher_cli.save_file")
    mock_apply_overlay = mocker.patch("oas_patch.oas_patcher_cli.apply_overlay")

    return {
        "load_file": mock_load_file,
        "save_file": mock_save_file,
        "apply_overlay": mock_apply_overlay,
    }


# =============================================================================
# APPLY COMMAND TESTS
# =============================================================================


def test_apply_command_basic_success(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test apply command with basic successful execution."""
    # Setup mocks
    from unittest.mock import MagicMock

    bundle_config = MagicMock()
    bundle_config.overlays = [MagicMock(path="test.yaml", variables=None)]
    bundle_config.variables = {"test_var": "test_value"}

    mock_enhanced_features["bundle_manager"].return_value.load_bundle.return_value = (
        bundle_config
    )
    mock_enhanced_features["env_manager"].return_value.get_variables.return_value = {}
    mock_enhanced_features[
        "bundle_manager"
    ].return_value._resolve_overlay_path.return_value = "test.yaml"

    mock_enhanced_file_operations["load_file"].side_effect = [
        {"openapi": "3.0.0", "info": {"title": "Test API"}},  # OpenAPI doc
        {"overlay": "1.0.0", "actions": []},  # Overlay
    ]
    mock_enhanced_file_operations["apply_overlay"].return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Modified API"},
    }
    mock_enhanced_features[
        "template_engine"
    ].return_value.process_overlay_data.return_value = {
        "overlay": "1.0.0",
        "actions": [],
    }

    result = run_cli_with_args(
        ["apply", "openapi.yaml", "test-bundle", "--output", "output.yaml"]
    )

    assert result.exit_code == 0
    mock_enhanced_file_operations["save_file"].assert_called_once()
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.load_bundle.assert_called_once_with("test-bundle")


def test_apply_command_with_environment(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test apply command with environment specified."""
    # Setup mocks
    from unittest.mock import MagicMock

    bundle_config = MagicMock()
    bundle_config.overlays = [MagicMock(path="test.yaml", variables=None)]
    bundle_config.variables = {"bundle_var": "value"}

    mock_enhanced_features["bundle_manager"].return_value.load_bundle.return_value = (
        bundle_config
    )
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_overlays_for_environment.return_value = bundle_config.overlays
    mock_enhanced_features["env_manager"].return_value.get_variables.return_value = {
        "env_var": "env_value"
    }
    mock_enhanced_features[
        "bundle_manager"
    ].return_value._resolve_overlay_path.return_value = "test.yaml"

    mock_enhanced_file_operations["load_file"].side_effect = [
        {"openapi": "3.0.0", "info": {"title": "Test API"}},
        {"overlay": "1.0.0", "actions": []},
    ]
    mock_enhanced_file_operations["apply_overlay"].return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Modified API"},
    }
    mock_enhanced_features[
        "template_engine"
    ].return_value.process_overlay_data.return_value = {
        "overlay": "1.0.0",
        "actions": [],
    }

    result = run_cli_with_args(
        [
            "apply",
            "openapi.yaml",
            "test-bundle",
            "--env",
            "staging",
            "--output",
            "output.yaml",
        ]
    )

    assert result.exit_code == 0
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_overlays_for_environment.assert_called_once_with(
        "test-bundle", "staging"
    )


def test_apply_command_with_variables(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test apply command with CLI variables."""
    # Setup mocks
    from unittest.mock import MagicMock

    bundle_config = MagicMock()
    bundle_config.overlays = [
        MagicMock(path="test.yaml", variables={"overlay_var": "overlay_value"})
    ]
    bundle_config.variables = {"bundle_var": "bundle_value"}

    mock_enhanced_features["bundle_manager"].return_value.load_bundle.return_value = (
        bundle_config
    )
    mock_enhanced_features["env_manager"].return_value.get_variables.return_value = {}
    mock_enhanced_features[
        "bundle_manager"
    ].return_value._resolve_overlay_path.return_value = "test.yaml"

    mock_enhanced_file_operations["load_file"].side_effect = [
        {"openapi": "3.0.0", "info": {"title": "Test API"}},
        {"overlay": "1.0.0", "actions": []},
    ]
    mock_enhanced_file_operations["apply_overlay"].return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Modified API"},
    }
    mock_enhanced_features[
        "template_engine"
    ].return_value.process_overlay_data.return_value = {
        "overlay": "1.0.0",
        "actions": [],
    }

    result = run_cli_with_args(
        [
            "apply",
            "openapi.yaml",
            "test-bundle",
            "--var",
            "cli_var=cli_value",
            "--var",
            "another_var=another_value",
            "--output",
            "output.yaml",
        ]
    )

    assert result.exit_code == 0
    mock_enhanced_features[
        "template_engine"
    ].return_value.process_overlay_data.assert_called()


def test_apply_command_dry_run(mock_enhanced_features, mock_enhanced_file_operations):
    """Test apply command with dry run flag."""
    # Setup mocks
    from unittest.mock import MagicMock

    bundle_config = MagicMock()
    bundle_config.overlays = [MagicMock(path="test.yaml", variables=None)]
    bundle_config.variables = {}

    mock_enhanced_features["bundle_manager"].return_value.load_bundle.return_value = (
        bundle_config
    )
    mock_enhanced_features["env_manager"].return_value.get_variables.return_value = {}
    mock_enhanced_features[
        "bundle_manager"
    ].return_value._resolve_overlay_path.return_value = "test.yaml"

    mock_enhanced_file_operations["load_file"].side_effect = [
        {"openapi": "3.0.0", "info": {"title": "Test API"}},
        {"overlay": "1.0.0", "actions": []},
    ]
    mock_enhanced_file_operations["apply_overlay"].return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Modified API"},
    }
    mock_enhanced_features[
        "template_engine"
    ].return_value.process_overlay_data.return_value = {
        "overlay": "1.0.0",
        "actions": [],
    }

    result = run_cli_with_args(["apply", "openapi.yaml", "test-bundle", "--dry-run"])

    assert result.exit_code == 0
    # Verify save_file was NOT called in dry run
    mock_enhanced_file_operations["save_file"].assert_not_called()


def test_apply_command_missing_openapi_file(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test apply command with missing OpenAPI file."""
    mock_enhanced_file_operations["load_file"].side_effect = FileNotFoundError(
        "File not found"
    )

    result = run_cli_with_args(["apply", "missing.yaml", "test-bundle"])

    assert result.exit_code == 1


def test_apply_command_missing_bundle(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test apply command with missing bundle."""
    mock_enhanced_file_operations["load_file"].return_value = {"openapi": "3.0.0"}
    mock_enhanced_features["bundle_manager"].return_value.load_bundle.side_effect = (
        FileNotFoundError("Bundle not found")
    )

    result = run_cli_with_args(["apply", "openapi.yaml", "missing-bundle"])

    assert result.exit_code == 1


# =============================================================================
# LIST-BUNDLES COMMAND TESTS
# =============================================================================


def test_list_bundles_command_basic(mock_enhanced_features):
    """Test basic list-bundles command."""
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.discover_bundles.return_value = ["bundle1", "bundle2", "bundle3"]

    result = run_cli_with_args(["list-bundles"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].print_header.assert_called_once_with(
        "Available Bundles"
    )
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  bundle1")
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  bundle2")
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  bundle3")


def test_list_bundles_command_verbose(mock_enhanced_features):
    """Test list-bundles command with verbose flag."""
    mock_bundles_info = [
        {
            "name": "bundle1",
            "description": "Test bundle 1",
            "overlays": ["overlay1.yaml"],
            "validation": {"valid": True, "errors": [], "warnings": []},
        }
    ]

    mock_enhanced_features[
        "bundle_manager"
    ].return_value.discover_bundles.return_value = ["bundle1"]
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_bundle_info.return_value = mock_bundles_info[0]

    result = run_cli_with_args(["list-bundles", "--verbose"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].console.print.assert_called()


def test_list_bundles_command_no_bundles(mock_enhanced_features):
    """Test list-bundles command when no bundles are found."""
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.discover_bundles.return_value = []

    result = run_cli_with_args(["list-bundles"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].print_info.assert_called_with(
        "No bundles found in overlays"
    )


def test_list_bundles_command_error(mock_enhanced_features):
    """Test list-bundles command with error."""
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.discover_bundles.side_effect = Exception(
        "Failed to discover bundles"
    )

    result = run_cli_with_args(["list-bundles"])

    assert result.exit_code == 1


# =============================================================================
# LIST-ENVIRONMENTS COMMAND TESTS
# =============================================================================


def test_list_environments_command_basic(mock_enhanced_features):
    """Test basic list-environments command."""
    mock_enhanced_features[
        "env_manager"
    ].return_value.discover_environments.return_value = ["dev", "staging", "prod"]

    result = run_cli_with_args(["list-environments"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].print_header.assert_called_once_with(
        "Available Environments"
    )
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  dev")
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  staging")
    mock_enhanced_features["cli_utils"].print_info.assert_any_call("  prod")


def test_list_environments_command_verbose(mock_enhanced_features):
    """Test list-environments command with verbose flag."""
    mock_env_info = [
        {
            "name": "dev",
            "description": "Development environment",
            "variables": {"debug": "true"},
        },
        {
            "name": "prod",
            "description": "Production environment",
            "variables": {"debug": "false"},
        },
    ]

    mock_enhanced_features[
        "env_manager"
    ].return_value.list_environments_info.return_value = mock_env_info

    result = run_cli_with_args(["list-environments", "--verbose"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].console.print.assert_called()


def test_list_environments_command_no_environments(mock_enhanced_features):
    """Test list-environments command when no environments are found."""
    mock_enhanced_features[
        "env_manager"
    ].return_value.discover_environments.return_value = []

    result = run_cli_with_args(["list-environments"])

    assert result.exit_code == 0
    mock_enhanced_features["cli_utils"].print_info.assert_called_with(
        "No environments found in overlays"
    )


# =============================================================================
# BUNDLE-VALIDATE COMMAND TESTS
# =============================================================================


def test_bundle_validate_command_success(mock_enhanced_features):
    """Test bundle-validate command with valid bundle."""
    mock_validation_result = {"valid": True, "errors": [], "warnings": []}
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.validate_bundle.return_value = mock_validation_result

    result = run_cli_with_args(["bundle-validate", "test-bundle"])

    assert result.exit_code == 0
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.validate_bundle.assert_called_once_with("test-bundle")


def test_bundle_validate_command_failure(mock_enhanced_features):
    """Test bundle-validate command with invalid bundle."""
    mock_validation_result = {
        "valid": False,
        "errors": ["Error 1", "Error 2"],
        "warnings": ["Warning 1"],
    }
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.validate_bundle.return_value = mock_validation_result

    result = run_cli_with_args(["bundle-validate", "invalid-bundle"])

    assert result.exit_code == 1


def test_bundle_validate_command_exception(mock_enhanced_features):
    """Test bundle-validate command with exception."""
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.validate_bundle.side_effect = Exception("Validation error")

    result = run_cli_with_args(["bundle-validate", "test-bundle"])

    assert result.exit_code == 1


# =============================================================================
# INFO COMMAND TESTS
# =============================================================================


def test_info_command_success(mock_enhanced_features):
    """Test info command with valid bundle."""
    mock_bundle_info = {
        "name": "test-bundle",
        "description": "Test bundle description",
        "version": "1.0.0",
        "overlays": ["overlay1.yaml", "overlay2.yaml"],
        "variables": {"var1": "value1"},
        "validation": {"valid": True, "errors": [], "warnings": []},
    }
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_bundle_info.return_value = mock_bundle_info

    result = run_cli_with_args(["info", "test-bundle"])

    assert result.exit_code == 0
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_bundle_info.assert_called_once_with("test-bundle")
    mock_enhanced_features["cli_utils"].console.print.assert_called()


def test_info_command_exception(mock_enhanced_features):
    """Test info command with exception."""
    mock_enhanced_features[
        "bundle_manager"
    ].return_value.get_bundle_info.side_effect = Exception("Bundle not found")

    result = run_cli_with_args(["info", "missing-bundle"])

    assert result.exit_code == 1


# =============================================================================
# INIT COMMAND TESTS
# =============================================================================


def test_init_command_new_directory(mock_enhanced_features, mocker):
    """Test init command with new directory."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test-config"

        # Mock yaml.dump to avoid actual file writing in test
        mock_yaml_dump = mocker.patch("oas_patch.oas_patcher_cli.yaml.dump")

        result = run_cli_with_args(["init", "--config", str(config_path)])

        assert result.exit_code == 0
        assert config_path.exists()
        assert (config_path / "environments").exists()
        assert (config_path / "example-bundle").exists()

        # Verify yaml.dump was called for bundle and environment files
        assert (
            mock_yaml_dump.call_count >= 4
        )  # bundle.yaml + 2 overlays + 2 environments


def test_init_command_existing_directory_no_force(mock_enhanced_features, mocker):
    """Test init command with existing directory without force."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir)

        # Pre-create a file to make directory non-empty
        (config_path / "existing.txt").write_text("test")

        # Mock the confirm_action to return False (user says no)
        mock_enhanced_features["cli_utils"].confirm_action.return_value = False

        result = run_cli_with_args(["init", "--config", str(config_path)])

        assert result.exit_code == 0
        mock_enhanced_features["cli_utils"].print_info.assert_called_with(
            "Initialization cancelled"
        )


def test_init_command_existing_directory_with_force(mock_enhanced_features, mocker):
    """Test init command with existing directory with force."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir)

        # Mock yaml.dump to avoid actual file writing in test
        mock_yaml_dump = mocker.patch("oas_patch.oas_patcher_cli.yaml.dump")

        result = run_cli_with_args(["init", "--config", str(config_path), "--force"])

        assert result.exit_code == 0
        assert (config_path / "example-bundle").exists()

        # Verify yaml.dump was called for bundle and environment files
        assert mock_yaml_dump.call_count >= 4


def test_init_command_exception(mock_enhanced_features, mocker):
    """Test init command with exception."""
    # Mock Path to raise an exception
    mocker.patch("oas_patch.oas_patcher_cli.Path").side_effect = Exception(
        "Permission denied"
    )

    result = run_cli_with_args(["init"])

    assert result.exit_code == 1


# =============================================================================
# ENHANCED FEATURES AVAILABILITY TESTS
# =============================================================================


def test_enhanced_commands_require_dependencies(mocker):
    """Test that enhanced commands check for dependencies."""
    # Mock ENHANCED_FEATURES_AVAILABLE to False
    mocker.patch("oas_patch.oas_patcher_cli.ENHANCED_FEATURES_AVAILABLE", False)

    result = run_cli_with_args(["apply", "test.yaml", "test-bundle"])

    assert result.exit_code == 1
    assert "Enhanced features require additional dependencies" in result.output


def test_enhanced_commands_dependency_message(mocker):
    """Test enhanced commands show helpful dependency installation message."""
    mocker.patch("oas_patch.oas_patcher_cli.ENHANCED_FEATURES_AVAILABLE", False)

    result = run_cli_with_args(["list-bundles"])

    assert result.exit_code == 1
    assert "pip install Jinja2 rich click" in result.output


# =============================================================================
# HELPER FUNCTION TESTS FOR ENHANCED COMMANDS
# =============================================================================


def test_parse_cli_variables_function():
    """Test parse_cli_variables helper function."""
    from oas_patch.oas_patcher_cli import parse_cli_variables

    variables = parse_cli_variables(
        ["key1=value1", "key2=value2", "key3=value with spaces"]
    )

    assert variables == {
        "key1": "value1",
        "key2": "value2",
        "key3": "value with spaces",
    }


def test_parse_cli_variables_invalid_format():
    """Test parse_cli_variables with invalid format."""
    from oas_patch.oas_patcher_cli import parse_cli_variables
    from click import BadParameter

    with pytest.raises(BadParameter):
        parse_cli_variables(["invalid_format"])


def test_auto_generate_output_filename_function():
    """Test auto_generate_output_filename helper function."""
    from oas_patch.oas_patcher_cli import auto_generate_output_filename

    result = auto_generate_output_filename("api.yaml", "test-bundle", "yaml")
    assert result == "api-test-bundle.yaml"

    result = auto_generate_output_filename("api.json", "test-bundle", "json")
    assert result == "api-test-bundle.json"


def test_determine_output_format_function():
    """Test determine_output_format helper function."""
    from oas_patch.oas_patcher_cli import determine_output_format

    # Test with override
    assert determine_output_format("test.yaml", "json") == "json"

    # Test without override - yaml file
    assert determine_output_format("test.yaml", None) == "yaml"
    assert determine_output_format("test.yml", None) == "yaml"

    # Test without override - json file
    assert determine_output_format("test.json", None) == "json"

    # Test without override - unknown extension
    assert determine_output_format("test.txt", None) == "yaml"
