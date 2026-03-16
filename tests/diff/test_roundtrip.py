"""Roundtrip tests: diff(a, b) |> apply(a) must equal b for every combination.

Each test builds a source and target document, generates an overlay with
create_overlay(), applies it to a fresh copy of the source, and asserts the
result equals the target.  A passing roundtrip proves the diff action is
correct end-to-end.
"""

import copy
import pytest
from oas_patch.overlay_diff import create_overlay
from oas_patch.overlay import apply_overlay


def roundtrip(source, target):
    """Helper: returns (result, overlay) so tests can inspect on failure."""
    overlay = create_overlay(copy.deepcopy(source), copy.deepcopy(target))
    result = apply_overlay(copy.deepcopy(source), overlay)
    return result, overlay


# ---------------------------------------------------------------------------
# Primitive value changes
# ---------------------------------------------------------------------------

def test_roundtrip_primitive_int_change():
    src = {"a": 1}
    tgt = {"a": 2}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_primitive_string_change():
    src = {"info": {"title": "Old"}}
    tgt = {"info": {"title": "New"}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_primitive_bool_change():
    src = {"deprecated": False}
    tgt = {"deprecated": True}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


# ---------------------------------------------------------------------------
# Bug 4 – type_changes: DeepDiff puts these in a separate category that was
# completely ignored, producing an empty overlay.
# ---------------------------------------------------------------------------

def test_roundtrip_type_change_string_to_int():
    """Changing a value's type (str -> int) must produce a replace update."""
    src = {"a": "hello"}
    tgt = {"a": 42}
    result, overlay = roundtrip(src, tgt)
    assert overlay["actions"], "type_changes must generate at least one action"
    assert result == tgt, "type change str->int not handled"


def test_roundtrip_type_change_dict_to_scalar():
    """Replacing a dict value with a scalar must generate a replace update."""
    src = {"a": {"b": 1}}
    tgt = {"a": "replaced"}
    result, overlay = roundtrip(src, tgt)
    assert overlay["actions"], "type_changes must generate at least one action"
    assert result == tgt, "type change dict->scalar not handled"


def test_roundtrip_type_change_list_to_dict():
    src = {"a": [1, 2]}
    tgt = {"a": {"x": 1}}
    result, overlay = roundtrip(src, tgt)
    assert overlay["actions"], "type_changes must generate at least one action"
    assert result == tgt, "type change list->dict not handled"


def test_roundtrip_type_change_none_to_string():
    src = {"a": None}
    tgt = {"a": "something"}
    result, overlay = roundtrip(src, tgt)
    assert overlay["actions"], "type_changes must generate at least one action"
    assert result == tgt, "type change None->str not handled"


def test_roundtrip_type_change_int_to_list():
    src = {"a": 42}
    tgt = {"a": [1, 2, 3]}
    result, overlay = roundtrip(src, tgt)
    assert overlay["actions"], "type_changes must generate at least one action"
    assert result == tgt, "type change int->list not handled"


def test_roundtrip_type_change_nested():
    """Type change inside a nested structure."""
    src = {"info": {"version": "1.0"}}
    tgt = {"info": {"version": 1}}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, "nested type change not handled"


# ---------------------------------------------------------------------------
# Bug 5 – list index consistency: ignore_order=True can produce remove and
# values_changed actions whose indices are inconsistent after partial removal,
# causing the roundtrip to produce the wrong list.
# ---------------------------------------------------------------------------

def test_roundtrip_list_shrink_with_value_change():
    """[1,2,3] -> [1,4]: one element changes, one is removed."""
    src = {"a": [1, 2, 3]}
    tgt = {"a": [1, 4]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list shrink+value change: overlay=%s result=%s" % (overlay, result)
    )


def test_roundtrip_list_element_replaced():
    """[x,y,z] -> [x,w]: one element changed, one removed."""
    src = {"a": ["x", "y", "z"]}
    tgt = {"a": ["x", "w"]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list element replaced: overlay=%s result=%s" % (overlay, result)
    )


def test_roundtrip_list_all_elements_shift():
    """[1,2,3] -> [2,3,4]: all elements change (shift)."""
    src = {"a": [1, 2, 3]}
    tgt = {"a": [2, 3, 4]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list full shift: overlay=%s result=%s" % (overlay, result)
    )


def test_roundtrip_list_of_dicts_remove_and_update():
    """Mixed list of objects: one removed, one field updated."""
    src = {
        "servers": [
            {"url": "https://prod.example.com", "description": "Production"},
            {"url": "https://staging.example.com", "description": "Staging"},
            {"url": "https://dev.example.com", "description": "Dev"},
        ]
    }
    tgt = {
        "servers": [
            {"url": "https://prod.example.com", "description": "Main Production"},
            {"url": "https://staging.example.com", "description": "Staging"},
        ]
    }
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "servers remove+update: overlay=%s result=%s" % (overlay, result)
    )


