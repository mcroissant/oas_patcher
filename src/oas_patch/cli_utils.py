"""Module providing CLI utilities for rich output and user experience."""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text


class CLIUtils:
    """Utilities for enhanced CLI output and user experience."""

    def __init__(self):
        """Initialize CLI utilities with rich console."""
        self.console = Console()

    def print_success(self, message: str):
        """Print success message in green."""
        self.console.print(f"✓ {message}", style="green")

    def print_error(self, message: str):
        """Print error message in red."""
        self.console.print(f"✗ {message}", style="red")

    def print_warning(self, message: str):
        """Print warning message in yellow."""
        self.console.print(f"⚠ {message}", style="yellow")

    def print_info(self, message: str):
        """Print info message in blue."""
        self.console.print(f"ℹ {message}", style="blue")

    def print_header(self, title: str):
        """Print section header."""
        self.console.print(f"\n[bold]{title}[/bold]")
        self.console.print("─" * len(title))

    def create_bundles_table(self, bundles_info: List[Dict[str, Any]]) -> Table:
        """Create a table for displaying bundle information."""
        table = Table(title="Available Overlay Bundles")
        table.add_column("Bundle Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Overlays", justify="right", style="magenta")
        table.add_column("Status", justify="center")

        for bundle_info in bundles_info:
            status = (
                "✓ Valid"
                if bundle_info.get("validation", {}).get("valid", False)
                else "✗ Invalid"
            )
            status_style = (
                "green"
                if bundle_info.get("validation", {}).get("valid", False)
                else "red"
            )

            table.add_row(
                bundle_info.get("name", "Unknown"),
                bundle_info.get("description", "No description"),
                str(len(bundle_info.get("overlays", []))),
                Text(status, style=status_style),
            )

        return table

    def create_environments_table(
        self, environments_info: List[Dict[str, Any]]
    ) -> Table:
        """Create a table for displaying environment information."""
        table = Table(title="Available Environments")
        table.add_column("Environment", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Variables", justify="right", style="magenta")
        table.add_column("Status", justify="center")

        for env_info in environments_info:
            status = (
                "✓ Valid"
                if env_info.get("validation", {}).get("valid", False)
                else "✗ Invalid"
            )
            status_style = (
                "green" if env_info.get("validation", {}).get("valid", False) else "red"
            )

            table.add_row(
                env_info.get("name", "Unknown"),
                env_info.get("description", "No description"),
                str(env_info.get("variable_count", 0)),
                Text(status, style=status_style),
            )

        return table

    def create_bundle_info_panel(self, bundle_info: Dict[str, Any]) -> Panel:
        """Create a panel for detailed bundle information."""
        content_lines = []

        # Basic info
        content_lines.append(f"[bold]Name:[/bold] {bundle_info.get('name', 'Unknown')}")
        content_lines.append(
            f"[bold]Version:[/bold] {bundle_info.get('version', 'Unknown')}"
        )
        content_lines.append(
            f"[bold]Description:[/bold] {bundle_info.get('description', 'No description')}"
        )
        content_lines.append("")

        # Overlays
        overlays = bundle_info.get("overlays", [])
        content_lines.append(f"[bold]Overlays ({len(overlays)}):[/bold]")
        for i, overlay in enumerate(overlays, 1):
            env_info = (
                f" (env: {', '.join(overlay.get('environment', []))})"
                if overlay.get("environment")
                else ""
            )
            content_lines.append(f"  {i}. {overlay.get('path', 'Unknown')}{env_info}")
            if overlay.get("description"):
                content_lines.append(f"     {overlay['description']}")

        # Variables
        variables = bundle_info.get("variables", {})
        if variables:
            content_lines.append("")
            content_lines.append(f"[bold]Bundle Variables ({len(variables)}):[/bold]")
            for key, value in variables.items():
                content_lines.append(f"  • {key}: {value}")

        # Validation
        validation = bundle_info.get("validation", {})
        content_lines.append("")
        valid = validation.get("valid", False)
        status_text = "[green]✓ Valid[/green]" if valid else "[red]✗ Invalid[/red]"
        content_lines.append(f"[bold]Validation:[/bold] {status_text}")

        if validation.get("errors"):
            content_lines.append("  [red]Errors:[/red]")
            for error in validation["errors"]:
                content_lines.append(f"    • {error}")

        if validation.get("warnings"):
            content_lines.append("  [yellow]Warnings:[/yellow]")
            for warning in validation["warnings"]:
                content_lines.append(f"    • {warning}")

        content = "\n".join(content_lines)
        return Panel(
            content,
            title=f"Bundle: {bundle_info.get('name', 'Unknown')}",
            border_style="blue",
        )

    def create_progress_context(self, description: str):
        """Create a progress context manager for long-running operations."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        )

    def print_validation_results(
        self, validation: Dict[str, Any], title: str = "Validation Results"
    ):
        """Print validation results with appropriate styling."""
        valid = validation.get("valid", False)

        if valid:
            self.print_success(f"{title}: Valid")
        else:
            self.print_error(f"{title}: Invalid")

        errors = validation.get("errors", [])
        if errors:
            self.print_header("Errors")
            for error in errors:
                self.print_error(f"  {error}")

        warnings = validation.get("warnings", [])
        if warnings:
            self.print_header("Warnings")
            for warning in warnings:
                self.print_warning(f"  {warning}")

    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation."""
        try:
            response = input(f"{message} (y/N): ").strip().lower()
            return response in ["y", "yes"]
        except KeyboardInterrupt:
            self.print_info("\nOperation cancelled by user")
            return False

    def print_dry_run_header(self):
        """Print dry run mode header."""
        panel = Panel(
            "[yellow]DRY RUN MODE[/yellow]\n"
            "The following changes would be applied, but no files will be modified.",
            title="Preview Mode",
            border_style="yellow",
        )
        self.console.print(panel)

    def print_overlay_application_summary(
        self, input_file: str, output_file: str, bundle_name: str, overlays_applied: int
    ):
        """Print summary of overlay application."""
        content = (
            f"[bold]Input:[/bold] {input_file}\n"
            f"[bold]Output:[/bold] {output_file}\n"
            f"[bold]Bundle:[/bold] {bundle_name}\n"
            f"[bold]Overlays Applied:[/bold] {overlays_applied}"
        )

        panel = Panel(content, title="Operation Summary", border_style="green")
        self.console.print(panel)


# Global CLI utilities instance
cli_utils = CLIUtils()
