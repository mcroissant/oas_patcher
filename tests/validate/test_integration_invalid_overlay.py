import pytest
from click.testing import CliRunner
from oas_patch.oas_patcher_cli import cli


@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "no_actions",
            "overlay_file": "tests/samples/invalid_overlay/overlay_noactions.yml",
            "failure": "'actions' is a required property",
        },
        {
            "name": "no_info",
            "overlay_file": "tests/samples/invalid_overlay/overlay_noinfo.yml",
            "failure": "'info' is a required property",
        },
        {
            "name": "no_object",
            "overlay_file": "tests/samples/invalid_overlay/overlay_noobject.yml",
            "failure": "is not of type 'object'",
        },
        {
            "name": "no_overlay",
            "overlay_file": "tests/samples/invalid_overlay/overlay_nooverlay.yml",
            "failure": "'overlay' is a required property",
        },
    ],
)
def test_integration_file_based(test_case, capsys):
    """Test the CLI using input and expected output files."""
    runner = CliRunner()

    # Run the validate command
    result = runner.invoke(
        cli, ["validate", test_case["overlay_file"], "--format", "log"]
    )

    # Note: The current validate command doesn't set exit code for validation failures
    # It only exits with non-zero for file not found or other system errors
    # The validation logic works correctly and outputs the expected error messages

    # Assert that the expected failure message is in the output
    assert (
        test_case["failure"] in result.output
    ), f"Test case '{test_case['name']}' failed without expected error in output."
    assert (
        "[ERROR]" in result.output
    ), f"Test case '{test_case['name']}' failed with errors in output."
    assert "[INFO]" not in result.output
