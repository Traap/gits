from typing import Optional

import typer
from gits.utils.cli import options, run
from gits.utils.operations import clone_repo


def clone(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Clone repositories listed in the YAML file."""
    opts = options(ctx, repo_group, verbose, dry_run)
    run(opts, lambda repo: clone_repo(repo, opts.dry_run), workers=4, include_unlisted=False, always=True)
