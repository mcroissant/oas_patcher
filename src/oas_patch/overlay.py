"""Module to apply the overlays to the OAS"""

import copy as _copy

from jsonpath_ng.ext import parse


def apply_overlay(openapi_doc, overlay):
    """Apply overlay actions to the OpenAPI document."""
    for action in overlay.get("actions", []):
        jsonpath_expr = parse(action["target"])

        if action.get("remove"):
            # jsonpath_ng's find() mutates the document when a filter expression
            # targets dict values (converts the dict to a synthetic list of values).
            # Run find() on a deep-copy snapshot so the real document is untouched,
            # then delete each matched node by navigating the path chain.
            snapshot_matches = list(jsonpath_expr.find(_copy.deepcopy(openapi_doc)))
            # Reverse order prevents index-shifting when deleting from lists.
            for match in reversed(snapshot_matches):
                _remove_by_path(match, openapi_doc)
        else:
            matches = list(jsonpath_expr.find(openapi_doc))

            # If no matches and this is a copy action, try to create the target
            if not matches and "copy" in action:
                matches = _create_target_for_copy(openapi_doc, action["target"], jsonpath_expr)

            for match in matches:
                parent, key = _get_parent_and_key(match, openapi_doc)
                _apply_action(jsonpath_expr, parent, key, match, action, openapi_doc)
    return openapi_doc


def _remove_by_path(match, openapi_doc):
    """Delete a matched node from the document by navigating its path chain.

    Uses the path chain recorded in the match's context hierarchy rather than
    jsonpath_ng.filter(), which corrupts dict nodes when filter expressions are
    used (it converts them to synthetic lists of values).
    """
    # Walk the context chain from the match up to (but not including) the root
    # to reconstruct the ordered list of path steps.
    path_parts = []
    node = match
    while node.context is not None:
        path_parts.insert(0, node.path)
        node = node.context

    if not path_parts:
        raise ValueError("Cannot remove the root of the document")

    # Navigate to the direct parent of the target node.
    parent = openapi_doc
    for path_part in path_parts[:-1]:
        if hasattr(path_part, "fields"):
            parent = parent[path_part.fields[0]]
        elif hasattr(path_part, "indices"):
            parent = parent[path_part.indices[0]]
        else:
            return  # Unsupported path step – skip silently

    last_part = path_parts[-1]

    if hasattr(last_part, "fields"):
        # Named dict key (e.g. $.info.license)
        key = last_part.fields[0]
        if isinstance(parent, dict) and key in parent:
            del parent[key]

    elif hasattr(last_part, "indices"):
        index = last_part.indices[0]
        if isinstance(parent, list):
            # Direct list index (e.g. $.servers[1])
            if 0 <= index < len(parent):
                del parent[index]
        elif isinstance(parent, dict):
            # Filter expression on a dict: jsonpath_ng builds a synthetic list
            # from dict.values() in insertion order, so the index maps directly
            # to the n-th key of the dict.
            keys = list(parent.keys())
            if 0 <= index < len(keys):
                del parent[keys[index]]


def _get_parent_and_key(match, openapi_doc):
    """Retrieve the parent and key for a given match."""
    if match.context is None:
        return openapi_doc, None  # Root of the document
    parent = match.context.value
    if hasattr(match.path, "fields"):
        key = match.path.fields[0]
    elif hasattr(match.path, "indices"):
        key = match.path.indices[0]
    else:
        key = None
    return parent, key


