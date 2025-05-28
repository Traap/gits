# gits/cli.py

import os
import subprocess
import typer
import yaml

from pathlib import Path
from typing import Optional
from gits.config_loader import load_repos
from gits.icons import ICON_SUCCESS, ICON_ERROR, ICON_CLONE, ICON_DELETE, ICON_STATUS, ICON_INFO, ICON_PULL

gits = typer.Typer()

@gits.command()
def clean(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit clean to a specific group.")
):
    """Remove untracked files and directories (git clean -fd)."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                typer.echo(f"{ICON_INFO} Skipping clean, not cloned: {repo['alias']}")
                continue
            try:
                subprocess.run(["git", "-C", str(path), "clean", "-fd"], check=True)
                typer.echo(f"{ICON_SUCCESS} Cleaned: {repo['alias']}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICON_ERROR} Failed to clean: {repo['alias']}")

@gits.command()
def clone(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit cloning to a specific group.")
):
    """Clone repositories."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if path.exists():
                typer.echo(f"{ICON_INFO} Skipping clone, exists: {path}")
                continue
            try:
                subprocess.run(["git", "clone", repo["url"], str(path)], check=True)
                typer.echo(f"{ICON_SUCCESS} {ICON_CLONE} Cloned: {repo['alias']}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICON_ERROR} Failed to clone: {repo['alias']}")

@gits.command()
def convert(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit conversion to a specific group.")
):
    """Add explicit target_path to each repo and rewrite the YAML file."""
    config_file = "repository_locations.yml"
    home = os.environ.get("HOME", "~")
    changed = False

    with open(config_file, "r") as f:
        data = yaml.safe_load(f)

    for group_name, group_repos in data.items():
        if repo_group and group_name != repo_group:
            continue

        root_dir = None
        repositories = []

        # Detect root_dir if present
        for entry in group_repos:
            if isinstance(entry, dict) and "root_dir" in entry:
                root_dir = os.path.expanduser(entry["root_dir"])

        for entry in group_repos:
            if isinstance(entry, dict) and "repositories" in entry:
                for repo in entry["repositories"]:
                    if "target_path" not in repo:
                        resolved_root = root_dir or os.path.join(home, group_name)
                        repo["target_path"] = os.path.join(resolved_root, repo["alias"])
                        typer.echo(f"{ICON_SUCCESS} Added target_path for {group_name}/{repo['alias']}")
                        changed = True

    if changed:
        with open(config_file, "w") as f:
            yaml.dump(data, f, sort_keys=False)
        typer.echo(f"{ICON_SUCCESS} Updated {config_file}")
    else:
        typer.echo(f"{ICON_INFO} No changes made — all target_path values present")

@gits.command()
def delete(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit deletion to a specific group.")
):
    """Delete repositories not marked do_not_delete."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not repo.get("do_not_delete", False) and path.exists():
                try:
                    subprocess.run(["rm", "-rf", str(path)], check=True)
                    typer.echo(f"{ICON_DELETE} Deleted: {repo['alias']}")
                except subprocess.CalledProcessError:
                    typer.echo(f"{ICON_ERROR} Failed to delete: {repo['alias']}")

@gits.command("list")
def list_repos(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit listing to a specific group.")
):
    """List repositories configured in the YAML file."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        typer.echo(f"\nGroup: {group['group_name']}")
        for repo in group["repositories"]:
            typer.echo(f"  - {repo['alias']}: {repo['url']}")

@gits.command()
def pull(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit pull to a specific group.")
):
    """Safely pull latest changes in all cloned repositories."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                typer.echo(f"{ICON_INFO} Skipping pull, not cloned: {path}")
                continue
            try:
                # Check for uncommitted changes
                result = subprocess.run(
                    ["git", "-C", str(path), "status", "--porcelain"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    typer.echo(f"{ICON_INFO} Changes detected, stashing before pull: {repo['alias']}")
                    subprocess.run(["git", "-C", str(path), "stash"], check=True)
                # Perform the pull
                subprocess.run(["git", "-C", str(path), "pull"], check=True)
                typer.echo(f"{ICON_SUCCESS} {ICON_PULL} Pulled: {repo['alias']}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICON_ERROR} Failed to pull: {repo['alias']}")

@gits.command()
def status(
    repo_group: str = typer.Option(None, "--repo-group", "-r", help="Limit status check to a specific group.")
):
    """Print status for all repositories."""
    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                typer.echo(f"{ICON_STATUS} {repo['alias']}: not cloned")
                continue
            try:
                result = subprocess.run(["git", "-C", str(path), "status", "--short"], capture_output=True, text=True)
                status = result.stdout.strip() or "clean"
                typer.echo(f"{ICON_STATUS} {repo['alias']}: {status}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICON_ERROR} {repo['alias']}: failed to get status")


@gits.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit status to a specific group.")
):
    """Default to 'status' if no command is provided."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(status, repo_group=repo_group)

if __name__ == "__main__":
    gits()

