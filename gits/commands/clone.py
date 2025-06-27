from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.ui.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos

def clone(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Clone repositories listed in the YAML file."""
    def clone_repo(group_name, repo):
        alias = repo["alias"]
        url = repo["url"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if path.exists():
            if verbose:
                typer.echo(f"   {ICONS.WARNING} Exists: {alias}")
            return

        if dry_run:
            typer.echo(f"   {ICONS.CLONE} (dry-run) clone {url} {path}")
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if verbose:
                subprocess.run(["git", "clone", "-v", url, str(path)], check=True)
            else:
                subprocess.run(["git", "clone", "-q", url, str(path)], check=True)

            typer.echo(f"   {ICONS.CLONE} Cloned: {alias}")
        except subprocess.CalledProcessError:
            if verbose:
                typer.echo(f"{ICONS.ERROR} Failed: {alias}")

    with ThreadPoolExecutor(max_workers=4) as executor:
        check_group = ""
        for group_name, repo in filtered_repos(repo_group):
            if group_name != check_group:
                check_group = group_name
                typer.echo(f"{ICONS.GROUP} {group_name}")
            executor.submit(clone_repo, group_name, repo)
