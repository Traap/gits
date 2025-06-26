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
    check_group = ""
    any_output = False

    for group_name, repo in filtered_repos(repo_group):
        if repo.get("unlisted", False):
            continue

        if group_name != check_group:
           check_group = group_name
           if verbose:
              typer.echo(f"{ICONS.GROUP} {group_name}")

        any_output = False

        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        # Skip directories that are not initialized Git repositories
        if not (path / ".git").exists():
            continue

        if not path.exists():
            if verbose:
                typer.echo(f"   {ICONS.WARNING} Not cloned: {alias}")
            any_output = True
            continue

        if dry_run:
            typer.echo(f"{ICONS.CLEAN} (dry-run) would clean {alias} at {path}")
            continue

        try:
            reset = subprocess.run(
                ["git", "-C", str(path), "reset", "--hard"],
                capture_output=True,
                text=True,
                check=True,
            )

            clean = subprocess.run(
                ["git", "-C", str(path), "clean", "-ffdx" ],
                capture_output=True,
                text=True,
                check=True,
            )

            if verbose:
                output = reset.stdout.rstrip() + "\n" + clean.stdout.rstrip()
                if output:
                    output = "\n".join(f"\t\t\t{line}" for line in output.splitlines())
                    typer.echo(f"   {ICONS.CLEAN} Modified: {alias}\n{output}")
                else:
                    typer.echo(f"   {ICONS.INFO} Clean: {alias}")

            any_output = True
        except subprocess.CalledProcessError:
            if verbose:
                typer.echo(f"   {ICONS.ERROR} {alias}: is not a git repository")
            any_output = True

    if not any_output:
        typer.echo(f"   {ICONS.INFO} All repositories are clean.")

