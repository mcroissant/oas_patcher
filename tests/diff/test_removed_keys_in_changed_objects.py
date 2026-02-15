"""Tests for ensuring removed keys in changed objects generate remove actions."""

import json
import pytest
from oas_patch.overlay_diff import create_overlay
from oas_patch.overlay import apply_overlay


def test_patternProperties_removal():
    """Test that patternProperties is removed when replaced with additionalProperties."""
    source = {
        "schema": {
            "columns": {
                "patternProperties": {
                    ".*": {"description": "Dynamic columns"}
                },
                "type": "object"
            }
        }
    }

    target = {
        "schema": {
            "columns": {
                "type": "object",
                "additionalProperties": True,
                "description": "Dynamic columns"
            }
        }
    }

    # Generate overlay
    overlay = create_overlay(source, target)

    # Verify remove action for patternProperties exists
    remove_actions = [a for a in overlay["actions"] if a.get("remove")]
    assert len(remove_actions) == 1
    assert "patternProperties" in remove_actions[0]["target"]

    # Apply overlay and verify result matches target
    result = apply_overlay(json.loads(json.dumps(source)), overlay)
    assert result == target


def test_multiple_removed_keys():
    """Test that multiple removed keys generate multiple remove actions."""
    source = {
        "obj": {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
    }

    target = {
        "obj": {
            "key1": "value1",
            "key4": "value4"
        }
    }

    # Generate overlay
    overlay = create_overlay(source, target)

    # Verify remove actions for key2 and key3 exist
    remove_actions = [a for a in overlay["actions"] if a.get("remove")]
    assert len(remove_actions) == 2
    removed_keys = [a["target"].split(".")[-1] for a in remove_actions]
    assert "key2" in removed_keys
    assert "key3" in removed_keys

    # Apply overlay and verify result matches target
    result = apply_overlay(json.loads(json.dumps(source)), overlay)
    assert result == target


def test_nested_object_replacement_with_removed_keys():
    """Test nested object replacement where some keys are removed."""
    source = {
        "paths": {
            "/metadata": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "columns": {
                                                "patternProperties": {
                                                    ".*": {"description": "Dynamic"}
                                                },
                                                "type": "object"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    target = {
        "paths": {
            "/metadata": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "properties": {
                                            "columns": {
                                                "type": "object",
                                                "additionalProperties": True,
                                                "description": "Dynamic"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Generate overlay
    overlay = create_overlay(source, target)

    # Verify remove action for patternProperties exists
    remove_actions = [a for a in overlay["actions"] if a.get("remove")]
    assert len(remove_actions) == 1
    assert "patternProperties" in remove_actions[0]["target"]

    # Apply overlay and verify result matches target
    result = apply_overlay(json.loads(json.dumps(source)), overlay)
    assert result == target


def test_diff_apply_roundtrip_with_real_samples():
    """Test that diff->apply roundtrip works with real sample files."""
    # This test requires the sample files to be available
    import os

    samples_dir = os.path.join(os.path.dirname(__file__), "..", "..", "samples")
    file_02 = os.path.join(samples_dir, "02_api_oas3.json")
    file_03 = os.path.join(samples_dir, "03_api_oas3_manual_fix.json")

    if not os.path.exists(file_02) or not os.path.exists(file_03):
        pytest.skip("Sample files not available")

    with open(file_02) as f:
        source = json.load(f)

    with open(file_03) as f:
        target = json.load(f)

    # Generate overlay
    overlay = create_overlay(source, target)

    # Verify patternProperties remove actions exist
    remove_actions = [a for a in overlay["actions"] if a.get("remove")]
    patternprop_removes = [a for a in remove_actions if "patternProperties" in a["target"]]
    assert len(patternprop_removes) >= 1, "Expected at least one patternProperties remove action"

    # Apply overlay and verify result matches target
    result = apply_overlay(json.loads(json.dumps(source)), overlay)
    assert result == target, "Applying generated overlay should produce exact target document"
