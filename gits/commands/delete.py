import os
import shutil
from pathlib import Path
from typing import Optional

import typer

import gits.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos
from gits.config_loader import load_repos


def delete(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Delete repositories listed in YAML that are not protected by do_not_delete."""
    repos = load_repos()
    repo_lookup = {}
    root_dirs = set()

    for group in repos:
        group_name = group["group_name"]
        if repo_group and group_name != repo_group:
            continue

        for repo in group["repositories"]:
            alias = repo["alias"]
            target_path = get_repo_path(group_name, alias, repo.get("target_path"))
            repo_lookup[str(target_path)] = repo
            root_dirs.add(str(target_path.parent))

    deleted = []

    for path_str, repo in repo_lookup.items():
        if not os.path.exists(path_str):
            continue

        do_not_delete = repo.get("do_not_delete", False)
        reason = "do_not_delete = true" if do_not_delete else "listed"
        allow_delete = not do_not_delete

        if allow_delete:
            if dry_run:
                typer.echo(f"{ICONS.DELETE} (dry-run) would remove: {path_str}")
            else:
                shutil.rmtree(path_str)
                typer.echo(f"{ICONS.DELETE} Removed: {path_str}")
            deleted.append(path_str)
        else:
            if verbose:
                typer.echo(f"{ICONS.INFO} Skipped {path_str} ({reason})")

    # Cleanup empty root directories
    for root in root_dirs:
        if os.path.exists(root) and not os.listdir(root):
            if dry_run:
                typer.echo(f"{ICONS.DELETE} (dry-run) would remove empty directory: {root}")
            else:
                os.rmdir(root)
                typer.echo(f"{ICONS.DELETE} Removed empty directory: {root}")

    if not deleted:
        typer.echo(f"{ICONS.INFO} No repositories deleted.")

