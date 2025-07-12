"""Unit tests for the TemplateEngine class."""

import pytest
from oas_patch.template_engine import TemplateEngine


class TestTemplateEngine:
    """Test cases for TemplateEngine class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.template_engine = TemplateEngine()

    def test_init(self):
        """Test TemplateEngine initialization."""
        engine = TemplateEngine()
        assert engine.jinja_env is not None
        assert "to_yaml" in engine.jinja_env.filters
        assert "to_json" in engine.jinja_env.filters

    def test_to_yaml_filter(self):
        """Test the to_yaml custom filter."""
        test_data = {"key": "value", "nested": {"inner": "data"}}
        result = self.template_engine._to_yaml_filter(test_data)

        assert isinstance(result, str)
        assert "key: value" in result
        assert "nested:" in result
        assert "inner: data" in result

    def test_to_json_filter(self):
        """Test the to_json custom filter."""
        test_data = {"key": "value", "nested": {"inner": "data"}}
        result = self.template_engine._to_json_filter(test_data)

        assert isinstance(result, str)
        assert '"key": "value"' in result
        assert '"nested"' in result
        assert '"inner": "data"' in result

    def test_process_template_content_simple(self):
        """Test processing simple template content."""
        content = "Hello {{ name }}!"
        variables = {"name": "World"}

        result = self.template_engine.process_template_content(content, variables)
        assert result == "Hello World!"

    def test_process_template_content_multiple_variables(self):
        """Test processing template with multiple variables."""
        content = "{{ greeting }} {{ name }}, version {{ version }}"
        variables = {"greeting": "Hello", "name": "OpenAPI", "version": "3.0.0"}

        result = self.template_engine.process_template_content(content, variables)
        assert result == "Hello OpenAPI, version 3.0.0"

    def test_process_template_content_with_filters(self):
        """Test processing template with custom filters."""
        content = "Data: {{ data | to_json }}"
        variables = {"data": {"key": "value"}}

        result = self.template_engine.process_template_content(content, variables)
        assert '"key": "value"' in result

    def test_process_template_content_with_control_structures(self):
        """Test processing template with Jinja2 control structures."""
        content = """
        {%- for item in items -%}
        - {{ item }}
        {% endfor -%}
        """
        variables = {"items": ["first", "second", "third"]}

        result = self.template_engine.process_template_content(content, variables)
        assert "- first" in result
        assert "- second" in result
        assert "- third" in result

    def test_process_template_content_syntax_error(self):
        """Test processing template with syntax error."""
        content = "Hello {{ name"  # Missing closing braces
        variables = {"name": "World"}

        with pytest.raises(ValueError, match="Template syntax error"):
            self.template_engine.process_template_content(content, variables)

    def test_process_template_content_undefined_variable(self):
        """Test processing template with undefined variable."""
        content = "Hello {{ undefined_var }}!"
        variables = {}

        # Jinja2 by default renders undefined variables as empty
        result = self.template_engine.process_template_content(content, variables)
        assert result == "Hello !"

    def test_process_template_content_no_template_syntax(self):
        """Test processing content without template syntax."""
        content = "This is plain text"
        variables = {"name": "World"}

        result = self.template_engine.process_template_content(content, variables)
        assert result == "This is plain text"

    def test_process_overlay_data_string_with_template(self):
        """Test processing overlay data with templated strings."""
        overlay_data = {
            "info": {"title": "{{ api_name }} API", "version": "{{ api_version }}"},
            "paths": {"/{{ endpoint }}": {"get": {"summary": "Get {{ resource }}"}}},
        }
        variables = {
            "api_name": "Pet Store",
            "api_version": "1.0.0",
            "endpoint": "pets",
            "resource": "pets",
        }

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        assert result["info"]["title"] == "Pet Store API"
        assert result["info"]["version"] == "1.0.0"
        assert "/pets" in result["paths"]
        assert result["paths"]["/pets"]["get"]["summary"] == "Get pets"

    def test_process_overlay_data_no_template_syntax(self):
        """Test processing overlay data without template syntax."""
        overlay_data = {
            "info": {"title": "Static API", "version": "1.0.0"},
            "static_number": 42,
            "static_boolean": True,
            "static_null": None,
        }
        variables = {"unused": "variable"}

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        # Should return unchanged data
        assert result == overlay_data
        # Verify original data wasn't modified
        assert overlay_data["info"]["title"] == "Static API"

    def test_process_overlay_data_list_processing(self):
        """Test processing overlay data with lists containing templates."""
        overlay_data = {
            "servers": [
                {"url": "https://{{ env }}.example.com"},
                {"url": "https://{{ env }}.api.com", "description": "{{ env }} server"},
            ],
            "tags": ["{{ category }}", "api"],
        }
        variables = {"env": "production", "category": "pets"}

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        assert result["servers"][0]["url"] == "https://production.example.com"
        assert result["servers"][1]["url"] == "https://production.api.com"
        assert result["servers"][1]["description"] == "production server"
        assert result["tags"] == ["pets", "api"]

    def test_process_overlay_data_nested_structures(self):
        """Test processing deeply nested overlay data structures."""
        overlay_data = {
            "components": {
                "schemas": {
                    "{{ model_name }}": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string", "example": "{{ example_name }}"},
                        },
                    }
                }
            }
        }
        variables = {"model_name": "Pet", "example_name": "Fluffy"}

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        assert "Pet" in result["components"]["schemas"]
        assert (
            result["components"]["schemas"]["Pet"]["properties"]["name"]["example"]
            == "Fluffy"
        )

    def test_process_overlay_data_deep_copy(self):
        """Test that processing overlay data doesn't modify the original."""
        overlay_data = {"info": {"title": "{{ api_name }} API"}}
        variables = {"api_name": "Test"}

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        # Original should be unchanged
        assert overlay_data["info"]["title"] == "{{ api_name }} API"
        # Result should be processed
        assert result["info"]["title"] == "Test API"

    def test_process_data_recursive_various_types(self):
        """Test recursive processing with various data types."""
        data = {
            "string": "{{ value }}",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, "{{ value }}", None],
            "nested": {"key": "{{ value }}"},
        }
        variables = {"value": "processed"}

        result = self.template_engine._process_data_recursive(data, variables)

        assert result["string"] == "processed"
        assert result["integer"] == 42
        assert result["float"] == 3.14
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["list"] == [1, "processed", None]
        assert result["nested"]["key"] == "processed"

    def test_process_data_recursive_templated_keys(self):
        """Test recursive processing with templated dictionary keys."""
        data = {"{{ key_name }}": "value", "static_key": "{{ value }}"}
        variables = {"key_name": "dynamic_key", "value": "processed_value"}

        result = self.template_engine._process_data_recursive(data, variables)

        assert "dynamic_key" in result
        assert result["dynamic_key"] == "value"
        assert result["static_key"] == "processed_value"

    def test_validate_template_valid_syntax(self):
        """Test validating template with valid syntax."""
        content = "Hello {{ name }}!"
        variables = {"name": "World"}

        result = self.template_engine.validate_template(content, variables)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_template_syntax_error(self):
        """Test validating template with syntax error."""
        content = "Hello {{ name"  # Missing closing braces

        result = self.template_engine.validate_template(content)

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "Template syntax error" in result["errors"][0]

    def test_validate_template_undefined_variable(self):
        """Test validating template with undefined variable."""
        content = "Hello {{ undefined_var }}!"
        variables = {"other_var": "value"}

        result = self.template_engine.validate_template(content, variables)

        # Template syntax is valid, and Jinja2 doesn't detect undefined variables during validation
        assert result["valid"] is True
        # No warnings are generated by the current implementation
        assert result["warnings"] == []

    def test_validate_template_no_variables(self):
        """Test validating template without providing variables."""
        content = "Hello {{ name }}!"

        result = self.template_engine.validate_template(content)

        # Template syntax is valid
        assert result["valid"] is True
        # No warnings are generated by the current implementation
        assert result["warnings"] == []

    def test_validate_template_complex_content(self):
        """Test validating complex template content."""
        content = """
        {% for item in items %}
        - {{ item.name }}: {{ item.value }}
        {% endfor %}
        """
        variables = {
            "items": [{"name": "first", "value": "1"}, {"name": "second", "value": "2"}]
        }

        result = self.template_engine.validate_template(content, variables)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_extract_template_variables_simple(self):
        """Test extracting variables from simple template."""
        content = "Hello {{ name }}!"

        variables = self.template_engine.extract_template_variables(content)

        assert "name" in variables

    def test_extract_template_variables_multiple(self):
        """Test extracting multiple variables from template."""
        content = "{{ greeting }} {{ name }}, version {{ version }}"

        variables = self.template_engine.extract_template_variables(content)

        assert "greeting" in variables
        assert "name" in variables
        assert "version" in variables

    def test_extract_template_variables_nested_access(self):
        """Test extracting variables with nested access."""
        content = "{{ user.name }} from {{ user.department.name }}"

        variables = self.template_engine.extract_template_variables(content)

        assert "user" in variables

    def test_extract_template_variables_with_filters(self):
        """Test extracting variables when using filters."""
        content = "{{ data | to_json }} and {{ other_data | to_yaml }}"

        variables = self.template_engine.extract_template_variables(content)

        assert "data" in variables
        assert "other_data" in variables

    def test_extract_template_variables_invalid_syntax(self):
        """Test extracting variables from template with invalid syntax."""
        content = "Hello {{ name"  # Invalid syntax

        variables = self.template_engine.extract_template_variables(content)

        # Should return empty set when parsing fails
        assert variables == set()

    def test_extract_template_variables_no_variables(self):
        """Test extracting variables from template without variables."""
        content = "This is static content"

        variables = self.template_engine.extract_template_variables(content)

        assert variables == set()

    def test_get_template_info_complete(self):
        """Test getting complete template information."""
        content = "Hello {{ name }}, version {{ version }}!"

        info = self.template_engine.get_template_info(content)

        assert "variables" in info
        assert "variable_count" in info
        assert "validation" in info

        assert len(info["variables"]) == 2
        assert "name" in info["variables"]
        assert "version" in info["variables"]
        assert info["variable_count"] == 2

        # Should include validation info
        assert info["validation"]["valid"] is True

    def test_get_template_info_invalid_template(self):
        """Test getting template information for invalid template."""
        content = "Hello {{ name"  # Invalid syntax

        info = self.template_engine.get_template_info(content)

        assert info["variables"] == []
        assert info["variable_count"] == 0
        assert info["validation"]["valid"] is False

    def test_jinja_env_configuration(self):
        """Test that Jinja2 environment is configured correctly."""
        engine = TemplateEngine()

        # Test trim_blocks and lstrip_blocks settings
        content = """
        {% if true %}
            trimmed content
        {% endif %}
        """
        variables = {}

        result = engine.process_template_content(content, variables)

        # Content should be trimmed due to trim_blocks and lstrip_blocks
        assert result.strip() == "trimmed content"

    def test_autoescape_disabled(self):
        """Test that autoescaping is disabled."""
        content = "HTML: {{ html_content }}"
        variables = {"html_content": '<script>alert("test")</script>'}

        result = self.template_engine.process_template_content(content, variables)

        # HTML should not be escaped
        assert "<script>" in result
        assert "&lt;script&gt;" not in result

    def test_custom_filters_integration(self):
        """Test integration of custom filters in template processing."""
        overlay_data = {
            "config": "{{ settings | to_yaml }}",
            "metadata": "{{ info | to_json }}",
        }
        variables = {
            "settings": {"debug": True, "timeout": 30},
            "info": {"name": "test", "version": "1.0"},
        }

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        # Check YAML output
        assert "debug: true" in result["config"]
        assert "timeout: 30" in result["config"]

        # Check JSON output
        assert '"name": "test"' in result["metadata"]
        assert '"version": "1.0"' in result["metadata"]

    def test_template_processing_edge_cases(self):
        """Test template processing with edge cases."""
        # Empty content
        assert self.template_engine.process_template_content("", {}) == ""

        # Content with only whitespace
        result = self.template_engine.process_template_content("   ", {})
        assert result == "   "

        # Content with escaped template syntax
        content = "Use \\{\\{ variable \\}\\} for templating"
        result = self.template_engine.process_template_content(content, {})
        # Note: Jinja2 doesn't process backslash escapes in this context
        assert "\\{\\{" in result

    def test_process_overlay_data_empty_structures(self):
        """Test processing overlay data with empty structures."""
        overlay_data = {
            "empty_dict": {},
            "empty_list": [],
            "nested_empty": {"empty_dict": {}, "empty_list": []},
        }
        variables = {"key": "value"}

        result = self.template_engine.process_overlay_data(overlay_data, variables)

        assert result["empty_dict"] == {}
        assert result["empty_list"] == []
        assert result["nested_empty"]["empty_dict"] == {}
        assert result["nested_empty"]["empty_list"] == []

    def test_error_handling_in_recursive_processing(self):
        """Test error handling during recursive data processing."""
        # Test with template that will cause an error
        overlay_data = {
            "valid": "{{ valid_var }}",
            "invalid": "{{ invalid_var }}",  # This will render as empty since undefined variables don't raise errors
        }
        variables = {"valid_var": "valid_value"}

        # Process should succeed, but undefined variables will be empty
        result = self.template_engine.process_overlay_data(overlay_data, variables)
        assert result["valid"] == "valid_value"
        assert result["invalid"] == ""  # Undefined variable renders as empty
