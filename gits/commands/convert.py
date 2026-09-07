from typing import Optional

import typer
from gits.utils.cli import options, run
from gits.utils.operations import convert_repo


def convert(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Convert UTF-16 files to UTF-8 in listed repositories."""
    opts = options(ctx, repo_group, verbose, dry_run)
    run(opts, lambda repo: convert_repo(repo, opts.dry_run), workers=4, include_unlisted=False, always=False)
