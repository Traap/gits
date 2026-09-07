import platform
import shutil
import sys
from typing import Optional

import typer
from gits.utils.cli import configured, options
from gits.utils.config_loader import CONFIG_FILE
from gits.utils.repos import selected_groups


def doctor(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r"),
):
    """Run environment and configuration checks for gits."""
    opts = options(ctx, repo_group)
    typer.echo(f"Python: {platform.python_version()}")
    git_found = shutil.which("git") is not None
    typer.echo(f"Git: {'found' if git_found else 'missing'}")
    typer.echo(f"Configuration: {CONFIG_FILE}")
    for group in configured(lambda: selected_groups(opts.repo_group)):
        typer.echo(f"Group: {group.name} ({group.root})")
        for repo in group.repositories:
            state = "found" if (repo.path / ".git").exists() else "not cloned"
            typer.echo(f"   {repo.alias}: {repo.path} ({state})")
    if not git_found or sys.version_info < (3, 8):
        raise typer.Exit(1)
