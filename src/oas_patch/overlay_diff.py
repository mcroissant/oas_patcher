from deepdiff import DeepDiff
from enum import Enum, auto


# JSON fields
TARGET_FIELD = 'target'
ACTIONS_FIELD = 'actions'


class ActionType(Enum):
    REMOVE = auto()
    UPDATE = auto()
    ITERABLE_ITEM_ADDED = auto()


def create_overlay(source_doc, target_doc):
    # Compute the differences
    diff = DeepDiff(source_doc, target_doc, view='tree', ignore_order=True)
    overlay = {
        'overlay': '1.0.0',
        'info': {
            'title': 'oas-patch generated overlay',
            'version': '1.0.0'
        },
        'actions': []
    }

    # Add remove actions first
    for diff_item in diff.get('dictionary_item_removed', []):
        action = _diff_to_action(diff_item, ActionType.REMOVE)
        overlay[ACTIONS_FIELD].append(action)

    for diff_item in diff.get('iterable_item_removed', []):
        action = _diff_to_action(diff_item, ActionType.REMOVE)
        overlay[ACTIONS_FIELD].append(action)

    # Add update actions next
    for diff_item in diff.get('values_changed', []):
        action = _diff_to_action(diff_item, ActionType.UPDATE)
        overlay[ACTIONS_FIELD].append(action)

    for diff_item in diff.get('dictionary_item_added', []):
        action = _diff_to_action(diff_item, ActionType.UPDATE)
        overlay[ACTIONS_FIELD].append(action)

    for diff_item in diff.get('iterable_item_added', []):
        action = _diff_to_action(diff_item, ActionType.ITERABLE_ITEM_ADDED)
        overlay[ACTIONS_FIELD].append(action)

    return overlay


def _diff_to_action(diff_item, action_type: ActionType):
    path_list = diff_item.path(output_format='list')
    new_value = {}

    if action_type == ActionType.REMOVE:
        path = _generate_path(path_list)
        return {
            "target": path,
            "remove": True
        }

    if action_type == ActionType.ITERABLE_ITEM_ADDED:
        new_value = diff_item.t2
        path = _generate_path(path_list[:-1])
    elif isinstance(path_list[-1], int):
        new_value = diff_item.t2
        path = _generate_path(path_list)
    else:
        new_value[path_list[-1]] = diff_item.t2
        path = _generate_path(path_list[:-1])
    return {
        "target": path,
        "update": new_value
    }


def _generate_path(path_list):
    """Generate a JSONPath from a path list"""
    if not path_list:
        return "$"

    path = "$"
    pattern_parts = []

    for i, p in enumerate(path_list):
        if isinstance(p, int):
            pattern_parts.append(f"[{p}]")
        elif isinstance(p, str) and p.isdigit():
            pattern_parts.append(f"['{p}']")
        elif "/" in str(p):
            pattern_parts.append(f"[\'{p}\']")
        else:
            pattern_parts.append(f".{p}")

    path += "".join(pattern_parts)
    return path.replace(".[", "[")
