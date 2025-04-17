import pytest
from src.oas_patch.overlay import apply_overlay, deep_update


def test_apply_overlay_update_action():
    """Test applying an overlay with update actions."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "summary": "Original summary"
                }
            }
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$.paths['/example'].get",
                "update": {
                    "summary": "Updated summary"
                }
            }
        ]
    }
    result = apply_overlay(openapi_doc, overlay)
    assert result["paths"]["/example"]["get"]["summary"] == "Updated summary"


def test_apply_overlay_remove_action():
    """Test applying an overlay with remove actions."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "summary": "Original summary"
                }
            }
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$.paths['/example'].get",
                "remove": True
            }
        ]
    }
    result = apply_overlay(openapi_doc, overlay)
    assert "get" not in result["paths"]["/example"]


def test_apply_overlay_no_matching_target():
    """Test applying an overlay with no matching JSONPath targets."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "summary": "Original summary"
                }
            }
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$.paths['/nonexistent'].get",
                "update": {
                    "summary": "Updated summary"
                }
            }
        ]
    }
    result = apply_overlay(openapi_doc, overlay)
    assert result == openapi_doc  # No changes should be made


def test_apply_overlay_empty_actions():
    """Test applying an overlay with an empty actions list."""
    openapi_doc = {
        "paths": {
            "/example": {
                "get": {
                    "summary": "Original summary"
                }
            }
        }
    }
    overlay = {
        "actions": []
    }
    result = apply_overlay(openapi_doc, overlay)
    assert result == openapi_doc  # No changes should be made


def test_deep_update_nested_keys():
    """Test deep updating a dictionary with nested keys."""
    target = {
        "key1": {
            "subkey1": "value1"
        }
    }
    updates = {
        "key1": {
            "subkey2": "value2"
        }
    }
    deep_update(target, updates)
    assert target["key1"]["subkey1"] == "value1"
    assert target["key1"]["subkey2"] == "value2"


def test_deep_update_overwrite_keys():
    """Test deep updating a dictionary with overwriting keys."""
    target = {
        "key1": {
            "subkey1": "value1"
        }
    }
    updates = {
        "key1": {
            "subkey1": "new_value1"
        }
    }
    deep_update(target, updates)
    assert target["key1"]["subkey1"] == "new_value1"


def test_deep_update_add_new_keys():
    """Test deep updating a dictionary by adding new keys."""
    target = {
        "key1": {
            "subkey1": "value1"
        }
    }
    updates = {
        "key2": {
            "subkey2": "value2"
        }
    }
    deep_update(target, updates)
    assert target["key1"]["subkey1"] == "value1"
    assert target["key2"]["subkey2"] == "value2"


def test_apply_overlay_update_root():
    """Test applying an overlay with an update action targeting the root."""
    openapi_doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$",  # Root of the document
                "update": {
                    "description": "This is a root-level description"
                }
            }
        ]
    }
    result = apply_overlay(openapi_doc, overlay)
    assert result["description"] == "This is a root-level description"
    assert result["openapi"] == "3.0.3"  # Ensure existing keys are preserved


def test_apply_overlay_remove_root():
    """Test applying an overlay with a remove action targeting the root."""
    openapi_doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$",  # Root of the document
                "remove": True
            }
        ]
    }
    with pytest.raises(ValueError, match="Cannot remove the root of the document"):
        apply_overlay(openapi_doc, overlay)


def test_apply_overlay_non_dict_update_root():
    """Test applying an overlay with a non-dict update action targeting the root."""
    openapi_doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$",  # Root of the document
                "update": "Invalid root update"
            }
        ]
    }
    with pytest.raises(ValueError, match="Cannot perform non-dict update on the root of the document"):
        apply_overlay(openapi_doc, overlay)


def test_apply_overlay_merge_dict_with_array():
    """Test applying an overlay with a non-dict update action targeting the root."""
    openapi_doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "Sample API",
            "version": "1.0.0"
        },
        "paths": {
            "/example": {
                "get": {
                    "summary": "Original summary",
                    "security": [
                        {
                            "api_key": []
                        }
                    ]
                }
            }
        }
    }
    overlay = {
        "actions": [
            {
                "target": "$.paths.*.get",  # Root of the document
                "update": {"security": [{"oauth2": []}]}
            }
        ]
    }
    result = apply_overlay(openapi_doc, overlay)
    assert len(result["paths"]["/example"]["get"]["security"]) == 2  # Ensure both security definitions are present
