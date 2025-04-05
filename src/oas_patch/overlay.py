"""Module to apply the overlays to the OAS"""

from jsonpath_ng.ext import parse


def apply_overlay(openapi_doc, overlay):
    """Apply overlay actions to the OpenAPI document."""
    for action in overlay.get('actions', []):
        jsonpath_expr = parse(action['target'])
        for match in jsonpath_expr.find(openapi_doc):
            parent, key = _get_parent_and_key(match, openapi_doc)
            _apply_action(jsonpath_expr, parent, key, match, action, openapi_doc)
    return openapi_doc


def _get_parent_and_key(match, openapi_doc):
    """Retrieve the parent and key for a given match."""
    if match.context is None:
        return openapi_doc, None  # Root of the document
    parent = match.context.value
    if hasattr(match.path, 'fields'):
        key = match.path.fields[0]
    elif hasattr(match.path, 'index'):
        key = match.path.index
    else:
        key = None
    return parent, key


def _apply_action(jsonpath_expr, parent, key, match, action, openapi_doc):
    """Apply a single action to the matched part of the document."""
    if match.context is not None:
        if 'remove' in action:
            jsonpath_expr.filter(lambda d: True, openapi_doc)
        elif 'update' in action:
            _apply_update(parent, key, action['update'])
    elif parent is openapi_doc:  # Handle the case where the matched item is the root
        if 'update' in action:
            _apply_root_update(openapi_doc, action['update'])
        elif 'remove' in action:
            raise ValueError("Cannot remove the root of the document")


def _apply_update(parent, key, update):
    """Apply an update action to the parent."""
    if isinstance(parent, list):
        deep_update(parent[key], update)
    elif isinstance(update, dict) and isinstance(parent.get(key), dict):
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


def deep_update(target, updates):
    """Iteratively update a dictionary while preserving existing keys."""
    stack = [(target, updates)]
    while stack:
        current_target, current_updates = stack.pop()
        for key, value in current_updates.items():
            if isinstance(value, dict) and key in current_target and isinstance(current_target[key], dict):
                stack.append((current_target[key], value))
            elif isinstance(value, list) and key in current_target and isinstance(current_target[key], list):
                current_target[key].extend(value)
            else:
                current_target[key] = value
