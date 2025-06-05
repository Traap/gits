from pathlib import Path
import shutil
import sys
import platform
from typing import Optional
import typer

from gits.config_loader import CONFIG_FILE

import gits.icons as ICONS
from gits.utils.repos import filtered_repos

def doctor(
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group.")
):
    """Run environment and configuration checks for gits."""
    typer.echo(f"{ICONS.DOC} Running system diagnostics...\n")

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        typer.echo(f"{ICONS.SUCCESS} Python >= 3.8: {platform.python_version()}")
    else:
        typer.echo(f"{ICONS.ERROR} Python >= 3.8 required. Found: {platform.python_version()}")

    # Check if git is installed
    if shutil.which("git"):
        typer.echo(f"{ICONS.SUCCESS} git found in PATH")
    else:
        typer.echo(f"{ICONS.ERROR} git not found in PATH")

    # Check config file
    if CONFIG_FILE.exists():
        typer.echo(f"{ICONS.SUCCESS} {CONFIG_FILE} found")
    else:
        typer.echo(f"{ICONS.ERROR} {CONFIG_FILE} missing")

    # Load and check filtered repos
    try:
        groups = list(filtered_repos(repo_group))
        typer.echo(f"{ICONS.SUCCESS} Loaded {len(groups)} repository definitions" + (f" for group '{repo_group}'" if repo_group else ""))
    except Exception as e:
        typer.echo(f"{ICONS.ERROR} Failed to parse repository config: {e}")
        return

    # Check each repo
    for group_name, repo in groups:
        alias = repo["alias"]
        if not repo.get("target_path"):
            typer.echo(f"{ICONS.WARNING} {alias}: missing target_path (will default to group name)")
        path = Path(repo.get("target_path") or Path.home() / group_name / alias)
        if not path.parent.exists():
            typer.echo(f"{ICONS.WARNING} {alias}: target directory parent does not exist → {path.parent}")

    typer.echo(f"\n{ICONS.DOC} Diagnostics complete.")
