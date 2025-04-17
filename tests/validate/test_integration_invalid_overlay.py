import pytest
from src.oas_patch.oas_patcher_cli import cli
from unittest.mock import patch


@pytest.mark.parametrize("test_case", [
    {
        "name": "no_actions",
        "overlay_file": "tests/samples/invalid_overlay/overlay_noactions.yml",
        "failure": "'actions' is a required property"
    },
    {
        "name": "no_info",
        "overlay_file": "tests/samples/invalid_overlay/overlay_noinfo.yml",
        "failure": "'info' is a required property"
    },
    {
        "name": "no_object",
        "overlay_file": "tests/samples/invalid_overlay/overlay_noobject.yml",
        "failure": "is not of type 'object'"
    },
    {
        "name": "no_overlay",
        "overlay_file": "tests/samples/invalid_overlay/overlay_nooverlay.yml",
        "failure": "'overlay' is a required property"
    }
])
def test_integration_file_based(test_case, capsys):
    """Test the CLI using input and expected output files."""
    # Mock CLI arguments
    with patch('sys.argv', [
        'oas-patch',
        'validate',
        test_case["overlay_file"],
        '--format',
        'log'
    ]):
        cli()

    # Capture the CLI console output
    captured = capsys.readouterr()

    # Assert that '[ERROR]' is not in the captured output
    assert test_case["failure"] in captured.out, f"Test case '{test_case['name']}' failed without expected error in output."
    assert '[ERROR]' in captured.out, f"Test case '{test_case['name']}' failed with errors in output."
    assert '[INFO]' not in captured.out
