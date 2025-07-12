import os
import tempfile
import yaml
import pytest
from click.testing import CliRunner
from oas_patch.oas_patcher_cli import cli


@pytest.mark.parametrize("test_case", [
    {
        "name": "array_update",
        "openapi_file": "tests/samples/medium/array_update/openapi.yaml",
        "overlay_file": "tests/samples/medium/array_update/overlay.yaml",
        "expected_file": "tests/samples/medium/array_update/output.yaml",
    },
    {
        "name": "array_remove",
        "openapi_file": "tests/samples/medium/array_remove/openapi.yaml",
        "overlay_file": "tests/samples/medium/array_remove/overlay.yaml",
        "expected_file": "tests/samples/medium/array_remove/output.yaml",
    },
    {
        "name": "remove_update",
        "openapi_file": "tests/samples/medium/remove_update/openapi.yaml",
        "overlay_file": "tests/samples/medium/remove_update/overlay.yaml",
        "expected_file": "tests/samples/medium/remove_update/output.yaml",
    },
    {
        "name": "structured_overlay",
        "openapi_file": "tests/samples/medium/structured_overlay/openapi.yaml",
        "overlay_file": "tests/samples/medium/structured_overlay/overlay.yaml",
        "expected_file": "tests/samples/medium/structured_overlay/output.yaml",
    },
    {
        "name": "targeted_overlay",
        "openapi_file": "tests/samples/medium/targeted_overlay/openapi.yaml",
        "overlay_file": "tests/samples/medium/targeted_overlay/overlay.yaml",
        "expected_file": "tests/samples/medium/targeted_overlay/output.yaml",
    },
    {
        "name": "wildcard_overlay",
        "openapi_file": "tests/samples/medium/wildcard_overlay/openapi.yaml",
        "overlay_file": "tests/samples/medium/wildcard_overlay/overlay.yaml",
        "expected_file": "tests/samples/medium/wildcard_overlay/output.yaml",
    }
])
def test_integration_file_based(test_case, capsys):
    """Test the CLI using input and expected output files."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_output:
        temp_output.close()

        # Apply the overlay using overlay command
        result = runner.invoke(cli, [
            'overlay',
            test_case["openapi_file"],
            test_case["overlay_file"],
            '-o', temp_output.name
        ])
        
        # Check that overlay command succeeded
        assert result.exit_code == 0, f"Overlay command failed for '{test_case['name']}': {result.output}"

        # Load the CLI output
        with open(temp_output.name, 'r', encoding='utf-8') as output_file:
            output_data = yaml.safe_load(output_file)

        # Load the expected output
        with open(test_case["expected_file"], 'r', encoding='utf-8') as expected_file:
            expected_data = yaml.safe_load(expected_file)

        # Compare the output with the expected data
        assert output_data == expected_data, f"Test case '{test_case['name']}' failed."

        # Clean up the temporary file
        os.remove(temp_output.name)
