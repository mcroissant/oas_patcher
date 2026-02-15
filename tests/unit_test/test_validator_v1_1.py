"""Tests for Overlay 1.1.0 schema validation."""
from oas_patch.validator import validate


def test_validate_v1_1_basic_overlay():
    """Test validation of a basic 1.1.0 overlay."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Test Overlay",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.info",
                "update": {"x-custom": "value"}
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_with_copy_action():
    """Test validation of overlay with copy action."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Copy Action Overlay",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.components.schemas['Bar']",
                "copy": "$.components.schemas['Foo']"
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_with_info_description():
    """Test validation of overlay with description in info."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Overlay with Description",
            "version": "1.0.0",
            "description": "This is a detailed description of the overlay"
        },
        "actions": [
            {
                "target": "$.info",
                "update": {"x-test": "value"}
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_invalid_version():
    """Test validation fails for invalid 1.1.x version."""
    overlay = {
        "overlay": "1.1",  # Invalid: missing patch version
        "info": {
            "title": "Test",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.info",
                "update": {}
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[ERROR]" in result


def test_validate_v1_1_with_all_action_types():
    """Test validation with update, copy, and remove actions."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "All Actions",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.info.title",
                "update": "New Title"
            },
            {
                "target": "$.components.schemas['Bar']",
                "copy": "$.components.schemas['Foo']"
            },
            {
                "target": "$.paths['/old']",
                "remove": True
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_with_action_descriptions():
    """Test validation with action descriptions."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Described Actions",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.info",
                "description": "Update API info",
                "update": {"x-api-version": "2.0"}
            },
            {
                "target": "$.components.schemas['Bar']",
                "description": "Copy Foo schema to Bar",
                "copy": "$.components.schemas['Foo']"
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_0_still_works():
    """Test that 1.0.0 overlays still validate correctly."""
    overlay = {
        "overlay": "1.0.0",
        "info": {
            "title": "Legacy Overlay",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.info",
                "update": {"x-custom": "value"}
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_0_with_copy_fails():
    """Test that 1.0.0 overlays with copy action fail validation."""
    overlay = {
        "overlay": "1.0.0",
        "info": {
            "title": "Invalid Legacy",
            "version": "1.0.0"
        },
        "actions": [
            {
                "target": "$.components.schemas['Bar']",
                "copy": "$.components.schemas['Foo']"  # copy not allowed in 1.0
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[ERROR]" in result
    # The error should mention unevaluated properties since copy is not in 1.0 schema
    assert "Validation failed" in result or "unevaluatedProperties" in result.lower()


def test_validate_v1_1_patch_versions():
    """Test that different patch versions of 1.1.x are accepted."""
    for patch in [0, 1, 5, 10, 99]:
        overlay = {
            "overlay": f"1.1.{patch}",
            "info": {
                "title": "Test",
                "version": "1.0.0"
            },
            "actions": [
                {
                    "target": "$.info",
                    "update": {"x-test": "value"}
                }
            ]
        }

        result = validate(overlay, "log")
        assert "[INFO] Validation successful" in result, f"Failed for version 1.1.{patch}"


def test_validate_v1_1_with_extends():
    """Test validation of overlay with extends field."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Extended Overlay",
            "version": "1.0.0"
        },
        "extends": "base-overlay.yaml",
        "actions": [
            {
                "target": "$.info",
                "update": {"x-extended": "true"}
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_with_x_extensions():
    """Test validation with specification extensions (x- properties)."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Extended Info",
            "version": "1.0.0",
            "x-custom-info": "custom value"
        },
        "x-custom-overlay": "overlay extension",
        "actions": [
            {
                "target": "$.info",
                "update": {"x-test": "value"},
                "x-custom-action": "action extension"
            }
        ]
    }

    result = validate(overlay, "log")
    assert "[INFO] Validation successful" in result


def test_validate_v1_1_missing_required_fields():
    """Test validation fails when required fields are missing."""
    # Missing info
    overlay1 = {
        "overlay": "1.1.0",
        "actions": [
            {
                "target": "$.info",
                "update": {}
            }
        ]
    }

    result1 = validate(overlay1, "log")
    assert "[ERROR]" in result1
    assert "'info' is a required property" in result1

    # Missing actions
    overlay2 = {
        "overlay": "1.1.0",
        "info": {
            "title": "Test",
            "version": "1.0.0"
        }
    }

    result2 = validate(overlay2, "log")
    assert "[ERROR]" in result2
    assert "'actions' is a required property" in result2


def test_validate_v1_1_empty_actions():
    """Test validation fails when actions array is empty."""
    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Test",
            "version": "1.0.0"
        },
        "actions": []
    }

    result = validate(overlay, "log")
    assert "[ERROR]" in result
    # Should fail minItems validation
    assert "Validation failed" in result
