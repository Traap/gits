from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos


def status(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Print git status for all repositories."""
    any_output = False

    for group_name, repo in filtered_repos(repo_group):
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            typer.echo(f"{ICONS.STATUS} {alias}: not cloned")
            any_output = True
            continue

        try:
            result = subprocess.run(
                ["git", "-C", str(path), "status", "--short"],
                capture_output=True,
                text=True,
                check=True,
            )
            status_output = result.stdout.strip() or "clean"
            typer.echo(f"{ICONS.STATUS} {alias}: {status_output}")
            any_output = True
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to get status")
            any_output = True

    if not any_output:
        typer.echo(f"{ICONS.INFO} All repositories are clean.")

