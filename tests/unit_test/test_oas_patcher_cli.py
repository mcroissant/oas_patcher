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

    # Click behavior for groups can vary - some versions show help (exit 0), others show usage error (exit 2)
    # Both are acceptable behaviors for a group command with no subcommand
    assert result.exit_code in [0, 2]
    assert (
        "OpenAPI overlay management tool" in result.output or "Usage:" in result.output
    )


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
# BUNDLE APPLY COMMAND TESTS
# =============================================================================


def test_apply_command_basic_success(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test bundle apply command with basic successful execution."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return bundle config, OpenAPI doc, and overlay in the correct order
    mock_enhanced_file_operations["load_file"].side_effect = [
        {  # Bundle config (loaded first)
            "name": "test-bundle",
            "overlays": [{"path": "overlays/test.yaml"}],
            "variables": {"test_var": "test_value"},
        },
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        },  # OpenAPI doc (loaded second)
        {"overlay": "1.0.0", "actions": []},  # Overlay (loaded third)
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

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        overlay_file = Path(temp_dir) / "overlays" / "test.yaml"

        # Create the files so they exist
        overlay_file.parent.mkdir(exist_ok=True)
        bundle_file.write_text("test")
        overlay_file.write_text("test")

        result = run_cli_with_args(
            [
                "bundle",
                "apply",
                "openapi.yaml",
                str(bundle_file),
                "--output",
                "output.yaml",
            ]
        )

        assert result.exit_code == 0
        mock_enhanced_file_operations["save_file"].assert_called_once()


def test_apply_command_with_environment(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test bundle apply command with environment specified."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return bundle config, OpenAPI doc, and overlay in the correct order
    mock_enhanced_file_operations["load_file"].side_effect = [
        {  # Bundle config (loaded first)
            "name": "test-bundle",
            "overlays": [
                {
                    "path": "overlays/test.yaml",
                    "environment": ["staging", "production"],
                },
                {"path": "overlays/dev.yaml", "environment": ["development"]},
            ],
            "variables": {"bundle_var": "value"},
        },
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        },  # OpenAPI doc (loaded second)
        {"overlay": "1.0.0", "actions": []},  # Overlay (loaded third)
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

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        overlay_file = Path(temp_dir) / "overlays" / "test.yaml"

        # Create the files so they exist
        overlay_file.parent.mkdir(exist_ok=True)
        bundle_file.write_text("test")
        overlay_file.write_text("test")

        result = run_cli_with_args(
            [
                "bundle",
                "apply",
                "openapi.yaml",
                str(bundle_file),
                "--env",
                "staging",
                "--output",
                "output.yaml",
            ]
        )

        assert result.exit_code == 0


def test_apply_command_with_variables(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test bundle apply command with CLI variables."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return bundle config, OpenAPI doc, and overlay in the correct order
    mock_enhanced_file_operations["load_file"].side_effect = [
        {  # Bundle config (loaded first)
            "name": "test-bundle",
            "overlays": [
                {
                    "path": "overlays/test.yaml",
                    "variables": {"overlay_var": "overlay_value"},
                }
            ],
            "variables": {"bundle_var": "bundle_value"},
        },
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        },  # OpenAPI doc (loaded second)
        {"overlay": "1.0.0", "actions": []},  # Overlay (loaded third)
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

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        overlay_file = Path(temp_dir) / "overlays" / "test.yaml"

        # Create the files so they exist
        overlay_file.parent.mkdir(exist_ok=True)
        bundle_file.write_text("test")
        overlay_file.write_text("test")

        result = run_cli_with_args(
            [
                "bundle",
                "apply",
                "openapi.yaml",
                str(bundle_file),
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
    """Test bundle apply command with dry run flag."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return bundle config, OpenAPI doc, and overlay in the correct order
    mock_enhanced_file_operations["load_file"].side_effect = [
        {  # Bundle config (loaded first)
            "name": "test-bundle",
            "overlays": [{"path": "overlays/test.yaml"}],
            "variables": {},
        },
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        },  # OpenAPI doc (loaded second)
        {"overlay": "1.0.0", "actions": []},  # Overlay (loaded third)
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

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        overlay_file = Path(temp_dir) / "overlays" / "test.yaml"

        # Create the files so they exist
        overlay_file.parent.mkdir(exist_ok=True)
        bundle_file.write_text("test")
        overlay_file.write_text("test")

        result = run_cli_with_args(
            ["bundle", "apply", "openapi.yaml", str(bundle_file), "--dry-run"]
        )

        assert result.exit_code == 0
        # Verify save_file was NOT called in dry run
        mock_enhanced_file_operations["save_file"].assert_not_called()


def test_apply_command_missing_openapi_file(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test bundle apply command with missing OpenAPI file."""
    import tempfile
    from pathlib import Path

    mock_enhanced_file_operations["load_file"].side_effect = FileNotFoundError(
        "File not found"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("test")

        result = run_cli_with_args(
            ["bundle", "apply", "missing.yaml", str(bundle_file)]
        )

        assert result.exit_code == 1


def test_apply_command_missing_bundle(
    mock_enhanced_features, mock_enhanced_file_operations
):
    """Test bundle apply command with missing bundle."""
    # This test should trigger a Click error because bundle file doesn't exist
    result = run_cli_with_args(
        ["bundle", "apply", "openapi.yaml", "missing-bundle.yaml"]
    )

    assert result.exit_code == 2  # Click error for missing file


# =============================================================================
# BUNDLE VALIDATE COMMAND TESTS
# =============================================================================


def test_bundle_validate_command_success(mock_enhanced_features, mocker):
    """Test bundle validate command with valid bundle file."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return valid bundle configuration
    mock_load_file = mocker.patch("oas_patch.oas_patcher_cli.load_file")
    mock_load_file.side_effect = [
        # Bundle configuration
        {"name": "test-bundle", "overlays": [{"path": "overlays/test.yaml"}]},
        # Overlay file
        {"overlay": "1.0.0", "actions": []},
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        overlay_file = Path(temp_dir) / "overlays" / "test.yaml"

        # Create the files so they exist
        bundle_file.parent.mkdir(exist_ok=True)
        overlay_file.parent.mkdir(exist_ok=True)
        bundle_file.write_text("test")
        overlay_file.write_text("test")

        result = run_cli_with_args(["bundle", "validate", str(bundle_file)])

        assert result.exit_code == 0


def test_bundle_validate_command_missing_overlay(mock_enhanced_features, mocker):
    """Test bundle validate command with missing overlay file."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return bundle configuration with missing overlay
    mock_load_file = mocker.patch("oas_patch.oas_patcher_cli.load_file")
    mock_load_file.return_value = {
        "name": "test-bundle",
        "overlays": [{"path": "overlays/missing.yaml"}],
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("test")

        result = run_cli_with_args(["bundle", "validate", str(bundle_file)])

        assert result.exit_code == 1


def test_bundle_validate_command_invalid_bundle_structure(
    mock_enhanced_features, mocker
):
    """Test bundle validate command with invalid bundle structure."""
    import tempfile
    from pathlib import Path

    # Mock load_file to return invalid bundle configuration (missing required fields)
    mock_load_file = mocker.patch("oas_patch.oas_patcher_cli.load_file")
    mock_load_file.return_value = {"description": "Missing name and overlays"}

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("test")

        result = run_cli_with_args(["bundle", "validate", str(bundle_file)])

        assert result.exit_code == 1


# =============================================================================
# BUNDLE INIT COMMAND TESTS
# =============================================================================


# BUNDLE INIT COMMAND TESTS
# =============================================================================


def test_init_command_creates_files(mock_enhanced_features, mocker):
    """Test bundle init command creates files in current directory."""
    import tempfile
    import os

    # Mock yaml.dump to avoid actual file writing in test
    mock_yaml_dump = mocker.patch("oas_patch.oas_patcher_cli.yaml.dump")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = run_cli_with_args(["bundle", "init"])

            assert result.exit_code == 0

            # Check that files would be created (yaml.dump called)
            assert mock_yaml_dump.call_count == 3  # bundle.yaml + 2 overlays

        finally:
            os.chdir(original_cwd)


def test_init_command_existing_files_no_force(mock_enhanced_features, mocker):
    """Test bundle init command with existing files without force."""
    import tempfile
    from pathlib import Path
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        # Pre-create files
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("existing")

        # Mock the confirm_action to return False (user says no)
        mock_enhanced_features["cli_utils"].confirm_action.return_value = False

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = run_cli_with_args(["bundle", "init"])

            assert result.exit_code == 0
            mock_enhanced_features["cli_utils"].print_info.assert_called_with(
                "Initialization cancelled"
            )
        finally:
            os.chdir(original_cwd)


def test_init_command_existing_files_with_force(mock_enhanced_features, mocker):
    """Test bundle init command with existing files with force."""
    import tempfile
    from pathlib import Path
    import os

    # Mock yaml.dump to avoid actual file writing in test
    mock_yaml_dump = mocker.patch("oas_patch.oas_patcher_cli.yaml.dump")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Pre-create files
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("existing")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            result = run_cli_with_args(["bundle", "init", "--force"])

            assert result.exit_code == 0
            # Verify yaml.dump was called for bundle and overlay files
            assert mock_yaml_dump.call_count == 3  # bundle.yaml + 2 overlays
        finally:
            os.chdir(original_cwd)


def test_init_command_exception(mock_enhanced_features, mocker):
    """Test bundle init command with exception."""
    # Mock Path to raise an exception when creating overlays directory
    mock_path = mocker.patch("oas_patch.oas_patcher_cli.Path")
    mock_path.return_value.mkdir.side_effect = Exception("Permission denied")

    result = run_cli_with_args(["bundle", "init"])

    assert result.exit_code == 1


# =============================================================================
# ENHANCED FEATURES AVAILABILITY TESTS
# =============================================================================


def test_enhanced_commands_require_dependencies(mocker):
    """Test that enhanced commands check for dependencies."""
    import tempfile
    from pathlib import Path

    # Mock ENHANCED_FEATURES_AVAILABLE to False
    mocker.patch("oas_patch.oas_patcher_cli.ENHANCED_FEATURES_AVAILABLE", False)

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_file = Path(temp_dir) / "bundle.yaml"
        bundle_file.write_text("test")

        result = run_cli_with_args(["bundle", "apply", "test.yaml", str(bundle_file)])

        assert result.exit_code == 1
        assert "Enhanced features require additional dependencies" in result.output


def test_enhanced_commands_dependency_message(mocker):
    """Test enhanced commands show helpful dependency installation message."""
    mocker.patch("oas_patch.oas_patcher_cli.ENHANCED_FEATURES_AVAILABLE", False)

    result = run_cli_with_args(["bundle", "init"])

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
