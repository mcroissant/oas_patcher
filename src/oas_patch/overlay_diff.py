from deepdiff import DeepDiff

def create_overlay(source_doc, target_doc):
    # Compute the differences
    diff = DeepDiff(source_doc, target_doc, view='tree', ignore_order=True)

    # Construct the overlay
    overlay = {"actions": []}

    for diff_item in diff.get('values_changed', []):
        action = _diff_to_action(diff_item, "update")
        overlay["actions"].append(action)

    for diff_item in diff.get('dictionary_item_added', []):
        action = _diff_to_action(diff_item, "update")
        overlay["actions"].append(action)

    for diff_item in diff.get('dictionary_item_removed', []):
        action = _diff_to_action(diff_item, "remove")
        overlay["actions"].append(action)

    for diff_item in diff.get('iterable_item_added', []):
        action = _diff_to_action(diff_item, "update")
        overlay["actions"].append(action)

    for diff_item in diff.get('iterable_item_removed', []):
        action = _diff_to_action(diff_item, "remove")
        overlay["actions"].append(action)

    # Save the overlay to the specified output file
    return overlay

def _diff_to_action(diff_item, action_type):
    path_list = diff_item.path(output_format='list')
    new_value = {}
    if isinstance(path_list[-1], int):
        new_value = diff_item.t2
    else:
        new_value[path_list[-1]] = diff_item.t2
    if action_type == "remove":
        path = _generate_path(path_list)
        return {
            "target": path,
            "remove": True
        }
    
    path = _generate_path(path_list[:-1])
    return {
        "target": path,
        "update": new_value
    }

def _generate_path(path_list):
    path = "$."
    for p in path_list:
        if  isinstance(p, int) :
            path += f"[{p}]"
        elif "/" in p:
            path += f"[\'{p}\']"
        else:
            path += f".{p}" if path != "$." else f"{p}"
    path = path.replace(".[", "[")
    return path