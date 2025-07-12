"""Unit tests for the BundleManager class."""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from oas_patch.bundle_manager import BundleManager, BundleConfig, OverlayConfig


class TestBundleManager:
    """Test cases for BundleManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.bundle_manager = BundleManager(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_config_dir(self):
        """Test BundleManager initialization with default config directory."""
        manager = BundleManager()
        assert manager.config_dir == Path("overlays")
        assert manager._bundles_cache == {}

    def test_init_custom_config_dir(self):
        """Test BundleManager initialization with custom config directory."""
        custom_dir = "/custom/path"
        manager = BundleManager(custom_dir)
        assert manager.config_dir == Path(custom_dir)

    def test_discover_bundles_empty_directory(self):
        """Test discovering bundles in empty directory."""
        bundles = self.bundle_manager.discover_bundles()
        assert bundles == []

    def test_discover_bundles_nonexistent_directory(self):
        """Test discovering bundles when config directory doesn't exist."""
        manager = BundleManager("nonexistent")
        bundles = manager.discover_bundles()
        assert bundles == []

    def test_discover_bundles_with_yaml_files(self):
        """Test discovering bundles with YAML bundle files."""
        # Create test bundle directories
        bundle1_dir = Path(self.temp_dir) / "bundle1"
        bundle2_dir = Path(self.temp_dir) / "bundle2"
        bundle1_dir.mkdir()
        bundle2_dir.mkdir()

        # Create bundle.yaml files
        (bundle1_dir / "bundle.yaml").touch()
        (bundle2_dir / "bundle.yml").touch()

        bundles = self.bundle_manager.discover_bundles()
        assert sorted(bundles) == ["bundle1", "bundle2"]

    def test_discover_bundles_deduplicate(self):
        """Test that duplicate bundle names are deduplicated."""
        # Create bundle directory with both .yaml and .yml files
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        (bundle_dir / "bundle.yaml").touch()
        (bundle_dir / "bundle.yml").touch()

        bundles = self.bundle_manager.discover_bundles()
        assert bundles == ["testbundle"]

    @patch("oas_patch.bundle_manager.load_file")
    def test_load_bundle_success(self, mock_load_file):
        """Test successful bundle loading."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        # Mock file content
        mock_config = {
            "name": "Test Bundle",
            "description": "A test bundle",
            "version": "1.0.0",
            "overlays": [
                {
                    "path": "overlay1.yaml",
                    "description": "First overlay",
                    "environment": ["dev", "test"],
                }
            ],
            "variables": {"env": "test"},
        }
        mock_load_file.return_value = mock_config

        bundle = self.bundle_manager.load_bundle("testbundle")

        assert isinstance(bundle, BundleConfig)
        assert bundle.name == "Test Bundle"
        assert bundle.description == "A test bundle"
        assert bundle.version == "1.0.0"
        assert len(bundle.overlays) == 1
        assert bundle.overlays[0].path == "overlay1.yaml"
        assert bundle.overlays[0].environment == ["dev", "test"]
        assert bundle.variables == {"env": "test"}

    def test_load_bundle_not_found(self):
        """Test loading non-existent bundle."""
        with pytest.raises(FileNotFoundError, match="Bundle 'nonexistent' not found"):
            self.bundle_manager.load_bundle("nonexistent")

    @patch("oas_patch.bundle_manager.load_file")
    def test_load_bundle_invalid_config(self, mock_load_file):
        """Test loading bundle with invalid configuration."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_load_file.side_effect = ValueError("Invalid YAML")

        with pytest.raises(ValueError, match="Failed to load bundle 'testbundle'"):
            self.bundle_manager.load_bundle("testbundle")

    @patch("oas_patch.bundle_manager.load_file")
    def test_load_bundle_caching(self, mock_load_file):
        """Test that loaded bundles are cached."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_config = {
            "name": "Test Bundle",
            "description": "A test bundle",
            "overlays": [],
        }
        mock_load_file.return_value = mock_config

        # Load bundle twice
        bundle1 = self.bundle_manager.load_bundle("testbundle")
        bundle2 = self.bundle_manager.load_bundle("testbundle")

        # Should be the same object (cached)
        assert bundle1 is bundle2
        # load_file should only be called once
        assert mock_load_file.call_count == 1

    def test_find_bundle_config_yaml_extension(self):
        """Test finding bundle config with .yaml extension."""
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        found_path = self.bundle_manager._find_bundle_config("testbundle")
        assert found_path == config_file

    def test_find_bundle_config_yml_extension(self):
        """Test finding bundle config with .yml extension."""
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yml"
        config_file.touch()

        found_path = self.bundle_manager._find_bundle_config("testbundle")
        assert found_path == config_file

    def test_find_bundle_config_root_level(self):
        """Test finding bundle config at root level."""
        config_file = Path(self.temp_dir) / "testbundle.yaml"
        config_file.touch()

        found_path = self.bundle_manager._find_bundle_config("testbundle")
        assert found_path == config_file

    def test_find_bundle_config_not_found(self):
        """Test finding non-existent bundle config."""
        found_path = self.bundle_manager._find_bundle_config("nonexistent")
        assert found_path is None

    def test_parse_bundle_config_minimal(self):
        """Test parsing minimal bundle configuration."""
        config_data = {"overlays": [{"path": "overlay1.yaml"}]}

        bundle = self.bundle_manager._parse_bundle_config(config_data, "testbundle")

        assert bundle.name == "testbundle"
        assert bundle.description == ""
        assert bundle.version == "1.0.0"
        assert len(bundle.overlays) == 1
        assert bundle.overlays[0].path == "overlay1.yaml"
        assert bundle.overlays[0].environment is None
        assert bundle.overlays[0].description is None
        assert bundle.overlays[0].variables == {}

    def test_parse_bundle_config_complete(self):
        """Test parsing complete bundle configuration."""
        config_data = {
            "name": "Complete Bundle",
            "description": "A complete test bundle",
            "version": "2.0.0",
            "overlays": [
                {
                    "path": "overlay1.yaml",
                    "environment": ["prod"],
                    "description": "Production overlay",
                    "variables": {"key": "value"},
                }
            ],
            "variables": {"global_var": "global_value"},
        }

        bundle = self.bundle_manager._parse_bundle_config(config_data, "testbundle")

        assert bundle.name == "Complete Bundle"
        assert bundle.description == "A complete test bundle"
        assert bundle.version == "2.0.0"
        assert len(bundle.overlays) == 1
        assert bundle.overlays[0].path == "overlay1.yaml"
        assert bundle.overlays[0].environment == ["prod"]
        assert bundle.overlays[0].description == "Production overlay"
        assert bundle.overlays[0].variables == {"key": "value"}
        assert bundle.variables == {"global_var": "global_value"}

    @patch("oas_patch.bundle_manager.load_file")
    def test_validate_bundle_success(self, mock_load_file):
        """Test successful bundle validation."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        # Create overlay file
        overlay_file = bundle_dir / "overlay1.yaml"
        overlay_file.touch()

        # Mock file loading
        mock_config = {"overlays": [{"path": "overlay1.yaml"}]}
        mock_overlay = {"info": {"title": "Test"}}

        def load_file_side_effect(path):
            if "bundle.yaml" in path:
                return mock_config
            elif "overlay1.yaml" in path:
                return mock_overlay
            return {}

        mock_load_file.side_effect = load_file_side_effect

        result = self.bundle_manager.validate_bundle("testbundle")

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    @patch("oas_patch.bundle_manager.load_file")
    def test_validate_bundle_no_overlays(self, mock_load_file):
        """Test bundle validation with no overlays."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_config = {"overlays": []}
        mock_load_file.return_value = mock_config

        result = self.bundle_manager.validate_bundle("testbundle")

        assert result["valid"] is True
        assert result["errors"] == []
        assert "Bundle contains no overlays" in result["warnings"]

    @patch("oas_patch.bundle_manager.load_file")
    def test_validate_bundle_missing_overlay_file(self, mock_load_file):
        """Test bundle validation with missing overlay file."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_config = {"overlays": [{"path": "missing_overlay.yaml"}]}
        mock_load_file.return_value = mock_config

        result = self.bundle_manager.validate_bundle("testbundle")

        assert result["valid"] is False
        assert "Overlay file not found: missing_overlay.yaml" in result["errors"]

    @patch("oas_patch.bundle_manager.load_file")
    def test_validate_bundle_invalid_overlay_format(self, mock_load_file):
        """Test bundle validation with invalid overlay file format."""
        # Create bundle config file and overlay file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()
        overlay_file = bundle_dir / "overlay1.yaml"
        overlay_file.touch()

        mock_config = {"overlays": [{"path": "overlay1.yaml"}]}

        def load_file_side_effect(path):
            if "bundle.yaml" in path:
                return mock_config
            elif "overlay1.yaml" in path:
                raise ValueError("Invalid YAML format")
            return {}

        mock_load_file.side_effect = load_file_side_effect

        result = self.bundle_manager.validate_bundle("testbundle")

        assert result["valid"] is False
        assert "Invalid overlay file format 'overlay1.yaml'" in str(result["errors"])

    def test_validate_bundle_bundle_not_found(self):
        """Test bundle validation with non-existent bundle."""
        result = self.bundle_manager.validate_bundle("nonexistent")

        assert result["valid"] is False
        assert "Bundle validation failed" in str(result["errors"])

    def test_resolve_overlay_path_absolute(self):
        """Test resolving absolute overlay path."""
        absolute_path = "/absolute/path/overlay.yaml"
        resolved = self.bundle_manager._resolve_overlay_path(
            "testbundle", absolute_path
        )
        assert resolved == Path(absolute_path)

    def test_resolve_overlay_path_relative_to_bundle(self):
        """Test resolving overlay path relative to bundle directory."""
        # Create bundle directory and overlay file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        overlay_file = bundle_dir / "overlay.yaml"
        overlay_file.touch()

        resolved = self.bundle_manager._resolve_overlay_path(
            "testbundle", "overlay.yaml"
        )
        assert resolved == overlay_file

    def test_resolve_overlay_path_relative_to_config(self):
        """Test resolving overlay path relative to config directory."""
        # Create overlay file in config root
        overlay_file = Path(self.temp_dir) / "overlay.yaml"
        overlay_file.touch()

        resolved = self.bundle_manager._resolve_overlay_path(
            "testbundle", "overlay.yaml"
        )
        assert resolved == overlay_file

    @patch("oas_patch.bundle_manager.load_file")
    def test_get_overlays_for_environment(self, mock_load_file):
        """Test filtering overlays by environment."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_config = {
            "overlays": [
                {"path": "overlay1.yaml", "environment": ["dev", "test"]},
                {"path": "overlay2.yaml", "environment": ["prod"]},
                {"path": "overlay3.yaml"},  # No environment restriction
            ]
        }
        mock_load_file.return_value = mock_config

        # Test dev environment
        dev_overlays = self.bundle_manager.get_overlays_for_environment(
            "testbundle", "dev"
        )
        assert len(dev_overlays) == 2
        assert dev_overlays[0].path == "overlay1.yaml"
        assert dev_overlays[1].path == "overlay3.yaml"

        # Test prod environment
        prod_overlays = self.bundle_manager.get_overlays_for_environment(
            "testbundle", "prod"
        )
        assert len(prod_overlays) == 2
        assert prod_overlays[0].path == "overlay2.yaml"
        assert prod_overlays[1].path == "overlay3.yaml"

    @patch("oas_patch.bundle_manager.load_file")
    @patch.object(BundleManager, "validate_bundle")
    def test_get_bundle_info(self, mock_validate, mock_load_file):
        """Test getting bundle information."""
        # Create bundle config file
        bundle_dir = Path(self.temp_dir) / "testbundle"
        bundle_dir.mkdir()
        config_file = bundle_dir / "bundle.yaml"
        config_file.touch()

        mock_config = {
            "name": "Test Bundle",
            "description": "A test bundle",
            "version": "1.0.0",
            "overlays": [
                {
                    "path": "overlay1.yaml",
                    "environment": ["dev"],
                    "description": "Dev overlay",
                    "variables": {"key": "value"},
                }
            ],
            "variables": {"global_var": "global_value"},
        }
        mock_load_file.return_value = mock_config

        mock_validation = {"valid": True, "errors": [], "warnings": []}
        mock_validate.return_value = mock_validation

        info = self.bundle_manager.get_bundle_info("testbundle")

        assert info["name"] == "Test Bundle"
        assert info["description"] == "A test bundle"
        assert info["version"] == "1.0.0"
        assert len(info["overlays"]) == 1
        assert info["overlays"][0]["path"] == "overlay1.yaml"
        assert info["overlays"][0]["environment"] == ["dev"]
        assert info["overlays"][0]["description"] == "Dev overlay"
        assert info["overlays"][0]["variables"] == {"key": "value"}
        assert info["variables"] == {"global_var": "global_value"}
        assert info["validation"] == mock_validation


class TestBundleConfig:
    """Test cases for BundleConfig dataclass."""

    def test_bundle_config_creation(self):
        """Test BundleConfig creation with all fields."""
        overlays = [OverlayConfig(path="test.yaml")]
        bundle = BundleConfig(
            name="Test Bundle",
            description="Test Description",
            overlays=overlays,
            version="2.0.0",
            variables={"key": "value"},
        )

        assert bundle.name == "Test Bundle"
        assert bundle.description == "Test Description"
        assert bundle.overlays == overlays
        assert bundle.version == "2.0.0"
        assert bundle.variables == {"key": "value"}

    def test_bundle_config_defaults(self):
        """Test BundleConfig with default values."""
        overlays = [OverlayConfig(path="test.yaml")]
        bundle = BundleConfig(
            name="Test Bundle", description="Test Description", overlays=overlays
        )

        assert bundle.version == "1.0.0"
        assert bundle.variables == {}


class TestOverlayConfig:
    """Test cases for OverlayConfig dataclass."""

    def test_overlay_config_creation(self):
        """Test OverlayConfig creation with all fields."""
        overlay = OverlayConfig(
            path="test.yaml",
            environment=["dev", "test"],
            description="Test overlay",
            variables={"key": "value"},
        )

        assert overlay.path == "test.yaml"
        assert overlay.environment == ["dev", "test"]
        assert overlay.description == "Test overlay"
        assert overlay.variables == {"key": "value"}

    def test_overlay_config_defaults(self):
        """Test OverlayConfig with default values."""
        overlay = OverlayConfig(path="test.yaml")

        assert overlay.path == "test.yaml"
        assert overlay.environment is None
        assert overlay.description is None
        assert overlay.variables == {}
