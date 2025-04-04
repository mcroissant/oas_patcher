"""Module providing the general cli parameters of the oas patcher"""

import argparse
import json
import sys
import yaml
from file_utils import load_file, save_file
from overlay import apply_overlay


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Apply an OpenAPI Overlay to your OpenAPI document.',
        epilog='Example usage:\n'
               'oas-patcher --openapi openapi.yaml --overlay overlay.yaml\
                   --output modified_openapi.yaml --sanitize',
        formatter_class=argparse.RawTextHelpFormatter
    )

    required_group = parser.add_argument_group('Required arguments')
    required_group.add_argument('--openapi', required=True, help='Path to the OpenAPI description (YAML/JSON).')
    required_group.add_argument('--overlay', required=True, help='Path to the Overlay document (YAML/JSON).')

    optional_group = parser.add_argument_group('Optional arguments')
    optional_group.add_argument('--output', required=False, help='Path to save the modified OpenAPI document. Defaults to stdout.')
    optional_group.add_argument('--sanitize', action='store_true', help='Remove special characters from the OpenAPI document.')
    return parser.parse_args()


def cli():
    """Command-line interface entry point."""
    args = parse_arguments()

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
