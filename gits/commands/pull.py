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
            if verbose:
                typer.echo(f"   {ICONS.PULL} Not pulled: {alias}")
            return

        if dry_run:
            typer.echo(f"   {ICONS.PULL} (dry-run) {alias}: would stash and pull")
            return

        try:
            if verbose:
                subprocess.run(["git", "-C", "-v", str(path), "stash"], check=True)
            else:
                subprocess.run(["git", "-C", "-q", str(path), "stash"], check=True)

            if verbose:
                subprocess.run(["git", "-C", "-v", str(path), "pull"], check=True)
            else:
                subprocess.run(["git", "-C", "-q", str(path), "pull"], check=True)

            if verbose:
                typer.echo(f"   {ICONS.PULL} Pulled: {alias}")
        except subprocess.CalledProcessError:
            if verbose:
                typer.echo(f"{ICONS.ERROR} Pull failed: {alias}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        check_group = ""
        for group_name, repo in filtered_repos(repo_group):
            if group_name != check_group:
                check_group = group_name
                if verbose or dry_run:
                    typer.echo(f"{ICONS.GROUP} {group_name}")
            executor.submit(pull_repo, group_name, repo)

