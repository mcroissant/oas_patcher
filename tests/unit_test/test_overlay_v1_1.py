"""Tests for Overlay 1.1.0 features."""
from oas_patch.overlay import apply_overlay


def test_overlay_v1_1_copy_action():
    """Test the new copy action in overlay 1.1.0."""
    openapi_doc = {
        "components": {
            "schemas": {
                "Foo": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.components.schemas['Bar']",
                "copy": "$.components.schemas['Foo']",
                "description": "Copy the Foo Schema to Bar (creates Bar if it doesn't exist)"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # Bar should now have the same structure as Foo
    assert "Bar" in result["components"]["schemas"]
    assert result["components"]["schemas"]["Bar"]["type"] == "object"
    assert "id" in result["components"]["schemas"]["Bar"]["properties"]
    assert "name" in result["components"]["schemas"]["Bar"]["properties"]
    # Ensure Foo is still intact
    assert "Foo" in result["components"]["schemas"]


def test_overlay_v1_1_copy_with_dot_notation():
    """Test copy action using dot notation JSONPath."""
    openapi_doc = {
        "info": {
            "title": "Original API",
            "version": "1.0.0",
            "description": "Original description"
        },
        "paths": {}
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.paths",
                "update": {
                    "/example": {
                        "get": {}
                    }
                }
            },
            {
                "target": "$.paths['/example'].get",
                "copy": "$.info",
                "description": "Copy info to path"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # The get operation should have info copied to it
    assert result["paths"]["/example"]["get"]["title"] == "Original API"
    assert result["paths"]["/example"]["get"]["description"] == "Original description"


def test_overlay_v1_1_copy_nonexistent_source():
    """Test copy action when source path doesn't match anything."""
    openapi_doc = {
        "info": {"title": "Test API", "version": "1.0.0"}
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.info",
                "copy": "$.nonexistent.path",
                "description": "Try to copy from nonexistent path"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # Should not change anything if source doesn't exist
    assert result["info"]["title"] == "Test API"
    assert result["info"]["version"] == "1.0.0"


def test_overlay_v1_1_copy_to_nonexistent_target():
    """Test copy action automatically creates target if it doesn't exist."""
    openapi_doc = {
        "info": {"title": "Test API", "version": "1.0.0"},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.components.schemas['Admin']",
                "copy": "$.components.schemas['User']",
                "description": "Copy User to non-existent Admin schema"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # Admin should be created with User's structure
    assert "Admin" in result["components"]["schemas"]
    assert result["components"]["schemas"]["Admin"]["type"] == "object"
    assert "id" in result["components"]["schemas"]["Admin"]["properties"]
    assert "name" in result["components"]["schemas"]["Admin"]["properties"]
    # Ensure User is unchanged
    assert "User" in result["components"]["schemas"]
    assert result["components"]["schemas"]["User"]["type"] == "object"


def test_overlay_v1_1_primitive_value_update():
    """Test updating primitive values directly (new in 1.1)."""
    openapi_doc = {
        "paths": {
            "/foo": {
                "get": {
                    "description": "Old description",
                    "summary": "Old summary"
                }
            },
            "/bar": {
                "get": {
                    "description": "Another old description"
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Targeted Overlay",
            "version": "1.0.0",
            "description": "Testing direct primitive updates"
        },
        "actions": [
            {
                "target": "$.paths['/foo'].get.description",
                "update": "This is the new description"
            },
            {
                "target": "$.paths['/bar'].get.description",
                "update": "This is the updated description"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert result["paths"]["/foo"]["get"]["description"] == "This is the new description"
    assert result["paths"]["/bar"]["get"]["description"] == "This is the updated description"
    # Summary should remain unchanged
    assert result["paths"]["/foo"]["get"]["summary"] == "Old summary"


def test_overlay_v1_1_remove_primitive_value():
    """Test removing primitive values directly."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "summary": "Test summary",
                    "description": "Test description",
                    "deprecated": True
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Remove primitive", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.paths['/example'].get.deprecated",
                "remove": True
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert "deprecated" not in result["paths"]["/example"]["get"]
    assert result["paths"]["/example"]["get"]["summary"] == "Test summary"


def test_overlay_v1_1_info_description():
    """Test that overlay info object can have a description field."""
    openapi_doc = {"info": {"title": "Test", "version": "1.0.0"}}

    overlay = {
        "overlay": "1.1.0",
        "info": {
            "title": "Overlay with description",
            "version": "1.0.0",
            "description": "This overlay document has a long description thanks to the new field."
        },
        "actions": [
            {
                "target": "$.info",
                "update": {"x-custom": "value"}
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # The overlay itself should be valid (will be tested by validation tests)
    # Here we just ensure applying it works
    assert result["info"]["x-custom"] == "value"


def test_overlay_v1_1_copy_array():
    """Test copying arrays with the copy action."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "tags": ["public", "user"],
                    "security": []
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy array", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.paths['/example'].get.security",
                "copy": "$.paths['/example'].get.tags"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # Security should now be a copy of tags
    assert result["paths"]["/example"]["get"]["security"] == ["public", "user"]


def test_overlay_v1_1_combined_actions():
    """Test combining update and copy actions in the same overlay."""
    openapi_doc = {
        "info": {"title": "API", "version": "1.0.0"},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}}
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Combined actions", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.info.title",
                "update": "Updated API"
            },
            {
                "target": "$.components.schemas",
                "update": {"Admin": {}}
            },
            {
                "target": "$.components.schemas['Admin']",
                "copy": "$.components.schemas['User']"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert result["info"]["title"] == "Updated API"
    assert "Admin" in result["components"]["schemas"]
    assert result["components"]["schemas"]["Admin"]["type"] == "object"
