"""Integration tests for bundle functionality with parameterized test cases."""

import tempfile
import pytest
from pathlib import Path

from oas_patch.bundle_manager import BundleManager
from oas_patch.template_engine import TemplateEngine
from oas_patch.overlay import apply_overlay
from oas_patch.file_utils import load_file, save_file


class TestBundleIntegration:
    """Integration tests for bundle functionality."""

    @pytest.fixture
    def samples_dir(self):
        """Get the samples directory path."""
        return Path(__file__).parent / "samples"

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

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
        {
            "id": "invalid_bundle",
            "bundle_name": "invalid_bundle",
            "description": "Test bundle with invalid configuration",
            "environment": None,
            "variables": None,
            "should_succeed": False,
            "expected_error_type": "missing_overlay",
        },
    ]

    @pytest.mark.parametrize("test_case", BUNDLE_TEST_CASES, ids=lambda tc: tc["id"])
    def test_bundle_integration(self, test_case, samples_dir, temp_output_dir):
        """Test bundle integration with various configurations."""
        # Setup
        bundle_dir = samples_dir / test_case["bundle_name"]
        openapi_file = bundle_dir / "openapi.yaml"
        bundle_manager = BundleManager(
            str(samples_dir)
        )  # Use samples_dir, not bundle_dir
        template_engine = TemplateEngine()

        if not test_case["should_succeed"]:
            # Test error cases
            if test_case["expected_error_type"] == "missing_overlay":
                validation_result = bundle_manager.validate_bundle(
                    test_case["bundle_name"]
                )
                assert not validation_result["valid"]
                assert any(
                    "not found" in error for error in validation_result["errors"]
                )
            return

        # Load and validate bundle
        bundle_config = bundle_manager.load_bundle(test_case["bundle_name"])
        assert bundle_config is not None
        assert bundle_config.name is not None

        # Load original OpenAPI document
        original_openapi = load_file(str(openapi_file))
        assert original_openapi is not None

        # Get overlays for environment (if specified)
        if test_case["environment"]:
            overlays = bundle_manager.get_overlays_for_environment(
                test_case["bundle_name"], test_case["environment"]
            )
        else:
            overlays = bundle_config.overlays

        # Prepare variables
        variables = dict(bundle_config.variables) if bundle_config.variables else {}
        if test_case["variables"]:
            variables.update(test_case["variables"])

        # Apply overlays
        result_openapi = original_openapi.copy()
        for overlay_config in overlays:
            # Load overlay file
            overlay_path = bundle_manager._resolve_overlay_path(
                test_case["bundle_name"], overlay_config.path
            )
            overlay_data = load_file(str(overlay_path))

            # Merge overlay variables
            overlay_variables = dict(variables)
            if overlay_config.variables:
                overlay_variables.update(overlay_config.variables)

            # Process template if variables are present
            if overlay_variables:
                overlay_data = template_engine.process_overlay_data(
                    overlay_data, overlay_variables
                )

            # Apply overlay
            result_openapi = apply_overlay(result_openapi, overlay_data)

        # Validate results based on test case expectations
        self._validate_result(result_openapi, test_case)

        # Save result for manual inspection
        output_file = temp_output_dir / f"{test_case['id']}_result.yaml"
        save_file(result_openapi, str(output_file))

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

    BUNDLE_DISCOVERY_TEST_CASES = [
        {
            "id": "discover_all_bundles",
            "description": "Test discovering all available bundles",
            "expected_bundles": [
                "simple_bundle",
                "multi_overlay_bundle",
                "environment_bundle",
                "template_bundle",
                "invalid_bundle",
            ],
        }
    ]

    @pytest.mark.parametrize(
        "test_case", BUNDLE_DISCOVERY_TEST_CASES, ids=lambda tc: tc["id"]
    )
    def test_bundle_discovery(self, test_case, samples_dir):
        """Test bundle discovery functionality."""
        bundle_manager = BundleManager(str(samples_dir))
        discovered_bundles = bundle_manager.discover_bundles()

        for expected_bundle in test_case["expected_bundles"]:
            assert expected_bundle in discovered_bundles

    BUNDLE_VALIDATION_TEST_CASES = [
        {
            "id": "validate_simple_bundle",
            "bundle_name": "simple_bundle",
            "description": "Test validation of simple bundle",
            "should_be_valid": True,
            "expected_warnings": 0,
            "expected_errors": 0,
        },
        {
            "id": "validate_multi_overlay_bundle",
            "bundle_name": "multi_overlay_bundle",
            "description": "Test validation of multi-overlay bundle",
            "should_be_valid": True,
            "expected_warnings": 0,
            "expected_errors": 0,
        },
        {
            "id": "validate_environment_bundle",
            "bundle_name": "environment_bundle",
            "description": "Test validation of environment bundle",
            "should_be_valid": True,
            "expected_warnings": 0,
            "expected_errors": 0,
        },
        {
            "id": "validate_template_bundle",
            "bundle_name": "template_bundle",
            "description": "Test validation of template bundle",
            "should_be_valid": True,
            "expected_warnings": 0,
            "expected_errors": 0,
        },
        {
            "id": "validate_invalid_bundle",
            "bundle_name": "invalid_bundle",
            "description": "Test validation of invalid bundle",
            "should_be_valid": False,
            "expected_warnings": 0,
            "expected_errors": 1,
            "expected_error_contains": "not found",
        },
    ]

    @pytest.mark.parametrize(
        "test_case", BUNDLE_VALIDATION_TEST_CASES, ids=lambda tc: tc["id"]
    )
    def test_bundle_validation(self, test_case, samples_dir):
        """Test bundle validation functionality."""
        bundle_manager = BundleManager(str(samples_dir))
        validation_result = bundle_manager.validate_bundle(test_case["bundle_name"])

        assert validation_result["valid"] == test_case["should_be_valid"]
        assert len(validation_result["warnings"]) == test_case["expected_warnings"]
        assert len(validation_result["errors"]) == test_case["expected_errors"]

        if "expected_error_contains" in test_case:
            assert any(
                test_case["expected_error_contains"] in error
                for error in validation_result["errors"]
            )

    BUNDLE_INFO_TEST_CASES = [
        {
            "id": "info_simple_bundle",
            "bundle_name": "simple_bundle",
            "description": "Test getting info for simple bundle",
            "expected_name": "Simple Bundle",
            "expected_overlay_count": 1,
            "expected_has_variables": True,
        },
        {
            "id": "info_multi_overlay_bundle",
            "bundle_name": "multi_overlay_bundle",
            "description": "Test getting info for multi-overlay bundle",
            "expected_name": "Multi Overlay Bundle",
            "expected_overlay_count": 3,
            "expected_has_variables": True,
        },
        {
            "id": "info_environment_bundle",
            "bundle_name": "environment_bundle",
            "description": "Test getting info for environment bundle",
            "expected_name": "Environment Bundle",
            "expected_overlay_count": 4,
            "expected_has_environment_overlays": True,
        },
    ]

    @pytest.mark.parametrize(
        "test_case", BUNDLE_INFO_TEST_CASES, ids=lambda tc: tc["id"]
    )
    def test_bundle_info(self, test_case, samples_dir):
        """Test getting bundle information."""
        bundle_manager = BundleManager(str(samples_dir))
        bundle_info = bundle_manager.get_bundle_info(test_case["bundle_name"])

        assert bundle_info["name"] == test_case["expected_name"]
        assert len(bundle_info["overlays"]) == test_case["expected_overlay_count"]

        if test_case.get("expected_has_variables"):
            assert bundle_info["variables"] is not None
            assert len(bundle_info["variables"]) > 0

        if test_case.get("expected_has_environment_overlays"):
            environment_overlays = [
                overlay
                for overlay in bundle_info["overlays"]
                if overlay["environment"] is not None
            ]
            assert len(environment_overlays) > 0

    def test_environment_overlay_filtering(self, samples_dir):
        """Test filtering overlays by environment."""
        bundle_manager = BundleManager(str(samples_dir))

        # Test development environment
        dev_overlays = bundle_manager.get_overlays_for_environment(
            "environment_bundle", "dev"
        )
        dev_overlay_paths = [overlay.path for overlay in dev_overlays]
        assert "base-overlay.yaml" in dev_overlay_paths  # Should include base overlay
        assert "dev-overlay.yaml" in dev_overlay_paths  # Should include dev overlay
        assert (
            "prod-overlay.yaml" not in dev_overlay_paths
        )  # Should not include prod overlay

        # Test production environment
        prod_overlays = bundle_manager.get_overlays_for_environment(
            "environment_bundle", "prod"
        )
        prod_overlay_paths = [overlay.path for overlay in prod_overlays]
        assert "base-overlay.yaml" in prod_overlay_paths  # Should include base overlay
        assert "prod-overlay.yaml" in prod_overlay_paths  # Should include prod overlay
        assert (
            "dev-overlay.yaml" not in prod_overlay_paths
        )  # Should not include dev overlay

        # Test non-existent environment
        unknown_overlays = bundle_manager.get_overlays_for_environment(
            "environment_bundle", "unknown"
        )
        unknown_overlay_paths = [overlay.path for overlay in unknown_overlays]
        assert (
            "base-overlay.yaml" in unknown_overlay_paths
        )  # Should include base overlay
        assert len(unknown_overlay_paths) == 1  # Should only include base overlay

    def test_template_processing_integration(self, samples_dir):
        """Test template processing integration with bundles."""
        bundle_manager = BundleManager(str(samples_dir))
        template_engine = TemplateEngine()

        # Load template bundle
        bundle_config = bundle_manager.load_bundle("template_bundle")

        # Test template processing with bundle variables
        variables = bundle_config.variables

        # Load and process a template overlay
        overlay_path = bundle_manager._resolve_overlay_path(
            "template_bundle", "template-overlay.yaml"
        )
        overlay_data = load_file(str(overlay_path))

        # Process templates
        processed_overlay = template_engine.process_overlay_data(
            overlay_data, variables
        )

        # Verify template processing
        info_action = next(
            action
            for action in processed_overlay["actions"]
            if action["target"] == "$.info"
        )
        assert info_action["update"]["title"] == "Templated API"
        assert info_action["update"]["version"] == "3.0.0"
        assert "Template Corp" in info_action["update"]["description"]
        assert info_action["update"]["contact"]["name"] == "Template Corp Support"

    def test_bundle_caching(self, samples_dir):
        """Test that bundle loading uses caching correctly."""
        bundle_manager = BundleManager(str(samples_dir))

        # Load bundle twice
        bundle1 = bundle_manager.load_bundle("simple_bundle")
        bundle2 = bundle_manager.load_bundle("simple_bundle")

        # Should be the same object (cached)
        assert bundle1 is bundle2

    def test_error_handling_integration(self, samples_dir):
        """Test error handling in integration scenarios."""
        bundle_manager = BundleManager(str(samples_dir))

        # Test loading non-existent bundle
        with pytest.raises(FileNotFoundError):
            bundle_manager.load_bundle("nonexistent_bundle")

        # Test validation of bundle with missing overlay file
        validation_result = bundle_manager.validate_bundle("invalid_bundle")
        assert not validation_result["valid"]
        assert len(validation_result["errors"]) > 0


