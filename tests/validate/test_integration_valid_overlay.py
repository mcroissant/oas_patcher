import pytest
from src.oas_patch.oas_patcher_cli import cli
from unittest.mock import patch


@pytest.mark.parametrize("test_case", [
    {
        "name": "valid_overlay",
        "overlay_file": "tests/samples/complex/petstore/overlay.yaml"
    },
    {
        "name": "add-a-license",
        "overlay_file": "tests/samples/compliance_set/add-a-license/overlay.yaml"
    },
    {
        "name": "description-and-summary",
        "overlay_file": "tests/samples/compliance_set/description-and-summary/overlay.yaml"
    },
    {
        "name": "remove-example",
        "overlay_file": "tests/samples/compliance_set/remove-example/overlay.yaml"
    },
    {
        "name": "remove-matching-responses",
        "overlay_file": "tests/samples/compliance_set/remove-matching-responses/overlay.yaml"
    },
    {
        "name": "remove-property",
        "overlay_file": "tests/samples/compliance_set/remove-property/overlay.yaml"
    },
    {
        "name": "remove-server",
        "overlay_file": "tests/samples/compliance_set/remove-server/overlay.yaml"
    },
    {
        "name": "replace-servers-for-sandbox",
        "overlay_file": "tests/samples/compliance_set/replace-servers-for-sandbox/overlay.yaml"
    },
    {
        "name": "update-root",
        "overlay_file": "tests/samples/compliance_set/update-root/overlay.yaml"
    },
    {
        "name": "array_update",
        "overlay_file": "tests/samples/medium/array_update/overlay.yaml"
    },
    {
        "name": "array_remove",
        "overlay_file": "tests/samples/medium/array_remove/overlay.yaml"
    },
    {
        "name": "remove_update",
        "overlay_file": "tests/samples/medium/remove_update/overlay.yaml"
    },
    {
        "name": "structured_overlay",
        "overlay_file": "tests/samples/medium/structured_overlay/overlay.yaml"
    },
    {
        "name": "targeted_overlay",
        "overlay_file": "tests/samples/medium/targeted_overlay/overlay.yaml"
    },
    {
        "name": "wildcard_overlay",
        "overlay_file": "tests/samples/medium/wildcard_overlay/overlay.yaml"
    },
    {
        "name": "update",
        "overlay_file": "tests/samples/simple/update/overlay.yaml"
    },
    {
        "name": "remove",
        "overlay_file": "tests/samples/simple/remove/overlay.yaml"
    },
    {
        "name": "multi_action",
        "overlay_file": "tests/samples/simple/multi_action/overlay.yaml"
    },
    {
        "name": "no_match",
        "overlay_file": "tests/samples/simple/no_match/overlay.yaml"
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
    assert '[ERROR]' not in captured.out, f"Test case '{test_case['name']}' failed with errors in output."
    assert '[INFO]' in captured.out
