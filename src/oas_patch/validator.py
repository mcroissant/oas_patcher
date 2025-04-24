import yaml
from jsonschema import Draft202012Validator, ValidationError
from importlib.resources import files, as_file


def load_schema(schema):
    """
    Load the Overlay JSON schema from the schema directory.

    Args:
        schema (str): The name of the schema file.

    Returns:
        dict: The loaded JSON schema.
    """
    try:
        schema_path = files("oas_patch.schema").joinpath(schema)
        with as_file(schema_path) as path:
            with path.open("r", encoding="utf-8") as f:
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
        status = "failed" if errors else "success"
        formatted_errors = [
            {
                "message": error.message,
                "path": " -> ".join(map(str, error.path)) if error.path else None,
            }
            for error in errors
        ]
        return yaml.dump({"status": status, "errors": formatted_errors}, sort_keys=False)
    elif output_format == 'log':  # Default to log-friendly format
        output = ["[ERROR] Validation failed with the following issues"] if errors else ["[INFO] Validation successful"]
        for error in errors:
            error_details = f"{error.message}"
            if error.path:
                error_details += f"\n\t Path: {' -> '.join(map(str, error.path))}"
            if error.schema_path:
                error_details += f"\n\t Schema Path: {' -> '.join(map(str, error.schema_path))}"
            output.append(f"[ERROR] {error_details}")
        return "\n".join(output)
    else:
        output = []
        if errors:
            output.append("!!! Validation failed with the following issues:")
            for error in errors:
                output.append(f"- {error.message}")
                if error.path:
                    output.append(f"\tPath: {' -> '.join(map(str, error.path))}")
        else:
            output.append("Validation successful")
        return "\n".join(output)


def validate(overlay_doc, output_format):
    """
    Validate an Overlay document against its Specification.

    Args:
        file_path (str): Path to the document (YAML/JSON).
        output_format (str): Format for the output ('sh', 'log', 'yaml')

    Returns:
        str: Formatted validation results or error message
    """
    try:
        # Validate as Overlay
        overlay_schema = load_schema("overlay_schema_1.0.0.yml")
        validator = Draft202012Validator(overlay_schema)
        errors = list(validator.iter_errors(overlay_doc))
        return format_errors(errors, output_format)
    except ValidationError as e:
        return f"Validation failed: {e}"
    except ValueError as e:
        return f"Error: {e}"
