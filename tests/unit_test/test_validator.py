import pytest
import yaml
from oas_patch.validator import validate, load_schema, format_errors


def test_load_schema():
    schema = load_schema("overlay_schema_1.0.0.yml")
    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "actions" in schema["properties"]


def test_load_schema_not_found():
    with pytest.raises(FileNotFoundError):
        load_schema("nonexistent.yml")


def test_validate_valid_overlay():
    overlay_file = {
        "overlay": "1.0.0",
        "info": {
            "title": "Update petstore API",
            "version": "1.0.0"
            },
        "actions": [
            {
                "target": "$.info.title",
                "update": "Updated API"
            }
        ]
    }
    # Test different output formats
    for format in ["sh", "log", "yaml"]:
        result = validate(overlay_file, format)
        if format == "yaml":
            parsed = yaml.safe_load(result)
            assert parsed["status"] == "success"
        elif format == "log":
            assert "[ERROR]" not in result
        else:
            assert "errors" not in result


def test_validate_invalid_overlay():
    overlay_file = {
        "overly": "1.0.0",
        "inf": {
            "title": "Update petstore API",
            "version": "1.0.0"
            },
        "actions": [
            {
                "update": "Updated API"
            }
        ]
    }
    # Test different output formats
    for format in ["sh", "log", "yaml"]:
        result = validate(overlay_file, format)
        if format == "yaml":
            parsed = yaml.safe_load(result)
            assert parsed["status"] == "failed"
        elif format == "log":
            assert "[ERROR]" in result
        else:
            assert "!!!" in result


def test_format_errors():
    class MockError:
        def __init__(self, message, path=None, schema_path=None):
            self.message = message
            self.path = path
            self.schema_path = schema_path

    errors = [
        MockError("Error 1", ["path", "to", "error"]),
        MockError("Error 2", ["another", "path"])
    ]

    # Test YAML format
    yaml_output = format_errors(errors, "yaml")
    assert isinstance(yaml_output, str)
    parsed = yaml.safe_load(yaml_output)
    assert parsed["status"] == "failed"
    assert len(parsed["errors"]) == 2

    # Test log format
    log_output = format_errors(errors, "log")
    assert "[ERROR]" in log_output
    assert "Error 1" in log_output
    assert "Error 2" in log_output

    # Test shell format
    sh_output = format_errors(errors, "sh")
    assert "!!!" in sh_output
    assert "Error 1" in sh_output
    assert "Error 2" in sh_output
