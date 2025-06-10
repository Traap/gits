import os
import shutil
from pathlib import Path
from typing import Optional

import typer

import gits.icons as ICONS
from gits.utils.repos import get_repo_path
from gits.config_loader import load_repos

def delete(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Delete repositories listed in YAML that are not protected by do_not_delete."""
    repos = load_repos()
    deleted = []

    for group in repos:
        group_name = group["group_name"]
        if repo_group and group_name != repo_group:
            continue

        typer.echo(f"{ICONS.GROUP} {group_name}")

        for repo in group["repositories"]:
            alias = repo["alias"]

            do_not_delete = repo.get("do_not_delete", False)
            target_path = get_repo_path(group_name, alias, repo.get("target_path"))

            if not target_path.exists():
                continue

            if repo.get("unlisted", False):
                if verbose:
                    typer.echo(f"   {ICONS.INFO} Skipped: {alias} -> {target_path} -> unlisted")
                continue


            if do_not_delete:
                if verbose:
                    typer.echo(f"   {ICONS.INFO} Skipped {alias} (do_not_delete = true)")
                continue

            if dry_run:
                if verbose:
                    typer.echo(f"   {ICONS.DELETE} (dry-run) would remove: {alias} -> {target_path}")
                else:
                    typer.echo(f"   {ICONS.DELETE} (dry-run) would remove: {alias}")
            else:
                shutil.rmtree(target_path)
                if verbose:
                    typer.echo(f"   {ICONS.DELETE} Deleted: {alias} -> {target_path}")
                else:
                    typer.echo(f"   {ICONS.DELETE} Deleted: {alias}")
                deleted.append(alias)

        # Check and remove the group root directory if now empty
        group_root = get_repo_path(group_name, "", None)
        if group_root.exists() and not any(group_root.iterdir()):
            if dry_run:
                if verbose:
                    typer.echo(f"   {ICONS.DELETE} (dry-run) would remove: {group_name} -> {group_root}")
                else:
                    typer.echo(f"   {ICONS.DELETE} (dry-run) would remove: {group_name}")
            else:
                os.rmdir(group_root)
                if verbose:
                    typer.echo(f"   {ICONS.DELETE} Deleted: {group_name} -> {group_root}")
                else:
                    typer.echo(f"   {ICONS.DELETE} Deleted: {group_name}")
        else:
            typer.echo(f"   {ICONS.WARNING} Not Empty: {group_name} -> {group_root}")

    if not deleted and verbose:
        typer.echo(f"   {ICONS.INFO} No repositories deleted.")

