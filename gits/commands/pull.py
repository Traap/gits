from typing import Optional

import typer
from gits.utils.cli import options, run
from gits.utils.operations import git_operation


def pull(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Stash and pull changes in configured and discovered repositories."""
    opts = options(ctx, repo_group, verbose, dry_run)
    run(opts, lambda repo: git_operation(repo, [["stash"], ["pull"]], opts.dry_run, True), workers=4, include_unlisted=True, always=False)
