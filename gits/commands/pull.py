from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos


def pull(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Pull changes for all repositories including unlisted ones."""
    def pull_repo(group_name, repo):
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            typer.echo(f"{ICONS.PULL} {alias}: not cloned")
            return

        if dry_run:
            typer.echo(f"{ICONS.PULL} (dry-run) {alias}: would stash and pull")
            return

        try:
            subprocess.run(["git", "-C", str(path), "stash"], check=True)
            subprocess.run(["git", "-C", str(path), "pull"], check=True)
            typer.echo(f"{ICONS.PULL} {alias}: pulled successfully")
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to pull")

    with ThreadPoolExecutor(max_workers=4) as executor:
        for group_name, repo in filtered_repos(repo_group):
            executor.submit(pull_repo, group_name, repo)

