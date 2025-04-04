import pytest
import yaml
from src.oas_patch.oas_patcher_cli import cli


@pytest.fixture
def mock_load_file(mocker):
    """Mock the load_file function."""
    return mocker.patch('src.oas_patch.oas_patcher_cli.load_file')


@pytest.fixture
def mock_save_file(mocker):
    """Mock the save_file function."""
    return mocker.patch('src.oas_patch.oas_patcher_cli.save_file')


@pytest.fixture
def mock_apply_overlay(mocker):
    """Mock the apply_overlay function."""
    return mocker.patch('src.oas_patch.oas_patcher_cli.apply_overlay')


@pytest.fixture
def setup_mocks(mock_load_file, mock_apply_overlay):
    """Set up common mock behavior for load_file and apply_overlay."""
    mock_load_file.side_effect = [
        {"openapi": "3.0.3", "info": {"title": "Sample API"}},
        {"actions": [{"target": "$.info", "update": {"title": "Updated API"}}]},
    ]
    mock_apply_overlay.return_value = {"openapi": "3.0.3", "info": {"title": "Updated API"}}


def run_cli_with_args(mocker, args):
    """Helper function to run the CLI with specific arguments."""
    mocker.patch('sys.argv', ['oas-patch'] + args)
    cli()


def assert_load_file_calls(mock_load_file, sanitize=False):
    """Helper function to assert calls to load_file."""
    mock_load_file.assert_any_call('openapi.yaml', sanitize)
    mock_load_file.assert_any_call('overlay.yaml')


def assert_apply_overlay_call(mock_apply_overlay):
    """Helper function to assert calls to apply_overlay."""
    mock_apply_overlay.assert_called_once_with(
        {"openapi": "3.0.3", "info": {"title": "Sample API"}},
        {"actions": [{"target": "$.info", "update": {"title": "Updated API"}}]}
    )


def assert_save_file_call(mock_save_file, output_file):
    """Helper function to assert calls to save_file."""
    mock_save_file.assert_called_once_with(
        {"openapi": "3.0.3", "info": {"title": "Updated API"}}, output_file
    )


def test_cli_output_to_file(setup_mocks, mock_save_file, mock_load_file, mock_apply_overlay, mocker):
    """Test the CLI with output to a file."""
    run_cli_with_args(mocker, ['overlay', 'openapi.yaml', 'overlay.yaml', '-o', 'output.yaml'])

    assert_load_file_calls(mock_load_file, sanitize=False)
    assert_apply_overlay_call(mock_apply_overlay)
    assert_save_file_call(mock_save_file, 'output.yaml')


def test_cli_output_to_console(setup_mocks, mock_load_file, mock_apply_overlay, mocker, capsys):
    """Test the CLI with output to the console."""
    run_cli_with_args(mocker, ['overlay', 'openapi.yaml', 'overlay.yaml'])

    assert_load_file_calls(mock_load_file, sanitize=False)
    assert_apply_overlay_call(mock_apply_overlay)

    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out) == {"openapi": "3.0.3", "info": {"title": "Updated API"}}


def test_cli_missing_required_arguments(mocker):
    """Test the CLI with missing required arguments."""
    mocker.patch('sys.argv', ['oas-patch'])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    assert excinfo.value.code == 1  # argparse exits with code 2 for missing arguments


def test_cli_with_sanitize_flag(setup_mocks, mock_load_file, mock_apply_overlay, mocker):
    """Test the CLI with the --sanitize flag."""
    run_cli_with_args(mocker, ['overlay', 'openapi.yaml', 'overlay.yaml', '--sanitize'])

    assert_load_file_calls(mock_load_file, sanitize=True)
    assert_apply_overlay_call(mock_apply_overlay)


def test_help_command(mocker, capsys):
    """Test the CLI help message."""
    mocker.patch('sys.argv', ['oas-patch', '--help'])

    with pytest.raises(SystemExit) as excinfo:
        cli()

    captured = capsys.readouterr()
    assert "Apply an OpenAPI Overlay to your OpenAPI document." in captured.out
    assert excinfo.value.code == 0  # Ensure the CLI exits with code 0 for help
