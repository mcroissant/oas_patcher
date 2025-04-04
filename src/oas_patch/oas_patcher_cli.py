"""Module providing the general CLI parameters of the oas patcher."""

import argparse
import json
import sys
import yaml
from oas_patch.file_utils import load_file, save_file
from oas_patch.overlay import apply_overlay


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

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def handle_overlay(args):
    # Load input files
    try:
        openapi_doc = load_file(args.openapi, args.sanitize)
        overlay = load_file(args.overlay)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Apply overlay
    modified_doc = apply_overlay(openapi_doc, overlay)

    if args.output:
        # Save the result to the specified file
        save_file(modified_doc, args.output)
        print(f'Modified OpenAPI document saved to {args.output}')
    else:
        # Output the result to the console
        if args.openapi.endswith(('.yaml', '.yml')):
            yaml.Dumper.ignore_aliases = lambda *args: True
            print(yaml.dump(modified_doc, sort_keys=False, default_flow_style=False))
        elif args.openapi.endswith('.json'):
            print(json.dumps(modified_doc, indent=2))


def cli():
    """Command-line interface entry point."""
    args = parse_arguments()
    if args.command == 'overlay':
        handle_overlay(args)
