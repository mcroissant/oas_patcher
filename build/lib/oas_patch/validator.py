import yaml
import json
from jsonschema import Draft202012Validator, ValidationError
import os
import argparse

from oas_patch.file_utils import load_file


def load_schema(schema):
    """
    Load the Overlay JSON schema from the schema directory.

    Args:
        schema_name (str): The name of the schema file.

    Returns:
        dict: The loaded JSON schema.
    """
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "schema", schema)
        with open(schema_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {schema}")
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse the schema file: {schema}\n{e}")

def format_errors(errors, output_format):
    """
    Format validation errors based on the specified output format.

    Args:
        errors (list): List of validation errors.
        output_format (str): The desired output format ('sh', 'log', 'yaml').

    Returns:
        str: Formatted error messages.
    """
    if output_format == "yaml":
        formatted_errors = [
            {
                "message": error.message,
                "path": " -> ".join(map(str, error.path)) if error.path else None,
            }
            for error in errors
        ]
        return yaml.dump({"status": "failed", "errors": formatted_errors}, sort_keys=False)
    elif output_format == 'log':  # Default to log-friendly format
        output = ["[ERROR] Validation failed with the following issues"]
        for error in errors:
            error_details = f"{error.message}"
            if error.path:
                error_details += f"\n\t Path: {' -> '.join(map(str, error.path))}"
            if error.schema_path:
                error_details += f"\n\t Schema Path: {' -> '.join(map(str, error.schema_path))}"
            output.append(f"[ERROR] {error_details}")
        return "\n".join(output)
    
    else :
        output = []
        if errors:
            output.append("!!! Validation failed with the following issues:")
            for error in errors:
                output.append(f"- {error.message}")
                if error.path:
                    output.append(f"\tPath: {' -> '.join(map(str, error.path))}")
        else:
            output.append(f"Validation successful")
        return "\n".join(output)


def validate(overlay_path, output_format):
    """
    Validate an Overlay document against its Specification.

    Args:
        file_path (str): Path to the document (YAML/JSON).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be parsed as YAML or JSON.
        ValidationError: If the document is not valid according to the Overlay Specification.
    """
    try:
        # Load the document
        with open(overlay_path, 'r', encoding='utf-8') as f:
            doc = load_file(overlay_path)

        # Validate as Overlay
        overlay_schema = load_schema("overlay_schema_1.0.0.yml")
        validator = Draft202012Validator(overlay_schema)
        errors = list(validator.iter_errors(doc), output_format)
        print(format_errors(errors, output_format))

    except FileNotFoundError:
        print(f"Error: File not found: {overlay_path}")
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error: Failed to parse the document:\n    {e}")
    except ValidationError as e:
        print(f"Validation failed: {e}")
    except ValueError as e:
        print(f"Error: {e}")