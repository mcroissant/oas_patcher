"""Unified CLI module for oas-patch with both legacy and enhanced functionality."""

import sys
import json
import yaml
from pathlib import Path
from typing import Optional

import click
from oas_patch.file_utils import load_file, save_file
from oas_patch.overlay import apply_overlay
from oas_patch.validator import validate as validate_overlay
from oas_patch.overlay_diff import create_overlay

# Import new enhanced functionality with graceful fallback
try:
    from oas_patch.bundle_manager import BundleManager
    from oas_patch.environment_manager import EnvironmentManager
    from oas_patch.template_engine import TemplateEngine
    from oas_patch.cli_utils import cli_utils

    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    # Fallback if enhanced dependencies are not installed
    ENHANCED_FEATURES_AVAILABLE = False
    BundleManager = None
    EnvironmentManager = None
    TemplateEngine = None
    cli_utils = None


def parse_cli_variables(var_strings):
    """Parse CLI variable strings in format key=value."""
    variables = {}
    for var_string in var_strings:
        if "=" not in var_string:
            raise click.BadParameter(
                f"Variable must be in format key=value: {var_string}"
            )
        key, value = var_string.split("=", 1)
        variables[key.strip()] = value.strip()
    return variables


def auto_generate_output_filename(
    input_file: str, bundle_name: str, output_format: str
) -> str:
    """Generate output filename based on input and bundle name."""
    input_path = Path(input_file)
    stem = input_path.stem
    ext = ".yaml" if output_format == "yaml" else ".json"
    return f"{stem}-{bundle_name}{ext}"


def determine_output_format(input_file: str, format_override: Optional[str]) -> str:
    """Determine output format based on input file or override."""
    if format_override:
        return format_override

    if input_file.endswith((".yaml", ".yml")):
        return "yaml"
    elif input_file.endswith(".json"):
        return "json"
    else:
        return "yaml"  # Default to YAML


@click.group()
@click.version_option()
def cli():
    """
    OAS Patcher - OpenAPI overlay management tool.

    Apply overlays to OpenAPI documents with support for both simple overlays
    and advanced bundle-based configuration with environment-specific variables.

    Use 'oas-patch COMMAND --help' for detailed help on any command.
    """
    pass


@cli.group()
def bundle():
    """
    Bundle management commands.

    Manage overlay bundles and environments for complex OpenAPI document processing.
    """
    pass


@cli.command()
@click.argument("openapi")
@click.argument("overlay")
@click.option(
    "-o",
    "--output",
    help="Path to save the modified OpenAPI document. Defaults to stdout.",
)
@click.option(
    "--sanitize",
    is_flag=True,
    help="Remove special characters from the OpenAPI document.",
)
def overlay(openapi, overlay, output, sanitize):
    """
    Apply an OpenAPI Overlay to your OpenAPI document.

    OPENAPI: Path to the OpenAPI description (YAML/JSON)
    OVERLAY: Path to the Overlay document (YAML/JSON)
    """
    try:
        openapi_doc = load_file(openapi, sanitize)
        overlay_doc = load_file(overlay)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    modified_doc = apply_overlay(openapi_doc, overlay_doc)

    if output:
        save_file(modified_doc, output)
        click.echo(f"Modified OpenAPI document saved to {output}")
    else:
        if openapi.endswith((".yaml", ".yml")):
            yaml.Dumper.ignore_aliases = lambda *args: True
            click.echo(
                yaml.dump(modified_doc, sort_keys=False, default_flow_style=False)
            )
        elif openapi.endswith(".json"):
            click.echo(json.dumps(modified_doc, indent=2))


@cli.command()
@click.argument("original")
@click.argument("modified")
@click.option("-o", "--output", help="Path to save the generated OpenAPI Overlay.")
def diff(original, modified, output):
    """
    Generate an OpenAPI Overlay from the differences between two OpenAPI documents.

    """
    try:
        original_doc = load_file(original)
        modified_doc = load_file(modified)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    overlay_doc = create_overlay(original_doc, modified_doc)

    if output:
        save_file(overlay_doc, output)
        click.echo(f"Generated overlay saved to {output}")
    else:
        if original.endswith((".yaml", ".yml")):
            yaml.Dumper.ignore_aliases = lambda *args: True
            click.echo(
                yaml.dump(overlay_doc, sort_keys=False, default_flow_style=False)
            )
        elif original.endswith(".json"):
            click.echo(json.dumps(overlay_doc, indent=2))


