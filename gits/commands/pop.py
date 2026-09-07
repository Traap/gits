from typing import Optional

import typer
from gits.utils.cli import options, run
from gits.utils.operations import git_operation


def pop(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Pop the latest stash in each listed repository."""
    opts = options(ctx, repo_group, verbose, dry_run)
    run(opts, lambda repo: git_operation(repo, [["stash", "pop"]], opts.dry_run, True), workers=1, include_unlisted=False, always=False)
