import pytest
import os
import sys
from pathlib import Path

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from oas_patch.template_engine import TemplateEngine


class TestTemplateEngineEnvironmentVariables:
    """Test environment variable support in the template engine."""

    def setup_method(self):
        """Set up test environment variables."""
        # Set some test environment variables
        os.environ['TEST_API_URL'] = 'https://api.test.com'
        os.environ['TEST_API_VERSION'] = '2.0.0'
        os.environ['TEST_OWNER'] = 'Test Corp'
        os.environ['CI_ENVIRONMENT'] = 'production'
        os.environ['CI_BUILD_NUMBER'] = '123'

    def teardown_method(self):
        """Clean up test environment variables."""
        test_vars = ['TEST_API_URL', 'TEST_API_VERSION', 'TEST_OWNER', 'CI_ENVIRONMENT', 'CI_BUILD_NUMBER']
        for var in test_vars:
            if var in os.environ:
                del os.environ[var]

    def test_env_function_in_templates(self):
        """Test using the env() function in Jinja2 templates."""
        template_engine = TemplateEngine()
        
        content = "API URL: {{ env('TEST_API_URL') }}"
        variables = {}
        
        result = template_engine.process_template_content(content, variables)
        assert result == "API URL: https://api.test.com"

    def test_env_function_with_default(self):
        """Test using env() function with default values."""
        template_engine = TemplateEngine()
        
        content = "Database: {{ env('MISSING_VAR', 'localhost') }}"
        variables = {}
        
        result = template_engine.process_template_content(content, variables)
        assert result == "Database: localhost"

    def test_env_namespace_access(self):
        """Test accessing environment variables via ENV namespace."""
        template_engine = TemplateEngine()
        
        content = "Owner: {{ ENV.TEST_OWNER }}"
        variables = {}
        
        result = template_engine.process_template_content(content, variables)
        assert result == "Owner: Test Corp"

    def test_dollar_brace_syntax(self):
        """Test ${VAR_NAME} syntax in variable values."""
        template_engine = TemplateEngine()
        
        overlay_data = {
            "actions": [
                {
                    "target": "$.info",
                    "update": {
                        "title": "{{ api_title }}",
                        "version": "{{ api_version }}"
                    }
                }
            ]
        }
        
        variables = {
            "api_title": "My API",
            "api_version": "${TEST_API_VERSION}"  # Will resolve to 2.0.0
        }
        
        result = template_engine.process_overlay_data(overlay_data, variables)
        assert result["actions"][0]["update"]["version"] == "2.0.0"

    def test_dollar_brace_with_default(self):
        """Test ${VAR_NAME:default} syntax."""
        template_engine = TemplateEngine()
        
        overlay_data = {
            "info": {
                "title": "API"
            }
        }
        
        variables = {
            "db_host": "${MISSING_DB_HOST:localhost}",
            "api_url": "${TEST_API_URL:https://fallback.com}"
        }
        
        result = template_engine.process_overlay_data(overlay_data, variables)
        # The variables should be resolved in the template engine's variable namespace
        # We can verify this by checking if they're available in templates
        
        content = "DB: {{ db_host }}, API: {{ api_url }}"
        processed = template_engine.process_template_content(content, variables)
        assert "DB: localhost" in processed
        assert "API: https://api.test.com" in processed

    def test_complex_ci_pipeline_scenario(self):
        """Test a complex CI/CD pipeline scenario with environment variables."""
        template_engine = TemplateEngine()
        
        overlay_data = {
            "overlay": "1.0.0",
            "info": {
                "title": "CI/CD Overlay",
                "version": "1.0.0"
            },
            "actions": [
                {
                    "target": "$.info",
                    "update": {
                        "title": "{{ app_name }} - {{ ENV.CI_ENVIRONMENT }}",
                        "version": "{{ app_version }}",
                        "description": "Built from CI build {{ env('CI_BUILD_NUMBER', 'unknown') }}"
                    }
                },
                {
                    "target": "$",
                    "update": {
                        "servers": [
                            {
                                "url": "{{ base_url }}",
                                "description": "{{ ENV.CI_ENVIRONMENT }} server"
                            }
                        ]
                    }
                }
            ]
        }
        
        variables = {
            "app_name": "MyApp",
            "app_version": "${TEST_API_VERSION}",  # Resolved from env
            "base_url": "${TEST_API_URL}"          # Resolved from env
        }
        
        result = template_engine.process_overlay_data(overlay_data, variables)
        
        # Check that environment variables were properly resolved
        info_update = result["actions"][0]["update"]
        assert info_update["title"] == "MyApp - production"
        assert info_update["version"] == "2.0.0"
        assert info_update["description"] == "Built from CI build 123"
        
        servers_update = result["actions"][1]["update"]
        assert servers_update["servers"][0]["url"] == "https://api.test.com"
        assert servers_update["servers"][0]["description"] == "production server"

    def test_disabled_env_vars(self):
        """Test that environment variable resolution can be disabled."""
        template_engine = TemplateEngine(enable_env_vars=False)
        
        variables = {
            "api_url": "${TEST_API_URL}"
        }
        
        # When env vars are disabled, ${} syntax should not be resolved
        content = "URL: {{ api_url }}"
        result = template_engine.process_template_content(content, variables)
        assert result == "URL: ${TEST_API_URL}"

    def test_nested_data_structure_env_resolution(self):
        """Test environment variable resolution in nested data structures."""
        template_engine = TemplateEngine()
        
        overlay_data = {
            "actions": [
                {
                    "target": "$.components",
                    "update": {
                        "securitySchemes": {
                            "ApiKey": {
                                "type": "apiKey",
                                "name": "{{ header_name }}",
                                "description": "API key for {{ env_name }}"
                            }
                        }
                    }
                }
            ]
        }
        
        variables = {
            "header_name": "X-API-Key",
            "env_name": "${CI_ENVIRONMENT}",
            "nested": {
                "config": {
                    "url": "${TEST_API_URL}",
                    "version": "${TEST_API_VERSION}"
                }
            }
        }
        
        result = template_engine.process_overlay_data(overlay_data, variables)
        
        # Verify that the nested environment variable was resolved
        security_scheme = result["actions"][0]["update"]["securitySchemes"]["ApiKey"]
        assert security_scheme["description"] == "API key for production"
        
        # Verify that nested variables are also resolved
        content = "Config: {{ nested.config.url }} v{{ nested.config.version }}"
        processed = template_engine.process_template_content(content, variables)
        assert processed == "Config: https://api.test.com v2.0.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
