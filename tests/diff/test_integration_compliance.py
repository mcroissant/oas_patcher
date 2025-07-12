import os
import tempfile
import yaml
import pytest
from click.testing import CliRunner
from oas_patch.oas_patcher_cli import cli


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "add-a-license",
            "openapi_file": "tests/samples/compliance_set/add-a-license/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/add-a-license/overlay.yaml",
            "output_file": "tests/samples/compliance_set/add-a-license/output.yaml",
        },
        {
            "name": "description-and-summary",
            "openapi_file": "tests/samples/compliance_set/description-and-summary/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/description-and-summary/overlay.yaml",
            "output_file": "tests/samples/compliance_set/description-and-summary/output.yaml",
        },
        {
            "name": "remove-example",
            "openapi_file": "tests/samples/compliance_set/remove-example/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/remove-example/overlay.yaml",
            "output_file": "tests/samples/compliance_set/remove-example/output.yaml",
        },
        {
            "name": "remove-matching-responses",
            "openapi_file": "tests/samples/compliance_set/remove-matching-responses/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/remove-matching-responses/overlay.yaml",
            "output_file": "tests/samples/compliance_set/remove-matching-responses/output.yaml",
        },
        {
            "name": "remove-property",
            "openapi_file": "tests/samples/compliance_set/remove-property/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/remove-property/overlay.yaml",
            "output_file": "tests/samples/compliance_set/remove-property/output.yaml",
        },
        {
            "name": "remove-server",
            "openapi_file": "tests/samples/compliance_set/remove-server/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/remove-server/overlay.yaml",
            "output_file": "tests/samples/compliance_set/remove-server/output.yaml",
        },
        {
            "name": "replace-servers-for-sandbox",
            "openapi_file": "tests/samples/compliance_set/replace-servers-for-sandbox/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/replace-servers-for-sandbox/overlay.yaml",
            "output_file": "tests/samples/compliance_set/replace-servers-for-sandbox/output.yaml",
        },
        {
            "name": "update-root",
            "openapi_file": "tests/samples/compliance_set/update-root/openapi.yaml",
            "expected_file": "tests/samples/compliance_set/update-root/overlay.yaml",
            "output_file": "tests/samples/compliance_set/update-root/output.yaml",
        },
    ],
)
def test_integration_file_based(test_case, capsys):
    """Test the CLI using input and expected output files."""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_overlay:
        temp_overlay.close()

        # Generate the overlay using diff command
        result = runner.invoke(
            cli,
            [
                "diff",
                test_case["openapi_file"],
                test_case["output_file"],
                "-o",
                temp_overlay.name,
            ],
        )

        # Check that diff command succeeded
        assert (
            result.exit_code == 0
        ), f"Diff command failed for '{test_case['name']}': {result.output}"

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_output:
            temp_output.close()

            # Apply the overlay using overlay command
            result = runner.invoke(
                cli,
                [
                    "overlay",
                    test_case["openapi_file"],
                    temp_overlay.name,
                    "-o",
                    temp_output.name,
                ],
            )

            # Check that overlay command succeeded
            assert (
                result.exit_code == 0
            ), f"Overlay command failed for '{test_case['name']}': {result.output}"

            # Load the CLI output
            with open(temp_output.name, "r", encoding="utf-8") as output_file:
                output_data = yaml.safe_load(output_file)

            # Load the expected output
            with open(test_case["output_file"], "r", encoding="utf-8") as expected_file:
                expected_data = yaml.safe_load(expected_file)

            # Compare the output with the expected data
            assert (
                output_data == expected_data
            ), f"Test case '{test_case['name']}' failed."

            # Clean up the temporary files
            os.remove(temp_output.name)
            os.remove(temp_overlay.name)
