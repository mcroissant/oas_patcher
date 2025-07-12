"""Module for managing overlay bundles and configurations."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from oas_patch.file_utils import load_file


@dataclass
class OverlayConfig:
    """Configuration for a single overlay within a bundle."""

    path: str
    environment: Optional[List[str]] = None
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class BundleConfig:
    """Configuration for an overlay bundle."""

    name: str
    description: str
    overlays: List[OverlayConfig]
    version: str = "1.0.0"
    variables: Optional[Dict[str, Any]] = field(default_factory=dict)


class BundleManager:
    """Manages overlay bundles and their configurations."""

    def __init__(self, config_dir: str = "overlays"):
        """Initialize bundle manager with configuration directory."""
        self.config_dir = Path(config_dir)
        self._bundles_cache = {}

    def discover_bundles(self) -> List[str]:
        """Discover all available bundle configuration files."""
        if not self.config_dir.exists():
            return []

        bundle_files = []
        for file_path in self.config_dir.rglob("bundle.yaml"):
            bundle_files.append(str(file_path.parent.name))

        for file_path in self.config_dir.rglob("bundle.yml"):
            bundle_files.append(str(file_path.parent.name))

        return sorted(list(set(bundle_files)))

    def load_bundle(self, bundle_name: str) -> BundleConfig:
        """Load a specific bundle configuration."""
        if bundle_name in self._bundles_cache:
            return self._bundles_cache[bundle_name]

        bundle_path = self._find_bundle_config(bundle_name)
        if not bundle_path:
            raise FileNotFoundError(
                f"Bundle '{bundle_name}' not found in {self.config_dir}"
            )

        try:
            config_data = load_file(str(bundle_path))
            bundle_config = self._parse_bundle_config(config_data, bundle_name)
            self._bundles_cache[bundle_name] = bundle_config
            return bundle_config
        except Exception as e:
            raise ValueError(f"Failed to load bundle '{bundle_name}': {str(e)}")

    def _find_bundle_config(self, bundle_name: str) -> Optional[Path]:
        """Find the configuration file for a bundle."""
        possible_paths = [
            self.config_dir / bundle_name / "bundle.yaml",
            self.config_dir / bundle_name / "bundle.yml",
            self.config_dir / f"{bundle_name}.yaml",
            self.config_dir / f"{bundle_name}.yml",
        ]

        for path in possible_paths:
            if path.exists():
                return path
        return None

    def _parse_bundle_config(
        self, config_data: Dict[str, Any], bundle_name: str
    ) -> BundleConfig:
        """Parse bundle configuration data into BundleConfig object."""
        overlays = []
        for overlay_data in config_data.get("overlays", []):
            overlay_config = OverlayConfig(
                path=overlay_data["path"],
                environment=overlay_data.get("environment"),
                description=overlay_data.get("description"),
                variables=overlay_data.get("variables", {}),
            )
            overlays.append(overlay_config)

        return BundleConfig(
            name=config_data.get("name", bundle_name),
            description=config_data.get("description", ""),
            overlays=overlays,
            version=config_data.get("version", "1.0.0"),
            variables=config_data.get("variables", {}),
        )

    def validate_bundle(self, bundle_name: str) -> Dict[str, Any]:
        """Validate a bundle configuration and its overlay files."""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        try:
            bundle_config = self.load_bundle(bundle_name)

            # Validate bundle structure
            if not bundle_config.overlays:
                validation_result["warnings"].append("Bundle contains no overlays")

            # Validate overlay files exist
            for overlay in bundle_config.overlays:
                overlay_path = self._resolve_overlay_path(bundle_name, overlay.path)
                if not overlay_path.exists():
                    validation_result["errors"].append(
                        f"Overlay file not found: {overlay.path}"
                    )
                    validation_result["valid"] = False
                else:
                    # Validate overlay file format
                    try:
                        load_file(str(overlay_path))
                    except Exception as e:
                        validation_result["errors"].append(
                            f"Invalid overlay file format '{overlay.path}': {str(e)}"
                        )
                        validation_result["valid"] = False

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Bundle validation failed: {str(e)}")

        return validation_result

    def _resolve_overlay_path(self, bundle_name: str, overlay_path: str) -> Path:
        """Resolve the full path to an overlay file."""
        if os.path.isabs(overlay_path):
            return Path(overlay_path)

        # Try relative to bundle directory first
        bundle_dir = self.config_dir / bundle_name
        if bundle_dir.exists():
            full_path = bundle_dir / overlay_path
            if full_path.exists():
                return full_path

        # Fall back to relative to config directory
        return self.config_dir / overlay_path

    def get_overlays_for_environment(
        self, bundle_name: str, environment: str
    ) -> List[OverlayConfig]:
        """Get overlays filtered by environment."""
        bundle_config = self.load_bundle(bundle_name)
        filtered_overlays = []

        for overlay in bundle_config.overlays:
            if overlay.environment is None or environment in overlay.environment:
                filtered_overlays.append(overlay)

        return filtered_overlays

    def get_bundle_info(self, bundle_name: str) -> Dict[str, Any]:
        """Get detailed information about a bundle."""
        bundle_config = self.load_bundle(bundle_name)
        validation_result = self.validate_bundle(bundle_name)

        return {
            "name": bundle_config.name,
            "description": bundle_config.description,
            "version": bundle_config.version,
            "overlays": [
                {
                    "path": overlay.path,
                    "environment": overlay.environment,
                    "description": overlay.description,
                    "variables": overlay.variables,
                }
                for overlay in bundle_config.overlays
            ],
            "variables": bundle_config.variables,
            "validation": validation_result,
        }
