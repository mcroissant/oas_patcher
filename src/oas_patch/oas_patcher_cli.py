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


@cli.command()
@click.argument("openapi_file")
@click.argument("bundle_name")
@click.option(
    "--output", "-o", help="Output file path (auto-generated if not specified)"
)
@click.option("--env", "-e", help="Environment name to use")
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
@click.option(
    "--format", "-f", type=click.Choice(["yaml", "json"]), help="Output format"
)
@click.option("--var", multiple=True, help="Variables in key=value format (repeatable)")
@click.option("--dry-run", is_flag=True, help="Preview changes without saving")
@click.option(
    "--verbose", "-v", is_flag=True, help="Verbose output with progress indicators"
)
def apply(
    openapi_file, bundle_name, output, env, config, format, var, dry_run, verbose
):
    """
    Apply overlay bundle to OpenAPI document.

    OPENAPI_FILE: Path to the OpenAPI document (YAML/JSON)
    BUNDLE_NAME: Name of the overlay bundle to apply
    """
    require_enhanced_features()

    try:
        # Initialize managers
        bundle_manager = BundleManager(config)
        env_manager = EnvironmentManager(config)
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

        # Load bundle configuration
        if verbose:
            cli_utils.print_info(f"Loading bundle configuration: {bundle_name}")

        try:
            bundle_config = bundle_manager.load_bundle(bundle_name)
        except (FileNotFoundError, ValueError) as e:
            cli_utils.print_error(f"Failed to load bundle: {e}")
            sys.exit(1)

        # Get environment-specific overlays
        if env:
            overlays = bundle_manager.get_overlays_for_environment(bundle_name, env)
            if verbose:
                cli_utils.print_info(f"Using environment: {env}")
                cli_utils.print_info(f"Found {len(overlays)} overlays for environment")
        else:
            overlays = bundle_config.overlays
            if verbose:
                cli_utils.print_info(f"Using all overlays ({len(overlays)})")

        if not overlays:
            cli_utils.print_warning("No overlays found for specified environment")
            return

        # Get merged variables
        variables = env_manager.get_variables(env, cli_variables)
        # Add bundle variables
        bundle_vars = bundle_config.variables or {}
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
                    cli_utils.print_info(f"Processing overlay: {overlay_config.path}")

                # Load overlay file
                overlay_path = bundle_manager._resolve_overlay_path(
                    bundle_name, overlay_config.path
                )
                try:
                    overlay_data = load_file(str(overlay_path))
                except (FileNotFoundError, ValueError) as e:
                    cli_utils.print_error(
                        f"Failed to load overlay {overlay_config.path}: {e}"
                    )
                    continue

                # Merge overlay variables
                overlay_variables = variables.copy()
                if overlay_config.variables:
                    overlay_variables.update(overlay_config.variables)

                # Process templates in overlay
                try:
                    processed_overlay = template_engine.process_overlay_data(
                        overlay_data, overlay_variables
                    )
                except ValueError as e:
                    cli_utils.print_error(
                        f"Template processing failed for {overlay_config.path}: {e}"
                    )
                    continue

                # Apply overlay
                try:
                    modified_doc = apply_overlay(modified_doc, processed_overlay)
                    overlays_applied += 1
                    if verbose:
                        cli_utils.print_success(
                            f"Applied overlay: {overlay_config.path}"
                        )
                except Exception as e:
                    cli_utils.print_error(
                        f"Failed to apply overlay {overlay_config.path}: {e}"
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


@cli.command("list-bundles")
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_bundles(config, verbose):
    """List all available overlay bundles."""
    require_enhanced_features()

    try:
        bundle_manager = BundleManager(config)
        bundle_names = bundle_manager.discover_bundles()

        if not bundle_names:
            cli_utils.print_info(f"No bundles found in {config}")
            return

        if verbose:
            # Get detailed info for each bundle
            bundles_info = []
            for bundle_name in bundle_names:
                try:
                    bundle_info = bundle_manager.get_bundle_info(bundle_name)
                    bundles_info.append(bundle_info)
                except Exception as e:
                    bundles_info.append(
                        {
                            "name": bundle_name,
                            "description": f"Error loading bundle: {e}",
                            "overlays": [],
                            "validation": {
                                "valid": False,
                                "errors": [str(e)],
                                "warnings": [],
                            },
                        }
                    )

            table = cli_utils.create_bundles_table(bundles_info)
            cli_utils.console.print(table)
        else:
            cli_utils.print_header("Available Bundles")
            for bundle_name in bundle_names:
                cli_utils.print_info(f"  {bundle_name}")

    except Exception as e:
        cli_utils.print_error(f"Failed to list bundles: {e}")
        sys.exit(1)


@cli.command("list-environments")
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list_environments(config, verbose):
    """List all available environments."""
    require_enhanced_features()

    try:
        env_manager = EnvironmentManager(config)

        if verbose:
            environments_info = env_manager.list_environments_info()

            if not environments_info:
                cli_utils.print_info(f"No environments found in {config}")
                return

            table = cli_utils.create_environments_table(environments_info)
            cli_utils.console.print(table)
        else:
            env_names = env_manager.discover_environments()

            if not env_names:
                cli_utils.print_info(f"No environments found in {config}")
                return

            cli_utils.print_header("Available Environments")
            for env_name in env_names:
                cli_utils.print_info(f"  {env_name}")

    except Exception as e:
        cli_utils.print_error(f"Failed to list environments: {e}")
        sys.exit(1)


@cli.command("bundle-validate")
@click.argument("bundle_name")
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
def bundle_validate(bundle_name, config):
    """Validate bundle configuration and overlay files."""
    require_enhanced_features()

    try:
        bundle_manager = BundleManager(config)

        cli_utils.print_info(f"Validating bundle: {bundle_name}")

        validation_result = bundle_manager.validate_bundle(bundle_name)
        cli_utils.print_validation_results(validation_result, f"Bundle '{bundle_name}'")

        if not validation_result["valid"]:
            sys.exit(1)

    except Exception as e:
        cli_utils.print_error(f"Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("bundle_name")
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
def info(bundle_name, config):
    """Show detailed information about a bundle."""
    require_enhanced_features()

    try:
        bundle_manager = BundleManager(config)

        bundle_info = bundle_manager.get_bundle_info(bundle_name)
        panel = cli_utils.create_bundle_info_panel(bundle_info)
        cli_utils.console.print(panel)

    except Exception as e:
        cli_utils.print_error(f"Failed to get bundle info: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    default="overlays",
    help="Configuration directory (default: overlays)",
)
@click.option("--force", is_flag=True, help="Overwrite existing configurations")
def init(config, force):
    """Create example overlay configuration."""
    require_enhanced_features()

    try:
        config_path = Path(config)

        if config_path.exists() and not force:
            if not cli_utils.confirm_action(
                f"Configuration directory '{config}' already exists. Continue?"
            ):
                cli_utils.print_info("Initialization cancelled")
                return

        # Create directory structure
        config_path.mkdir(exist_ok=True)
        (config_path / "environments").mkdir(exist_ok=True)
        (config_path / "example-bundle").mkdir(exist_ok=True)

        cli_utils.print_info(f"Creating configuration structure in {config}")

        # Create example bundle configuration
        bundle_config = {
            "name": "example-bundle",
            "description": "Example overlay bundle configuration",
            "version": "1.0.0",
            "variables": {"api_version": "v1", "base_url": "https://api.example.com"},
            "overlays": [
                {
                    "path": "add-version.yaml",
                    "description": "Add API version to info section",
                    "environment": ["staging", "production"],
                },
                {
                    "path": "add-server.yaml",
                    "description": "Add server configuration",
                    "variables": {"server_description": "Example API Server"},
                },
            ],
        }

        with open(config_path / "example-bundle" / "bundle.yaml", "w") as f:
            yaml.dump(bundle_config, f, sort_keys=False, default_flow_style=False)

        # Create example overlays
        version_overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Example API Bundle", "version": "{{ api_version }}"},
            "actions": [
                {"target": "$.info", "update": {"x-api-version": "{{ api_version }}"}}
            ],
        }

        with open(config_path / "example-bundle" / "add-version.yaml", "w") as f:
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

        with open(config_path / "example-bundle" / "add-server.yaml", "w") as f:
            yaml.dump(server_overlay, f, sort_keys=False, default_flow_style=False)

        # Create example environments
        staging_env = {
            "name": "staging",
            "description": "Staging environment configuration",
            "variables": {
                "base_url": "https://staging-api.example.com",
                "api_version": "v1-staging",
                "server_description": "Staging API Server",
            },
        }

        with open(config_path / "environments" / "staging.yaml", "w") as f:
            yaml.dump(staging_env, f, sort_keys=False, default_flow_style=False)

        production_env = {
            "name": "production",
            "description": "Production environment configuration",
            "variables": {
                "base_url": "https://api.example.com",
                "api_version": "v1",
                "server_description": "Production API Server",
            },
        }

        with open(config_path / "environments" / "production.yaml", "w") as f:
            yaml.dump(production_env, f, sort_keys=False, default_flow_style=False)

        cli_utils.print_success("Example configuration created successfully!")
        cli_utils.print_info("Try the following commands:")
        cli_utils.print_info(f"  oas-patch list-bundles --config {config}")
        cli_utils.print_info(f"  oas-patch list-environments --config {config}")
        cli_utils.print_info(f"  oas-patch info example-bundle --config {config}")
        cli_utils.print_info(
            f"  oas-patch bundle-validate example-bundle --config {config}"
        )

    except Exception as e:
        cli_utils.print_error(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
