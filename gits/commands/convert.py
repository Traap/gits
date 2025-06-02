from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos

def convert(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Convert UTF-16 files to UTF-8 in all repositories."""
    def convert_repo(group_name, repo):
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            typer.echo(f"{ICONS.CONVERT} {alias}: not cloned")
            return

        for file in path.rglob("*.sql"):
            try:
                with open(file, "r", encoding="utf-16") as f:
                    content = f.read()
                if dry_run:
                    typer.echo(f"{ICONS.CONVERT} (dry-run) would convert {file}")
                    continue
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
                typer.echo(f"{ICONS.CONVERT} Converted: {file}")
            except UnicodeError:
                continue

    with ThreadPoolExecutor(max_workers=4) as executor:
        for group_name, repo in filtered_repos(repo_group):
            executor.submit(convert_repo, group_name, repo)