# ---------------------------------------------------------------------------
# Bug 6 – _apply_update with list parent + primitive element: always called
# deep_update which requires a dict, crashing on int/str list elements.
# ---------------------------------------------------------------------------

def test_roundtrip_list_middle_primitive_change():
    """Change one primitive in the middle of a list."""
    src = {"a": [10, 20, 30]}
    tgt = {"a": [10, 99, 30]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list middle primitive: overlay=%s result=%s" % (overlay, result)
    )


def test_roundtrip_list_primitive_first_element():
    src = {"codes": [200, 404, 500]}
    tgt = {"codes": [201, 404, 500]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list first primitive change: overlay=%s result=%s" % (overlay, result)
    )


def test_roundtrip_list_string_element_change():
    src = {"tags": ["alpha", "beta", "gamma"]}
    tgt = {"tags": ["alpha", "delta", "gamma"]}
    result, overlay = roundtrip(src, tgt)
    assert result == tgt, (
        "list string element: overlay=%s result=%s" % (overlay, result)
    )


# ---------------------------------------------------------------------------
# Structural changes (existing behaviour that must stay correct)
# ---------------------------------------------------------------------------

def test_roundtrip_dict_key_added():
    src = {"info": {"title": "API"}}
    tgt = {"info": {"title": "API", "x-custom": "value"}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_dict_key_removed():
    src = {"info": {"title": "API", "x-extra": "remove me"}}
    tgt = {"info": {"title": "API"}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_list_item_added():
    src = {"tags": ["a"]}
    tgt = {"tags": ["a", "b"]}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_list_item_removed():
    src = {"tags": ["a", "b"]}
    tgt = {"tags": ["a"]}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_path_with_slash():
    src = {"paths": {"/foo": {"get": {"summary": "old"}}}}
    tgt = {"paths": {"/foo": {"get": {"summary": "new"}}}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_numeric_string_keys():
    """HTTP status codes as dict keys."""
    src = {"responses": {"200": {"description": "ok"}, "404": {"description": "not found"}}}
    tgt = {"responses": {"200": {"description": "OK"}, "404": {"description": "Not Found"}}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_new_top_level_key():
    src = {"info": {"title": "Test"}}
    tgt = {"info": {"title": "Test"}, "x-new": "value"}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_remove_top_level_key():
    src = {"info": {"title": "Test"}, "x-old": "value"}
    tgt = {"info": {"title": "Test"}}
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_replace_servers_list():
    """Replace entire servers list (compliance-set scenario)."""
    src = {
        "openapi": "3.1.0",
        "info": {"title": "API", "version": "1.0.0"},
        "servers": [
            {"url": "https://api.example.com/v1", "description": "Production"},
            {"url": "https://staging.example.com/v1", "description": "Staging"},
        ],
    }
    tgt = {
        "openapi": "3.1.0",
        "info": {"title": "API", "version": "1.0.0"},
        "servers": [{"url": "http://api-test-tunnel.local", "description": "Local"}],
    }
    result, _ = roundtrip(src, tgt)
    assert result == tgt


def test_roundtrip_patternproperties_replaced_by_additionalproperties():
    """Regression: removed keys inside a replaced object must generate remove actions."""
    src = {
        "schema": {
            "columns": {
                "patternProperties": {".*": {"description": "Dynamic"}},
                "type": "object",
            }
        }
    }
    tgt = {
        "schema": {
            "columns": {
                "type": "object",
                "additionalProperties": True,
                "description": "Dynamic",
            }
        }
    }
    result, _ = roundtrip(src, tgt)
    assert result == tgt
