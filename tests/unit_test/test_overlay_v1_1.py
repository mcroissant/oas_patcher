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


def test_copy_merges_into_existing_object():
    """Per spec: copy to an existing object target MUST merge, not replace.

    Spec: 'A property that only exists in the target object is left unchanged'
    and copied properties follow the same recursive merge semantics as update.
    """
    openapi_doc = {
        "components": {
            "schemas": {
                "Base": {
                    "type": "object",
                    "description": "Base schema",
                    "properties": {"id": {"type": "integer"}}
                },
                "Extended": {
                    "type": "object",
                    "title": "Extended Schema",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy merge test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.components.schemas['Extended']",
                "copy": "$.components.schemas['Base']",
                "description": "Merge Base into Extended; keys only in Extended must survive"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    extended = result["components"]["schemas"]["Extended"]
    # 'title' exists only in target → must be preserved
    assert extended["title"] == "Extended Schema", \
        "copy must MERGE into existing object, not replace it (title lost)"
    # 'description' exists only in source → must be inserted
    assert extended["description"] == "Base schema"
    # 'type' exists in both (primitive) → source value wins
    assert extended["type"] == "object"
    # 'properties' exists in both (objects) → must be recursively merged
    assert "id" in extended["properties"], "source property 'id' must be added"
    assert "name" in extended["properties"], "target property 'name' must be preserved"


def test_copy_concatenates_into_existing_array():
    """Per spec: copy to an existing non-empty array target MUST concatenate, not replace.

    Spec: array + array → concatenate (same as update merge semantics).
    """
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "tags": ["public", "user"],
                    "security": [{"bearerAuth": []}]
                }
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy concat test", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.paths['/example'].get.security",
                "copy": "$.paths['/example'].get.tags",
                "description": "Append tags into existing security list"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    security = result["paths"]["/example"]["get"]["security"]
    # Original security entry must be preserved
    assert {"bearerAuth": []} in security, \
        "copy must CONCATENATE into existing array, not replace it"
    # Copied items must be appended
    assert "public" in security
    assert "user" in security
    assert len(security) == 3


def test_copy_update_field_ignored_when_copy_present():
    """Per spec: 'The update field has no impact when copy is present.'"""
    openapi_doc = {
        "info": {"title": "Original", "version": "1.0.0"},
        "components": {
            "schemas": {
                "Foo": {"type": "object", "description": "from Foo"}
            }
        }
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy ignores update", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.info",
                "copy": "$.components.schemas['Foo']",
                "update": {"title": "SHOULD BE IGNORED"},
                "description": "update must be ignored because copy is present"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # The 'update' value must be ignored; only copy semantics apply
    assert result["info"].get("title") != "SHOULD BE IGNORED", \
        "update field must have no impact when copy is present"
    # The copy source fields must be present
    assert result["info"]["description"] == "from Foo"


def test_copy_zero_source_matches_no_change():
    """Per spec: 'If the copy expression selects zero nodes, the action succeeds
    without changing the target document.'
    """
    openapi_doc = {
        "info": {"title": "Unchanged", "version": "1.0.0"}
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Zero matches", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.info",
                "copy": "$.nonexistent.path.that.does.not.exist"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert result["info"]["title"] == "Unchanged"
    assert result["info"]["version"] == "1.0.0"


def test_copy_primitive_replaces_primitive():
    """Per spec: primitive + primitive → replace (same as update semantics)."""
    openapi_doc = {
        "info": {"title": "Old Title", "version": "1.0.0"},
        "x-service-name": "old-service"
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Primitive copy", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.x-service-name",
                "copy": "$.info.title",
                "description": "Copy primitive string value"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert result["x-service-name"] == "Old Title"


def test_copy_to_array_indexed_target():
    """Copy to a target selected by integer array index must work."""
    openapi_doc = {
        "servers": [
            {"url": "https://prod.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"}
        ]
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Copy to array index", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.servers[1]",
                "copy": "$.servers[0]",
                "description": "Copy prod server config onto the staging slot"
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    # servers[1] should now have prod's url merged in
    assert result["servers"][1]["url"] == "https://prod.example.com"


def test_update_array_indexed_target():
    """Update targeting an element via integer array index must work."""
    openapi_doc = {
        "servers": [
            {"url": "https://prod.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"}
        ]
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Update array index", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.servers[0]",
                "update": {"description": "Main Production Server"}
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert result["servers"][0]["description"] == "Main Production Server"
    assert result["servers"][0]["url"] == "https://prod.example.com"


def test_remove_array_indexed_target():
    """Remove targeting an element via integer array index must work."""
    openapi_doc = {
        "servers": [
            {"url": "https://prod.example.com"},
            {"url": "https://staging.example.com"}
        ]
    }

    overlay = {
        "overlay": "1.1.0",
        "info": {"title": "Remove array index", "version": "1.0.0"},
        "actions": [
            {
                "target": "$.servers[1]",
                "remove": True
            }
        ]
    }

    result = apply_overlay(openapi_doc, overlay)

    assert len(result["servers"]) == 1
    assert result["servers"][0]["url"] == "https://prod.example.com"


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
