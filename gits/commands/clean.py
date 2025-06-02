from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos

def clean(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Clean listed repositories by resetting and removing untracked files, including subfolders."""
    def clean_repo(group_name, repo):
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            typer.echo(f"{ICONS.CLEAN} {alias}: not cloned")
            return

        if dry_run:
            typer.echo(f"{ICONS.CLEAN} (dry-run) would clean {alias} at {path}")
            return

        try:
            subprocess.run(["git", "-C", str(path), "reset", "--hard"], check=True)
            subprocess.run(["git", "-C", str(path), "clean", "-fdx"], check=True)
            typer.echo(f"{ICONS.CLEAN} {alias}: cleaned successfully")
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to clean")

    with ThreadPoolExecutor(max_workers=4) as executor:
        for group_name, repo in filtered_repos(repo_group):
            executor.submit(clean_repo, group_name, repo)
