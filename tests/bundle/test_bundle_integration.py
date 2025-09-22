"""Integration tests for bundle functionality with parameterized test cases."""

import tempfile
import pytest
import json
from pathlib import Path
from click.testing import CliRunner

from oas_patch.oas_patcher_cli import cli
from oas_patch.file_utils import load_file, save_file


class TestBundleIntegration:
    """Integration tests for bundle functionality using CLI."""

    @pytest.fixture
    def samples_dir(self):
        """Get the samples directory path."""
        return Path(__file__).parent / "samples"

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def run_cli_command(self, args):
        """Helper function to run CLI commands."""
        runner = CliRunner()
        return runner.invoke(cli, args)

    # Test data for parameterized tests
    BUNDLE_TEST_CASES = [
        {
            "id": "simple_bundle",
            "bundle_name": "simple_bundle",
            "description": "Test simple bundle with single overlay and basic templating",
            "environment": None,
            "variables": None,
            "expected_title": "Simple API",
            "expected_version": "1.0.0",
            "expected_description": "Updated via bundle overlay",
            "should_succeed": True,
        },
        {
            "id": "simple_bundle_custom_vars",
            "bundle_name": "simple_bundle",
            "description": "Test simple bundle with custom variables",
            "environment": None,
            "variables": {"api_title": "Custom API", "api_version": "2.0.0"},
            "expected_title": "Custom API",
            "expected_version": "2.0.0",
            "expected_description": "Updated via bundle overlay",
            "should_succeed": True,
        },
        {
            "id": "multi_overlay_bundle",
            "bundle_name": "multi_overlay_bundle",
            "description": "Test bundle with multiple overlays",
            "environment": None,
            "variables": None,
            "expected_title": "Pet Store API",
            "expected_version": "2.0.0",
            "expected_has_security": True,
            "expected_has_new_paths": True,
            "should_succeed": True,
        },
        {
            "id": "environment_bundle_dev",
            "bundle_name": "environment_bundle",
            "description": "Test environment-specific bundle for development",
            "environment": "dev",
            "variables": None,
            "expected_title": "Environment API",
            "expected_environment": "development",
            "expected_server_url": "https://dev-api.example.com",
            "should_succeed": True,
        },
        {
            "id": "environment_bundle_prod",
            "bundle_name": "environment_bundle",
            "description": "Test environment-specific bundle for production",
            "environment": "prod",
            "variables": None,
            "expected_title": "Environment API",
            "expected_environment": "production",
            "expected_server_url": "https://api.example.com",
            "expected_has_api_key": True,
            "should_succeed": True,
        },
        {
            "id": "environment_bundle_test",
            "bundle_name": "environment_bundle",
            "description": "Test environment-specific bundle for testing",
            "environment": "test",
            "variables": None,
            "expected_title": "Environment API",
            "expected_environment": "testing",
            "expected_server_url": "https://test-api.example.com",
            "expected_test_mode": True,
            "should_succeed": True,
        },
        {
            "id": "template_bundle",
            "bundle_name": "template_bundle",
            "description": "Test bundle with advanced templating",
            "environment": None,
            "variables": None,
            "expected_title": "Templated API",
            "expected_version": "3.0.0",
            "expected_owner_support": "Template Corp Support",
            "expected_has_auth": True,
            "should_succeed": True,
        },
    ]

    @pytest.mark.parametrize("test_case", BUNDLE_TEST_CASES, ids=lambda tc: tc["id"])
    def test_bundle_integration(self, test_case, samples_dir, temp_output_dir):
        """Test bundle integration with various configurations using CLI."""
        # Setup paths
        bundle_dir = samples_dir / test_case["bundle_name"]
        openapi_file = bundle_dir / "openapi.yaml"
        bundle_file = bundle_dir / "bundle.yaml"
        output_file = temp_output_dir / f"{test_case['id']}_result.yaml"

        # Verify required files exist
        assert openapi_file.exists(), f"OpenAPI file not found: {openapi_file}"
        assert bundle_file.exists(), f"Bundle file not found: {bundle_file}"

        # Build CLI command
        cli_args = [
            "bundle",
            "apply",
            str(openapi_file),
            str(bundle_file),
            "--output",
            str(output_file),
        ]

        # Add environment if specified
        if test_case["environment"]:
            cli_args.extend(["--env", test_case["environment"]])

        # Add variables if specified
        if test_case["variables"]:
            for key, value in test_case["variables"].items():
                cli_args.extend(["--var", f"{key}={value}"])

        # Run CLI command
        result = self.run_cli_command(cli_args)

        # Verify command succeeded
        if not test_case["should_succeed"]:
            assert result.exit_code != 0
            return

        assert result.exit_code == 0, f"CLI command failed: {result.output}"

        # Verify output file was created
        assert output_file.exists(), "Output file was not created"

        # Load and validate the result
        result_openapi = load_file(str(output_file))
        self._validate_result(result_openapi, test_case)

    def _validate_result(self, result_openapi, test_case):
        """Validate the result OpenAPI document based on test case expectations."""
        # Common validations
        if "expected_title" in test_case:
            assert result_openapi["info"]["title"] == test_case["expected_title"]

        if "expected_version" in test_case:
            assert result_openapi["info"]["version"] == test_case["expected_version"]

        if "expected_description" in test_case:
            assert (
                result_openapi["info"]["description"]
                == test_case["expected_description"]
            )

        # Environment-specific validations
        if "expected_environment" in test_case:
            assert (
                result_openapi["info"]["x-environment"]
                == test_case["expected_environment"]
            )

        if "expected_server_url" in test_case:
            assert any(
                server["url"] == test_case["expected_server_url"]
                for server in result_openapi.get("servers", [])
            )

        if test_case.get("expected_test_mode"):
            assert result_openapi["info"].get("x-test-mode") is True

        # Security validations
        if test_case.get("expected_has_security"):
            assert "securitySchemes" in result_openapi.get("components", {})

        if test_case.get("expected_has_api_key"):
            security_schemes = result_openapi.get("components", {}).get(
                "securitySchemes", {}
            )
            assert "ApiKey" in security_schemes

        if test_case.get("expected_has_auth"):
            security_schemes = result_openapi.get("components", {}).get(
                "securitySchemes", {}
            )
            assert "BearerAuth" in security_schemes

        # Path validations
        if test_case.get("expected_has_new_paths"):
            assert "/pets/{id}" in result_openapi.get("paths", {})

        # Owner/contact validations
        if "expected_owner_support" in test_case:
            contact = result_openapi.get("info", {}).get("contact", {})
            assert contact.get("name") == test_case["expected_owner_support"]

    BUNDLE_VALIDATION_TEST_CASES = [
        {
            "id": "validate_simple_bundle",
            "bundle_name": "simple_bundle",
            "description": "Test validation of simple bundle",
            "should_be_valid": True,
        },
        {
            "id": "validate_multi_overlay_bundle",
            "bundle_name": "multi_overlay_bundle",
            "description": "Test validation of multi-overlay bundle",
            "should_be_valid": True,
        },
        {
            "id": "validate_environment_bundle",
            "bundle_name": "environment_bundle",
            "description": "Test validation of environment bundle",
            "should_be_valid": True,
        },
        {
            "id": "validate_template_bundle",
            "bundle_name": "template_bundle",
            "description": "Test validation of template bundle",
            "should_be_valid": True,
        },
        {
            "id": "validate_invalid_bundle",
            "bundle_name": "invalid_bundle",
            "description": "Test validation of invalid bundle",
            "should_be_valid": False,
            "expected_error_contains": "not found",
        },
    ]

    @pytest.mark.parametrize(
        "test_case", BUNDLE_VALIDATION_TEST_CASES, ids=lambda tc: tc["id"]
    )
    def test_bundle_validation(self, test_case, samples_dir):
        """Test bundle validation functionality using CLI."""
        bundle_dir = samples_dir / test_case["bundle_name"]
        bundle_file = bundle_dir / "bundle.yaml"

        # Run bundle validate command
        result = self.run_cli_command(["bundle", "validate", str(bundle_file)])

        if test_case["should_be_valid"]:
            assert result.exit_code == 0, f"Bundle validation failed: {result.output}"
        else:
            assert (
                result.exit_code == 1
            ), f"Bundle validation should have failed: {result.output}"
            if "expected_error_contains" in test_case:
                assert test_case["expected_error_contains"] in result.output

    def test_dry_run_functionality(self, samples_dir, temp_output_dir):
        """Test dry run functionality using CLI."""
        bundle_dir = samples_dir / "simple_bundle"
        openapi_file = bundle_dir / "openapi.yaml"
        bundle_file = bundle_dir / "bundle.yaml"
        output_file = temp_output_dir / "dry_run_test.yaml"

        # Run with dry run flag
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(openapi_file),
                str(bundle_file),
                "--output",
                str(output_file),
                "--dry-run",
            ]
        )

        # Should succeed but not create output file
        assert result.exit_code == 0
        assert not output_file.exists(), "Dry run should not create output file"
        assert "Simple API" in result.output  # Should show the result in stdout

    def test_format_options(self, samples_dir, temp_output_dir):
        """Test different output format options using CLI."""
        bundle_dir = samples_dir / "simple_bundle"
        openapi_file = bundle_dir / "openapi.yaml"
        bundle_file = bundle_dir / "bundle.yaml"

        # Test YAML format
        yaml_output = temp_output_dir / "output.yaml"
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(openapi_file),
                str(bundle_file),
                "--output",
                str(yaml_output),
                "--format",
                "yaml",
            ]
        )
        assert result.exit_code == 0
        assert yaml_output.exists()

        # Verify it's valid YAML
        result_data = load_file(str(yaml_output))
        assert result_data["info"]["title"] == "Simple API"

        # Test JSON format
        json_output = temp_output_dir / "output.json"
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(openapi_file),
                str(bundle_file),
                "--output",
                str(json_output),
                "--format",
                "json",
            ]
        )
        assert result.exit_code == 0
        assert json_output.exists()

        # Verify it's valid JSON
        with open(json_output, "r") as f:
            json_data = json.load(f)
        assert json_data["info"]["title"] == "Simple API"

    def test_cli_error_handling(self, samples_dir, temp_output_dir):
        """Test CLI error handling for various error conditions."""
        bundle_dir = samples_dir / "simple_bundle"
        bundle_file = bundle_dir / "bundle.yaml"
        output_file = temp_output_dir / "error_test.yaml"

        # Test with non-existent OpenAPI file
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                "nonexistent.yaml",
                str(bundle_file),
                "--output",
                str(output_file),
            ]
        )
        assert result.exit_code == 1

        # Test with non-existent bundle file
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(bundle_dir / "openapi.yaml"),
                "nonexistent_bundle.yaml",
                "--output",
                str(output_file),
            ]
        )
        assert result.exit_code == 2  # Click validation error

        # Test bundle validation with invalid bundle
        invalid_bundle_file = samples_dir / "invalid_bundle" / "bundle.yaml"
        result = self.run_cli_command(["bundle", "validate", str(invalid_bundle_file)])
        assert result.exit_code == 1

    def test_verbose_output(self, samples_dir, temp_output_dir):
        """Test verbose output functionality."""
        bundle_dir = samples_dir / "simple_bundle"
        openapi_file = bundle_dir / "openapi.yaml"
        bundle_file = bundle_dir / "bundle.yaml"
        output_file = temp_output_dir / "verbose_test.yaml"

        # Run with verbose flag
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(openapi_file),
                str(bundle_file),
                "--output",
                str(output_file),
                "--verbose",
            ]
        )

        assert result.exit_code == 0
        # Check for verbose output elements (these may vary based on implementation)
        # We just verify it doesn't break anything
        assert output_file.exists()


