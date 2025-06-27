from typing import Optional

import typer
import gits.ui.icons as ICONS

from gits.utils.config_loader import load_repos

def list(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="List repositories instead of just groups."),
):
    """List repository groups and optionally their repositories."""
    repos = load_repos()
    for group in repos:
        group_name = group["group_name"]
        if repo_group and group_name != repo_group:
            continue

        typer.echo(f"{ICONS.GROUP} {group_name}")

        if verbose:
            for repo in group["repositories"]:
                if not isinstance(repo, dict) or "alias" not in repo or "url" not in repo:
                    continue
                alias = repo["alias"]
                url = repo["url"]
                typer.echo(f"   {ICONS.REPO} {alias} -> {url}")
