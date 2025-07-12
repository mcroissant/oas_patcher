#!/usr/bin/env python3

from click.testing import CliRunner
from oas_patch.oas_patcher_cli import cli

def debug_validate():
    runner = CliRunner()
    
    result = runner.invoke(cli, [
        'validate',
        'tests/samples/invalid_overlay/overlay_noactions.yml',
        '--format',
        'log'
    ])
    
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {repr(result.output)}")
    print(f"Exception: {result.exception}")
    print("=" * 50)
    print("Raw output:")
    print(result.output)

if __name__ == "__main__":
    debug_validate()