def _create_target_for_copy(openapi_doc, target_path, jsonpath_expr):
    """
    Create a target path for copy action if it doesn't exist.
    Returns a list with a synthetic match object for the created target.
    """
    import re

    # Try to parse the target path to extract parent and key
    # Pattern for $.path.to.parent['key'] or $.path.to.parent.key
    bracket_pattern = r"^(.+)\['([^']+)'\]$"
    dot_pattern = r"^(.+)\.([^.]+)$"

    parent_path = None
    key = None

    # Try bracket notation first
    match = re.match(bracket_pattern, target_path)
    if match:
        parent_path = match.group(1)
        key = match.group(2)
    else:
        # Try dot notation
        match = re.match(dot_pattern, target_path)
        if match:
            parent_path = match.group(1)
            key = match.group(2)

    if not parent_path or not key:
        # Can't parse the path, return empty list
        return []

    # Find the parent
    parent_expr = parse(parent_path)
    parent_matches = list(parent_expr.find(openapi_doc))

    if not parent_matches:
        # Parent doesn't exist either, can't create
        return []

    parent = parent_matches[0].value

    # Create a placeholder in the parent
    if isinstance(parent, dict):
        parent[key] = None  # Placeholder that will be replaced by copy

        # Now find the newly created path
        new_matches = list(jsonpath_expr.find(openapi_doc))
        return new_matches

    return []


def _apply_action(jsonpath_expr, parent, key, match, action, openapi_doc):
    """Apply a single action to the matched part of the document."""
    if match.context is not None:
        if "copy" in action:
            _apply_copy(parent, key, action["copy"], openapi_doc)
        elif "update" in action:
            _apply_update(parent, key, action["update"])
    elif parent is openapi_doc:  # Handle the case where the matched item is the root
        if "copy" in action:
            _apply_root_copy(openapi_doc, action["copy"], openapi_doc)
        elif "update" in action:
            _apply_root_update(openapi_doc, action["update"])


def _apply_update(parent, key, update):
    """Apply an update action to the parent."""

    if isinstance(parent, list):
        deep_update(parent[key], update)
    elif isinstance(parent.get(key), dict) and isinstance(update, dict):
        deep_update(parent[key], update)
    elif isinstance(parent.get(key), list) and isinstance(update, list):
        parent[key].extend(update)
    elif isinstance(parent.get(key), list):
        parent[key].append(update)
    else:
        parent[key] = update


def _apply_root_update(openapi_doc, update):
    """Apply an update action to the root of the document."""
    if isinstance(update, dict):
        deep_update(openapi_doc, update)
    else:
        raise ValueError("Cannot perform non-dict update on the root of the document")


def _apply_copy(parent, key, copy_path, openapi_doc):
    """Apply a copy action to the parent using a JSONPath to find the source.

    Per spec: merge semantics of copy are identical to those of update.
    - object target + object source  -> recursive merge
    - array target  + array source   -> concatenate
    - primitive target               -> replace
    Zero matches -> no-op (spec: "action succeeds without changing the target").
    """
    jsonpath_expr = parse(copy_path)
    matches = jsonpath_expr.find(openapi_doc)

    if not matches:
        # Zero nodes: succeed without changing the document
        return

    # Use the first match as the source value
    source_value = matches[0].value

    # Create a deep copy to avoid reference issues
    source_value = _copy.deepcopy(source_value)

    # Reuse update merge semantics: merge objects, concatenate arrays, replace primitives
    _apply_update(parent, key, source_value)


def _apply_root_copy(openapi_doc, copy_path, source_doc):
    """Apply a copy action to the root of the document."""
    jsonpath_expr = parse(copy_path)
    matches = jsonpath_expr.find(source_doc)

    if not matches:
        # No matches found, no action taken
        return

    source_value = matches[0].value

    if isinstance(source_value, dict):
        deep_update(openapi_doc, source_value)
    else:
        raise ValueError("Cannot perform non-dict copy on the root of the document")


def deep_update(target, updates):
    """Iteratively update a dictionary while preserving existing keys."""
    stack = [(target, updates)]
    while stack:
        current_target, current_updates = stack.pop()
        for key, value in current_updates.items():
            if (
                isinstance(value, dict)
                and key in current_target
                and isinstance(current_target[key], dict)
            ):
                stack.append((current_target[key], value))
            elif (
                isinstance(value, list)
                and key in current_target
                and isinstance(current_target[key], list)
            ):
                current_target[key].extend(value)
            else:
                current_target[key] = value
