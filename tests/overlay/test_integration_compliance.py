import os
import tempfile
import yaml
import pytest
from src.oas_patch.oas_patcher_cli import cli
from unittest.mock import patch


@pytest.mark.parametrize("test_case", [
    {
        "name": "add-a-license",
        "openapi_file": "tests/samples/compliance_set/add-a-license/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/add-a-license/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/add-a-license/output.yaml",
    },
    {
        "name": "description-and-summary",
        "openapi_file": "tests/samples/compliance_set/description-and-summary/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/description-and-summary/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/description-and-summary/output.yaml",
    },
    {
        "name": "remove-example",
        "openapi_file": "tests/samples/compliance_set/remove-example/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/remove-example/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/remove-example/output.yaml",
    },
    {
        "name": "remove-matching-responses",
        "openapi_file": "tests/samples/compliance_set/remove-matching-responses/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/remove-matching-responses/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/remove-matching-responses/output.yaml",
    },
    {
        "name": "remove-property",
        "openapi_file": "tests/samples/compliance_set/remove-property/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/remove-property/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/remove-property/output.yaml",
    },
    {
        "name": "remove-server",
        "openapi_file": "tests/samples/compliance_set/remove-server/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/remove-server/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/remove-server/output.yaml",
    },
    {
        "name": "replace-servers-for-sandbox",
        "openapi_file": "tests/samples/compliance_set/replace-servers-for-sandbox/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/replace-servers-for-sandbox/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/replace-servers-for-sandbox/output.yaml",
    },
    {
        "name": "update-root",
        "openapi_file": "tests/samples/compliance_set/update-root/openapi.yaml",
        "overlay_file": "tests/samples/compliance_set/update-root/overlay.yaml",
        "expected_file": "tests/samples/compliance_set/update-root/output.yaml",
    }
])
def test_integration_file_based(test_case, capsys):
    """Test the CLI using input and expected output files."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_output:
        temp_output.close()

        # Mock CLI arguments
        with patch('sys.argv', [
            'oas-patch',
            'overlay',
            test_case["openapi_file"],
            test_case["overlay_file"],
            '-o', temp_output.name
        ]):
            cli()

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