@cli.command()
@click.argument("overlay_file")
@click.option(
    "--format",
    type=click.Choice(["sh", "log", "yaml"]),
    default="sh",
    help="Output format for validation results (shell, log or yaml).",
)
def validate(overlay_file, format):
    """
    Validate an OpenAPI Overlay document against the specification.

    OVERLAY_FILE: Path to the overlay document to validate (YAML/JSON)
    """
    try:
        overlay_doc = load_file(overlay_file)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    try:
        output = validate_overlay(overlay_doc, format)
        click.echo(output)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: Unable to load the document. {e}", err=True)
        sys.exit(1)


# =============================================================================
# ENHANCED COMMANDS (require additional dependencies)
# =============================================================================


def require_enhanced_features():
    """Check if enhanced features are available."""
    if not ENHANCED_FEATURES_AVAILABLE:
        click.echo("Enhanced features require additional dependencies.", err=True)
        click.echo("Please install with: pip install Jinja2 rich click", err=True)
        sys.exit(1)


@bundle.command()
@click.argument("openapi_file")
@click.argument(
    "bundle_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--output", "-o", help="Output file path (auto-generated if not specified)"
)
@click.option("--env", "-e", help="Environment name to use")
@click.option(
    "--format", "-f", type=click.Choice(["yaml", "json"]), help="Output format"
)
@click.option("--var", multiple=True, help="Variables in key=value format (repeatable)")
@click.option("--dry-run", is_flag=True, help="Preview changes without saving")
@click.option(
    "--verbose", "-v", is_flag=True, help="Verbose output with progress indicators"
)
def apply(openapi_file, bundle_file, output, env, format, var, dry_run, verbose):
    """
    Apply overlay bundle to OpenAPI document.

    OPENAPI_FILE: Path to the OpenAPI document (YAML/JSON)
    BUNDLE_FILE: Path to the bundle configuration file (e.g., bundle.yaml)
    """
    require_enhanced_features()

    try:
        # Load bundle configuration first to get bundle name
        try:
            bundle_config = load_file(str(bundle_file))
        except Exception as e:
            click.echo(f"Error: Failed to load bundle file: {e}", err=True)
            sys.exit(1)

        bundle_name = bundle_config.get("name", bundle_file.stem)
        bundle_dir = bundle_file.parent

        # Initialize managers with bundle directory
        env_manager = EnvironmentManager(str(bundle_dir))
        template_engine = TemplateEngine()

        if verbose:
            cli_utils.print_header(f"Applying Bundle: {bundle_name}")

        # Parse CLI variables
        cli_variables = parse_cli_variables(var) if var else {}

        # Load OpenAPI document
        if verbose:
            cli_utils.print_info(f"Loading OpenAPI document: {openapi_file}")

        try:
            openapi_doc = load_file(openapi_file)
        except (FileNotFoundError, ValueError) as e:
            cli_utils.print_error(f"Failed to load OpenAPI document: {e}")
            sys.exit(1)

        if verbose:
            cli_utils.print_info(f"Loading bundle configuration: {bundle_file}")

        # Validate bundle structure
        required_fields = ["name", "overlays"]
        for field in required_fields:
            if field not in bundle_config:
                cli_utils.print_error(f"Bundle file missing required field: {field}")
                sys.exit(1)

        # Get overlays from bundle config
        overlays = bundle_config.get("overlays", [])

        # Filter overlays by environment if specified
        if env:
            filtered_overlays = []
            for overlay in overlays:
                overlay_env = overlay.get("environment", [])
                if not overlay_env or env in overlay_env:
                    filtered_overlays.append(overlay)
            overlays = filtered_overlays

            if verbose:
                cli_utils.print_info(f"Using environment: {env}")
                cli_utils.print_info(f"Found {len(overlays)} overlays for environment")
        else:
            if verbose:
                cli_utils.print_info(f"Using all overlays ({len(overlays)})")

        if not overlays:
            cli_utils.print_warning("No overlays found for specified environment")
            return

        # Get merged variables
        variables = {}

        # Add environment variables if environment manager can find them
        try:
            if env:
                variables = env_manager.get_variables(env, cli_variables)
            else:
                variables = cli_variables.copy()
        except Exception:
            # If environment manager fails, just use CLI variables
            variables = cli_variables.copy()

        # Add bundle variables
        bundle_vars = bundle_config.get("variables", {})
        for key, value in bundle_vars.items():
            if key not in variables:  # Don't override env or CLI variables
                variables[key] = value

        if verbose and variables:
            cli_utils.print_info(f"Using {len(variables)} variables")

        # Determine output settings
        output_format = determine_output_format(openapi_file, format)
        if not output:
            output = auto_generate_output_filename(
                openapi_file, bundle_name, output_format
            )

        if dry_run:
            cli_utils.print_dry_run_header()

        # Apply overlays sequentially
        modified_doc = openapi_doc.copy()
        overlays_applied = 0

        with cli_utils.create_progress_context("Applying overlays") as progress:
            if verbose:
                task = progress.add_task("Processing overlays...", total=len(overlays))

            for overlay_config in overlays:
                if verbose:
                    cli_utils.print_info(
                        f"Processing overlay: {overlay_config.get('path', 'unknown')}"
                    )

                # Resolve overlay file path relative to bundle file
                overlay_path_str = overlay_config.get("path")
                if not overlay_path_str:
                    cli_utils.print_error("Overlay missing required 'path' field")
                    continue

                if Path(overlay_path_str).is_absolute():
                    overlay_path = Path(overlay_path_str)
                else:
                    overlay_path = bundle_file.parent / overlay_path_str

                try:
                    overlay_data = load_file(str(overlay_path))
                except (FileNotFoundError, ValueError) as e:
                    cli_utils.print_error(
                        f"Failed to load overlay {overlay_path_str}: {e}"
                    )
                    continue

                # Merge overlay variables
                overlay_variables = variables.copy()
                overlay_vars = overlay_config.get("variables", {})
                if overlay_vars:
                    overlay_variables.update(overlay_vars)

                # Process templates in overlay
                try:
                    processed_overlay = template_engine.process_overlay_data(
                        overlay_data, overlay_variables
                    )
                except ValueError as e:
                    cli_utils.print_error(
                        f"Template processing failed for {overlay_path_str}: {e}"
                    )
                    continue

                # Apply overlay
                try:
                    modified_doc = apply_overlay(modified_doc, processed_overlay)
                    overlays_applied += 1
                    if verbose:
                        cli_utils.print_success(f"Applied overlay: {overlay_path_str}")
                except Exception as e:
                    cli_utils.print_error(
                        f"Failed to apply overlay {overlay_path_str}: {e}"
                    )
                    continue

                if verbose:
                    progress.update(task, advance=1)

        # Save or display result
        if not dry_run:
            save_file(modified_doc, output)
            cli_utils.print_success(f"Modified OpenAPI document saved to: {output}")
        else:
            cli_utils.print_info("Dry run completed - no files were modified")
            if output_format == "yaml":
                yaml.Dumper.ignore_aliases = lambda *args: True
                click.echo(
                    yaml.dump(modified_doc, sort_keys=False, default_flow_style=False)
                )
            else:
                click.echo(json.dumps(modified_doc, indent=2))

        # Print summary
        if verbose:
            cli_utils.print_overlay_application_summary(
                openapi_file, output, bundle_name, overlays_applied
            )

    except KeyboardInterrupt:
        cli_utils.print_info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        cli_utils.print_error(f"Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


@bundle.command("validate")
@click.argument(
    "bundle_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def bundle_validate(bundle_file):
    """Validate bundle configuration and overlay files.

    BUNDLE_FILE: Path to the bundle configuration file (e.g., bundle.yaml)
    """
    require_enhanced_features()

    try:
        cli_utils.print_info(f"Validating bundle file: {bundle_file}")

        # Load bundle configuration
        try:
            bundle_config = load_file(str(bundle_file))
        except Exception as e:
            cli_utils.print_error(f"Failed to load bundle.yaml: {e}")
            sys.exit(1)

        bundle_name = bundle_config.get("name", "unknown")
        cli_utils.print_info(f"Validating bundle: {bundle_name}")

        # Validate bundle structure
        validation_errors = []
        validation_warnings = []

        # Check required fields
        required_fields = ["name", "overlays"]
        for field in required_fields:
            if field not in bundle_config:
                validation_errors.append(f"Missing required field: {field}")

        # Validate overlays
        overlays = bundle_config.get("overlays", [])
        if not isinstance(overlays, list):
            validation_errors.append("'overlays' must be a list")
        else:
            for i, overlay in enumerate(overlays):
                if not isinstance(overlay, dict):
                    validation_errors.append(f"Overlay {i} must be an object")
                    continue

                if "path" not in overlay:
                    validation_errors.append(
                        f"Overlay {i} missing required 'path' field"
                    )
                    continue

                # Check if overlay file exists (resolve relative to bundle file)
                if Path(overlay["path"]).is_absolute():
                    overlay_path = Path(overlay["path"])
                else:
                    overlay_path = bundle_file.parent / overlay["path"]

                if not overlay_path.exists():
                    validation_errors.append(
                        f"Overlay file not found: {overlay['path']}"
                    )
                else:
                    # Try to load and validate the overlay file
                    try:
                        overlay_data = load_file(str(overlay_path))
                        if "overlay" not in overlay_data:
                            validation_warnings.append(
                                f"Overlay {overlay['path']} missing 'overlay' version field"
                            )
                    except Exception as e:
                        validation_errors.append(
                            f"Failed to load overlay {overlay['path']}: {e}"
                        )

        # Create validation result
        validation_result = {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "warnings": validation_warnings,
        }

        cli_utils.print_validation_results(validation_result, f"Bundle '{bundle_name}'")

        if not validation_result["valid"]:
            sys.exit(1)

    except Exception as e:
        cli_utils.print_error(f"Validation failed: {e}")
        sys.exit(1)


@bundle.command()
@click.option("--force", is_flag=True, help="Overwrite existing files")
def init(force):
    """Create example overlay bundle in current directory."""
    require_enhanced_features()

    try:
        current_path = Path(".")
        overlays_path = current_path / "overlays"
        bundle_name = "example-bundle"

        # Check if files already exist
        bundle_file = current_path / "bundle.yaml"
        overlay1_file = overlays_path / "add-version.yaml"
        overlay2_file = overlays_path / "add-server.yaml"

        existing_files = []
        if bundle_file.exists():
            existing_files.append("bundle.yaml")
        if overlay1_file.exists():
            existing_files.append("overlays/add-version.yaml")
        if overlay2_file.exists():
            existing_files.append("overlays/add-server.yaml")

        if existing_files and not force:
            if not cli_utils.confirm_action(
                f"Files {', '.join(existing_files)} already exist. Continue?"
            ):
                cli_utils.print_info("Initialization cancelled")
                return

        # Create overlays directory if it doesn't exist
        overlays_path.mkdir(exist_ok=True)

        cli_utils.print_info("Creating example bundle files in current directory")

        # Create example bundle configuration
        bundle_config = {
            "name": bundle_name,
            "description": "Example overlay bundle configuration",
            "version": "1.0.0",
            "variables": {"api_version": "v1", "base_url": "https://api.example.com"},
            "overlays": [
                {
                    "path": "overlays/add-version.yaml",
                    "description": "Add API version to info section",
                },
                {
                    "path": "overlays/add-server.yaml",
                    "description": "Add server configuration",
                    "variables": {"server_description": "Example API Server"},
                },
            ],
        }

        with open(bundle_file, "w") as f:
            yaml.dump(bundle_config, f, sort_keys=False, default_flow_style=False)

        # Create example overlays
        version_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Example API Bundle", "version": "{{ api_version }}"},
            "actions": [
                {"target": "$.info", "update": {"x-api-version": "{{ api_version }}"}}
            ],
        }

        with open(overlay1_file, "w") as f:
            yaml.dump(version_overlay, f, sort_keys=False, default_flow_style=False)

        server_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Example Server Configuration"},
            "actions": [
                {
                    "target": "$",
                    "update": {
                        "servers": [
                            {
                                "url": "{{ base_url }}",
                                "description": "{{ server_description }}",
                            }
                        ]
                    },
                }
            ],
        }

        with open(overlay2_file, "w") as f:
            yaml.dump(server_overlay, f, sort_keys=False, default_flow_style=False)

        cli_utils.print_success("Example bundle created successfully!")
        cli_utils.print_info("Created files:")
        cli_utils.print_info("  - bundle.yaml (bundle configuration)")
        cli_utils.print_info("  - overlays/add-version.yaml (version overlay)")
        cli_utils.print_info("  - overlays/add-server.yaml (server overlay)")
        cli_utils.print_info("")
        cli_utils.print_info("Try the following commands:")
        cli_utils.print_info("  oas-patch bundle validate bundle.yaml")
        cli_utils.print_info("  oas-patch bundle apply your-openapi.yaml bundle.yaml")

    except Exception as e:
        cli_utils.print_error(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