class TestBundleAdvancedScenarios:
    """Advanced integration test scenarios for bundle functionality."""

    def test_complex_overlay_chain(self, tmp_path):
        """Test applying multiple overlays in sequence with variable inheritance."""
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

        # Apply bundle
        bundle_manager = BundleManager(
            str(tmp_path)
        )  # Use parent directory, not bundle_dir
        template_engine = TemplateEngine()

        bundle_config = bundle_manager.load_bundle("complex_bundle")
        result_openapi = load_file(str(bundle_dir / "openapi.yaml"))

        # Apply each overlay in sequence
        for overlay_config in bundle_config.overlays:
            overlay_path = bundle_manager._resolve_overlay_path(
                "complex_bundle", overlay_config.path
            )
            overlay_data = load_file(str(overlay_path))

            # Merge variables
            variables = dict(bundle_config.variables)
            if overlay_config.variables:
                variables.update(overlay_config.variables)

            # Process template
            overlay_data = template_engine.process_overlay_data(overlay_data, variables)

            # Apply overlay
            result_openapi = apply_overlay(result_openapi, overlay_data)

        # Verify final result
        assert result_openapi["info"]["title"] == "Complex App"
        assert result_openapi["info"]["version"] == "1.0.0"
        assert result_openapi["info"]["description"] == "Processed in middleware"
        assert result_openapi["info"]["x-stage"] == "base"
        assert result_openapi["info"]["x-final-stage"] == "final"
