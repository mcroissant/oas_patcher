"""Module for template processing and variable substitution."""

import copy
import os
import re
from typing import Dict, Any, Optional
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError
import yaml
import json


class TemplateEngine:
    """Handles Jinja2 templating and variable substitution in overlay files."""

    def __init__(self, enable_env_vars: bool = True):
        """Initialize the template engine with Jinja2 environment.

        Args:
            enable_env_vars: If True, environment variables will be available in templates
        """
        self.enable_env_vars = enable_env_vars
        self.jinja_env = Environment(
            loader=BaseLoader(), autoescape=False, trim_blocks=True, lstrip_blocks=True
        )

        # Add custom filters
        self.jinja_env.filters["to_yaml"] = self._to_yaml_filter
        self.jinja_env.filters["to_json"] = self._to_json_filter

        # Add custom functions
        self.jinja_env.globals["env"] = self._env_function

    def _to_yaml_filter(self, obj: Any) -> str:
        """Jinja2 filter to convert object to YAML string."""
        return yaml.dump(obj, default_flow_style=False)

    def _to_json_filter(self, obj: Any) -> str:
        """Jinja2 filter to convert object to JSON string."""
        return json.dumps(obj, indent=2)

    def process_template_content(self, content: str, variables: Dict[str, Any]) -> str:
        """Process template content with variable substitution."""
        try:
            # Resolve environment variables in the variables
            resolved_variables = self._resolve_env_vars_in_variables(variables)

            template = self.jinja_env.from_string(content)
            return template.render(**resolved_variables)
        except TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error: {str(e)}")
        except UndefinedError as e:
            raise ValueError(f"Undefined variable in template: {str(e)}")
        except Exception as e:
            raise ValueError(f"Template processing error: {str(e)}")

    def process_overlay_data(
        self, overlay_data: Dict[str, Any], variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process overlay data structure with variable substitution."""
        # Create a deep copy to avoid modifying the original
        processed_data = copy.deepcopy(overlay_data)

        # Resolve environment variables in the variables
        resolved_variables = self._resolve_env_vars_in_variables(variables)

        # Process the data recursively
        return self._process_data_recursive(processed_data, resolved_variables)

    def _process_data_recursive(self, data: Any, variables: Dict[str, Any]) -> Any:
        """Recursively process data structure for template substitution."""
        if isinstance(data, str):
            # Check if string contains Jinja2 template syntax
            if "{{" in data or "{%" in data:
                return self.process_template_content(data, variables)
            return data
        elif isinstance(data, dict):
            processed_dict = {}
            for key, value in data.items():
                # Process both keys and values
                processed_key = self._process_data_recursive(key, variables)
                processed_value = self._process_data_recursive(value, variables)
                processed_dict[processed_key] = processed_value
            return processed_dict
        elif isinstance(data, list):
            return [self._process_data_recursive(item, variables) for item in data]
        else:
            # For other data types (int, float, bool, None), return as-is
            return data

    def validate_template(
        self, content: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate template syntax and check for undefined variables."""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        if variables is None:
            variables = {}

        try:
            # Check template syntax
            template = self.jinja_env.from_string(content)

            # Try to render with provided variables
            try:
                template.render(**variables)
            except UndefinedError as e:
                validation_result["warnings"].append(f"Undefined variable: {str(e)}")

        except TemplateSyntaxError as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Template syntax error: {str(e)}")
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Template validation error: {str(e)}")

        return validation_result

    def extract_template_variables(self, content: str) -> set:
        """Extract variable names used in a template."""
        try:
            import jinja2.meta

            ast = self.jinja_env.parse(content)
            variables = jinja2.meta.find_undeclared_variables(ast)
            return variables
        except Exception:
            # If parsing fails, return empty set
            return set()

    def get_template_info(self, content: str) -> Dict[str, Any]:
        """Get information about template variables and validation."""
        variables = self.extract_template_variables(content)
        validation = self.validate_template(content)

        return {
            "variables": list(variables),
            "variable_count": len(variables),
            "validation": validation,
        }

    def _env_function(self, var_name: str, default: str = None) -> str:
        """Jinja2 function to get environment variables.

        Usage in templates: {{ env('VAR_NAME') }} or {{ env('VAR_NAME', 'default_value') }}
        """
        return os.environ.get(var_name, default)

    def _resolve_env_vars_in_value(self, value: str) -> str:
        """Resolve ${VAR_NAME} syntax in string values."""
        if not isinstance(value, str):
            return value

        # Pattern to match ${VAR_NAME} or ${VAR_NAME:default_value}
        pattern = r"\$\{([^}:]+)(?::([^}]*))?\}"

        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.environ.get(var_name, default_value)

        return re.sub(pattern, replace_env_var, value)

    def _resolve_env_vars_in_variables(
        self, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve environment variables in the variables dictionary."""
        if not self.enable_env_vars:
            return variables

        resolved_vars = copy.deepcopy(variables)

        # Add environment variables as a special 'ENV' namespace (uppercase to avoid conflicts)
        resolved_vars["ENV"] = dict(os.environ)

        # Resolve ${VAR} syntax in string values
        for key, value in resolved_vars.items():
            if isinstance(value, str):
                resolved_vars[key] = self._resolve_env_vars_in_value(value)
            elif isinstance(value, dict):
                resolved_vars[key] = self._resolve_env_vars_recursive(value)
            elif isinstance(value, list):
                resolved_vars[key] = [
                    (
                        self._resolve_env_vars_in_value(item)
                        if isinstance(item, str)
                        else (
                            self._resolve_env_vars_recursive(item)
                            if isinstance(item, dict)
                            else item
                        )
                    )
                    for item in value
                ]

        return resolved_vars

    def _resolve_env_vars_recursive(self, data: Any) -> Any:
        """Recursively resolve environment variables in nested data structures."""
        if isinstance(data, str):
            return self._resolve_env_vars_in_value(data)
        elif isinstance(data, dict):
            return {
                key: self._resolve_env_vars_recursive(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._resolve_env_vars_recursive(item) for item in data]
        else:
            return data
