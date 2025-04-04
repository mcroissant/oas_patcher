"""Module providing set of function to load and save YAML \
    and JSON files, also helps removing non printable characters"""

import json
import re
import yaml


def load_yaml(file_path, sanitize=False):
    """Load a YAML file, optionally sanitizing its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if sanitize:
                content = sanitize_content(content)
            return yaml.safe_load(content)
    except FileNotFoundError as not_found_exc:
        raise FileNotFoundError(f"File not found: {file_path}") from not_found_exc
    except yaml.YAMLError as yaml_error_exc:
        raise ValueError(f"Invalid YAML format in file {file_path}") from yaml_error_exc


def load_json(file_path, sanitize=False):
    """Load a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if sanitize:
                content = sanitize_content(content)
            return json.loads(content)
    except FileNotFoundError as not_found_exc:
        raise FileNotFoundError(f"File not found: {file_path}") from not_found_exc
    except json.JSONDecodeError as json_error_exc:
        raise ValueError(f"Invalid JSON format in file {file_path}") from json_error_exc


def load_file(file_path, sanitize=False):
    """Load a YAML or JSON file based on its extension."""
    if file_path.endswith(('.yaml', '.yml')):
        return load_yaml(file_path, sanitize)
    if file_path.endswith('.json'):
        return load_json(file_path, sanitize)
    raise ValueError(f"Unsupported file format: {file_path}. Supported : .yaml, .yml, .json")


def save_yaml(data, file_path):
    """Save data to a YAML file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, sort_keys=False, default_flow_style=False)


def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


def save_file(data, file_path):
    """Save data to a YAML or JSON file based on its extension."""
    if file_path.endswith(('.yaml', '.yml')):
        save_yaml(data, file_path)
    elif file_path.endswith('.json'):
        save_json(data, file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}. Supported : .yaml, .yml, .json")


def sanitize_content(content):
    """Remove non-printable characters from the content."""
    return re.sub(r'[^\x20-\x7E\n\r]', '', content)
