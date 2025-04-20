"""Module providing the general CLI parameters of the oas patcher."""

import argparse
import json
import sys
import yaml
from oas_patch.file_utils import load_file, save_file
from oas_patch.overlay import apply_overlay
from oas_patch.validator import validate
from oas_patch.overlay_diff import create_overlay


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='A tool to apply overlays to OpenAPI documents.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(title='subcommands', dest='command', required=True)

    # Subcommand: overlay
    overlay_parser = subparsers.add_parser(
        'overlay',
        help='Apply an OpenAPI Overlay to your OpenAPI document.'
    )
    overlay_parser.add_argument('openapi', help='Path to the OpenAPI description (YAML/JSON).')
    overlay_parser.add_argument('overlay', help='Path to the Overlay document (YAML/JSON).')
    overlay_parser.add_argument('-o', '--output', required=False, help='Path to save the modified OpenAPI document. Defaults to stdout.')
    overlay_parser.add_argument('--sanitize', action='store_true', help='Remove special characters from the OpenAPI document.')

    # Subcommand: diff
    diff_parser = subparsers.add_parser(
        'diff',
        help='Generate an OpenAPI Overlay from the differences between two OpenAPI documents.'
    )
    diff_parser.add_argument('original', help='Path to the source OpenAPI document (YAML/JSON).')
    diff_parser.add_argument('modified', help='Path to the target OpenAPI document (YAML/JSON).')
    diff_parser.add_argument('-o', '--output', help='Path to save the generated OpenAPI Overlay.')

    # Subcommand: validate
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate an OpenAPI Overlay document against the specification.'
    )
    validate_parser.add_argument("overlay", type=str, help="Path to the document to validate (YAML/JSON).")
    validate_parser.add_argument("--format", type=str, choices=["sh", "log", "yaml"], default="sh",
                                 help="Output format for validation results (shell, log or yaml).")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def handle_validate(args):
    """Handle the 'validate' subcommand."""

    try:
        overlay_doc = load_file(args.overlay)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    try:
        output = validate(overlay_doc, args.format)
        print(output)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: Unable to load the document. {e}")
        sys.exit(1)


def handle_overlay(args):
    try:
        openapi_doc = load_file(args.openapi, args.sanitize)
        overlay = load_file(args.overlay)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    modified_doc = apply_overlay(openapi_doc, overlay)

    if args.output:
        save_file(modified_doc, args.output)
        print(f'Modified OpenAPI document saved to {args.output}')
    else:
        if args.openapi.endswith(('.yaml', '.yml')):
            yaml.Dumper.ignore_aliases = lambda *args: True
            print(yaml.dump(modified_doc, sort_keys=False, default_flow_style=False))
        elif args.openapi.endswith('.json'):
            print(json.dumps(modified_doc, indent=2))


def handle_diff(args):
    # Load input files
    try:
        original = load_file(args.original)
        modified = load_file(args.modified)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Apply overlay
    overlay_doc = create_overlay(original, modified)

    if args.output:
        # Save the result to the specified file
        save_file(overlay_doc, args.output)
        print(f'Modified OpenAPI document saved to {args.output}')
    else:
        # Output the result to the console
        if args.original.endswith(('.yaml', '.yml')):
            yaml.Dumper.ignore_aliases = lambda *args: True
            print(yaml.dump(overlay_doc, sort_keys=False, default_flow_style=False))
        elif args.original.endswith('.json'):
            print(json.dumps(overlay_doc, indent=2))


def cli():
    """Command-line interface entry point."""
    args = parse_arguments()
    if args.command == 'overlay':
        handle_overlay(args)
    elif args.command == 'validate':
        handle_validate(args)
    elif args.command == 'diff':
        handle_diff(args)
