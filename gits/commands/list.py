from typing import Optional

import typer
import gits.ui.icons as ICONS
from gits.utils.cli import configured, options
from gits.utils.repos import selected_groups


def list(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """List repository groups and optionally their repositories."""
    opts = options(ctx, repo_group, verbose)
    for group in configured(lambda: selected_groups(opts.repo_group)):
        typer.echo(f"{ICONS.GROUP} {group.name}")
        if opts.verbose:
            for repo in group.repositories:
                typer.echo(f"   {ICONS.REPO} {repo.alias} -> {repo.url}")
