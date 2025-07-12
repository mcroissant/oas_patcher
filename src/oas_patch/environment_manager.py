"""Module for managing environments and variables."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from oas_patch.file_utils import load_file


@dataclass
class EnvironmentConfig:
    """Configuration for an environment."""

    name: str
    description: str
    variables: Dict[str, Any] = field(default_factory=dict)


class EnvironmentManager:
    """Manages environment configurations and variables."""

    def __init__(self, config_dir: str = "overlays"):
        """Initialize environment manager with configuration directory."""
        self.config_dir = Path(config_dir)
        self._environments_cache = {}

    def discover_environments(self) -> List[str]:
        """Discover all available environment configuration files."""
        if not self.config_dir.exists():
            return []

        env_files = []

        # Look for environment files in environments subdirectory
        env_dir = self.config_dir / "environments"
        if env_dir.exists():
            for file_path in env_dir.glob("*.yaml"):
                env_files.append(file_path.stem)
            for file_path in env_dir.glob("*.yml"):
                env_files.append(file_path.stem)

        # Look for environment files in root config directory
        for file_path in self.config_dir.glob("env-*.yaml"):
            env_name = file_path.stem.replace("env-", "")
            env_files.append(env_name)

        for file_path in self.config_dir.glob("env-*.yml"):
            env_name = file_path.stem.replace("env-", "")
            env_files.append(env_name)

        return sorted(list(set(env_files)))

    def load_environment(self, env_name: str) -> EnvironmentConfig:
        """Load a specific environment configuration."""
        if env_name in self._environments_cache:
            return self._environments_cache[env_name]

        env_path = self._find_environment_config(env_name)
        if not env_path:
            raise FileNotFoundError(
                f"Environment '{env_name}' not found in {self.config_dir}"
            )

        try:
            config_data = load_file(str(env_path))
            env_config = self._parse_environment_config(config_data, env_name)
            self._environments_cache[env_name] = env_config
            return env_config
        except Exception as e:
            raise ValueError(f"Failed to load environment '{env_name}': {str(e)}")

    def _find_environment_config(self, env_name: str) -> Optional[Path]:
        """Find the configuration file for an environment."""
        possible_paths = [
            self.config_dir / "environments" / f"{env_name}.yaml",
            self.config_dir / "environments" / f"{env_name}.yml",
            self.config_dir / f"env-{env_name}.yaml",
            self.config_dir / f"env-{env_name}.yml",
        ]

        for path in possible_paths:
            if path.exists():
                return path
        return None

    def _parse_environment_config(
        self, config_data: Dict[str, Any], env_name: str
    ) -> EnvironmentConfig:
        """Parse environment configuration data into EnvironmentConfig object."""
        return EnvironmentConfig(
            name=config_data.get("name", env_name),
            description=config_data.get("description", ""),
            variables=config_data.get("variables", {}),
        )

    def get_variables(
        self, env_name: Optional[str], cli_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get merged variables with proper precedence (CLI > Environment > System)."""
        variables = {}

        # Start with system environment variables
        variables.update(dict(os.environ))

        # Add environment-specific variables if environment is specified
        if env_name:
            try:
                env_config = self.load_environment(env_name)
                variables.update(env_config.variables)
            except (FileNotFoundError, ValueError):
                # Environment file not found, continue with other sources
                pass

        # CLI variables have highest precedence
        if cli_variables:
            variables.update(cli_variables)

        return variables

    def validate_environment(self, env_name: str) -> Dict[str, Any]:
        """Validate an environment configuration."""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        try:
            env_config = self.load_environment(env_name)

            # Basic validation
            if not env_config.variables:
                validation_result["warnings"].append(
                    "Environment contains no variables"
                )

            # Validate variable types
            for key, value in env_config.variables.items():
                if not isinstance(key, str):
                    validation_result["errors"].append(
                        f"Variable key must be string: {key}"
                    )
                    validation_result["valid"] = False

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(
                f"Environment validation failed: {str(e)}"
            )

        return validation_result

    def get_environment_info(self, env_name: str) -> Dict[str, Any]:
        """Get detailed information about an environment."""
        try:
            env_config = self.load_environment(env_name)
            validation_result = self.validate_environment(env_name)

            return {
                "name": env_config.name,
                "description": env_config.description,
                "variables": env_config.variables,
                "variable_count": len(env_config.variables),
                "validation": validation_result,
            }
        except Exception as e:
            return {
                "name": env_name,
                "description": "Failed to load environment",
                "error": str(e),
                "validation": {"valid": False, "errors": [str(e)], "warnings": []},
            }

    def list_environments_info(self) -> List[Dict[str, Any]]:
        """Get information about all discovered environments."""
        env_names = self.discover_environments()
        return [self.get_environment_info(env_name) for env_name in env_names]
