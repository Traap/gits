from typing import Optional

import typer
from gits.utils.cli import options, run
from gits.utils.operations import git_operation


def clean(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Clean listed repositories by resetting and removing untracked files."""
    opts = options(ctx, repo_group, verbose, dry_run)
    run(opts, lambda repo: git_operation(repo, [["reset", "--hard"], ["clean", "-ffdx"]], opts.dry_run, True), workers=1, include_unlisted=False, always=False)
