"""Command-line interface for Superset Toolkit."""

import sys
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.traceback import install
    
    # Install rich traceback handler
    install(show_locals=True)
    
    app = typer.Typer(
        name="superset-toolkit",
        help="Professional toolkit for Superset API automation",
        add_completion=False,
    )
    console = Console()
    
    CLI_AVAILABLE = True
    
except ImportError:
    CLI_AVAILABLE = False
    app = None
    console = None

from .client import SupersetClient
from .exceptions import SupersetToolkitError


def _handle_error(error: Exception) -> None:
    """Handle and display errors appropriately."""
    if CLI_AVAILABLE and console:
        if isinstance(error, SupersetToolkitError):
            console.print(f"[red]Error:[/red] {error}")
        else:
            console.print(f"[red]Unexpected error:[/red] {error}")
            console.print_exception()
    else:
        print(f"Error: {error}")
    
    sys.exit(1)


if CLI_AVAILABLE:
    @app.command("test-connection")
    def test_connection_command(
        superset_url: Optional[str] = typer.Option(
            None,
            "--url",
            help="Superset URL (defaults to SUPERSET_URL env var)"
        ),
        username: Optional[str] = typer.Option(
            None,
            "--username",
            help="Username (defaults to SUPERSET_USERNAME env var)"
        ),
        password: Optional[str] = typer.Option(
            None,
            "--password",
            help="Password (defaults to SUPERSET_PASSWORD env var)"
        ),
        schema: Optional[str] = typer.Option(
            None,
            "--schema",
            help="Database schema (defaults to SUPERSET_SCHEMA env var or 'reports')"
        ),
        database_name: Optional[str] = typer.Option(
            None,
            "--database",
            help="Database name (defaults to SUPERSET_DATABASE_NAME env var or 'Trino')"
        ),
    ):
        """Test connection to Superset instance and show configuration."""
        try:
            console.print("[blue]🔗 Testing Superset connection...[/blue]")
            
            # Create config with any overrides
            from .config import Config
            config = Config(
                superset_url=superset_url,
                username=username,
                password=password,
                schema=schema,
                database_name=database_name
            )
            
            # Create client (this will test authentication)
            client = SupersetClient(config=config)
            
            console.print(f"[green]✅ Successfully connected to {client.base_url}[/green]")
            console.print(f"[green]👤 Authenticated as user ID: {client.user_id}[/green]")
            console.print(f"[blue]📊 Using schema: {config.schema}[/blue]")
            console.print(f"[blue]🗄️ Using database: {config.database_name}[/blue]")
            
        except Exception as e:
            _handle_error(e)
    
    @app.command("version")
    def version_command():
        """Show version information."""
        from . import __version__
        console.print(f"superset-toolkit version {__version__}")


def main() -> None:
    """Main CLI entry point."""
    if not CLI_AVAILABLE:
        print("Error: CLI dependencies not installed.")
        print("Install with: pip install superset-toolkit[cli]")
        sys.exit(1)
    
    app()


def simple_main() -> None:
    """Simple entry point without CLI dependencies for programmatic use."""
    try:
        print("🚀 Running Timelapse/Illustration dashboard creation...")
        client = SupersetClient()
        run_timelapse_illustration(client)
        print("✅ Dashboard creation completed successfully!")
    except Exception as e:
        _handle_error(e)


if __name__ == "__main__":
    main()