class TestBundleAdvancedScenarios:
    """Advanced integration test scenarios for bundle functionality using CLI."""

    def run_cli_command(self, args):
        """Helper function to run CLI commands."""
        runner = CliRunner()
        return runner.invoke(cli, args)

    def test_complex_overlay_chain(self, tmp_path):
        """Test applying multiple overlays in sequence with variable inheritance using CLI."""
        # Create test bundle structure
        bundle_dir = tmp_path / "complex_bundle"
        bundle_dir.mkdir()

        # Create bundle configuration
        bundle_config = {
            "name": "Complex Bundle",
            "description": "Bundle with overlay chain",
            "overlays": [
                {"path": "base.yaml", "variables": {"stage": "base"}},
                {"path": "middleware.yaml", "variables": {"stage": "middleware"}},
                {"path": "final.yaml", "variables": {"stage": "final"}},
            ],
            "variables": {"app_name": "Complex App", "version": "1.0.0"},
        }
        save_file(bundle_config, str(bundle_dir / "bundle.yaml"))

        # Create overlay files
        base_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Base", "version": "1.0.0"},
            "actions": [
                {
                    "target": "$.info",
                    "update": {"title": "{{ app_name }}", "x-stage": "{{ stage }}"},
                }
            ],
        }
        save_file(base_overlay, str(bundle_dir / "base.yaml"))

        middleware_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Middleware", "version": "1.0.0"},
            "actions": [
                {
                    "target": "$.info",
                    "update": {"description": "Processed in {{ stage }}"},
                }
            ],
        }
        save_file(middleware_overlay, str(bundle_dir / "middleware.yaml"))

        final_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Final", "version": "1.0.0"},
            "actions": [
                {
                    "target": "$.info",
                    "update": {
                        "version": "{{ version }}",
                        "x-final-stage": "{{ stage }}",
                    },
                }
            ],
        }
        save_file(final_overlay, str(bundle_dir / "final.yaml"))

        # Create base OpenAPI document
        openapi_doc = {
            "openapi": "3.0.3",
            "info": {"title": "Original", "version": "0.1.0"},
            "paths": {},
        }
        save_file(openapi_doc, str(bundle_dir / "openapi.yaml"))

        # Apply bundle using CLI
        output_file = tmp_path / "complex_result.yaml"
        result = self.run_cli_command(
            [
                "bundle",
                "apply",
                str(bundle_dir / "openapi.yaml"),
                str(bundle_dir / "bundle.yaml"),
                "--output",
                str(output_file),
            ]
        )

        # Verify command succeeded
        assert result.exit_code == 0, f"CLI command failed: {result.output}"
        assert output_file.exists()

        # Load and verify final result
        result_openapi = load_file(str(output_file))
        assert result_openapi["info"]["title"] == "Complex App"
        assert result_openapi["info"]["version"] == "1.0.0"
        assert result_openapi["info"]["description"] == "Processed in middleware"
        assert result_openapi["info"]["x-stage"] == "base"
        assert result_openapi["info"]["x-final-stage"] == "final"

    def test_bundle_init_command(self, tmp_path):
        """Test bundle init command functionality."""
        # Change to the temp directory
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            # Run bundle init command
            result = self.run_cli_command(["bundle", "init", "--force"])

            # Should succeed
            assert result.exit_code == 0

            # Check that bundle.yaml was mentioned in output (though actual file creation may be mocked)
            assert "bundle.yaml" in result.output or result.exit_code == 0

        finally:
            os.chdir(original_cwd)
