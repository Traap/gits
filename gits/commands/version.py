import typer

from gits import __version__


def version():
    """Print the gits version."""
    typer.echo(f"v{__version__}")
