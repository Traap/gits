import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import typer

import gits.icons as ICONS
from gits.config_loader import load_repos

app = typer.Typer(help="Manage git repositories defined in YAML configuration.")


def get_repo_path(group_name: str, alias: str, target_path: Optional[str]) -> Path:
    return Path(target_path or f"{Path.home()}/{group_name}/{alias}")


def filtered_repos(repo_group):
    return [
        (group["group_name"], repo)
        for group in load_repos()
        if not repo_group or group["group_name"] == repo_group
        for repo in group["repositories"]
    ]


@app.command()
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
            typer.echo(f"{ICONS.PULL} {alias}: not cloned")
            return

        if dry_run:
            typer.echo(f"{ICONS.PULL} (dry-run) {alias}: would stash and pull")
            return

        try:
            subprocess.run(["git", "-C", str(path), "stash"], check=True)
            subprocess.run(["git", "-C", str(path), "pull"], check=True)
            typer.echo(f"{ICONS.PULL} {alias}: pulled successfully")
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to pull")

    with ThreadPoolExecutor(max_workers=4) as executor:
        for group_name, repo in filtered_repos(repo_group):
            executor.submit(pull_repo, group_name, repo)


@app.command()
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



@app.command()
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
            typer.echo(f"{ICONS.CLONE} {alias}: already exists")
            return

        if dry_run:
            typer.echo(f"{ICONS.CLONE} (dry-run) would clone {url} to {path}")
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(["git", "clone", url, str(path)], check=True)
            typer.echo(f"{ICONS.CLONE} {alias}: cloned successfully")
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to clone")

    with ThreadPoolExecutor(max_workers=4) as executor:
        for group_name, repo in filtered_repos(repo_group):
            executor.submit(clone_repo, group_name, repo)


@app.command()
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

@app.command()
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


@app.command()
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

        typer.echo(f"{ICONS.INFO} {group_name}")

        if verbose:
            for repo in group["repositories"]:
                if not isinstance(repo, dict) or "alias" not in repo or "url" not in repo:
                    continue
                alias = repo["alias"]
                url = repo["url"]
                typer.echo(f"  - {alias}: {url}")


@app.command()
def status(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Print git status for all repositories."""
    any_output = False

    for group_name, repo in filtered_repos(repo_group):
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            typer.echo(f"{ICONS.STATUS} {alias}: not cloned")
            any_output = True
            continue

        try:
            result = subprocess.run(
                ["git", "-C", str(path), "status", "--short"],
                capture_output=True,
                text=True,
                check=True,
            )
            status_output = result.stdout.strip() or "clean"
            typer.echo(f"{ICONS.STATUS} {alias}: {status_output}")
            any_output = True
        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} {alias}: failed to get status")
            any_output = True

    if not any_output:
        typer.echo(f"{ICONS.INFO} All repositories are clean.")



if __name__ == "__main__":
    import sys

    known_commands = {"clean", "clone", "convert", "delete", "list", "pull", "status"}
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if not args or args[0] not in known_commands:
        typer.echo(f"{ICONS.ERROR} Missing or unknown command. Use '--help' to view available options.")
        raise typer.Exit(code=1)

    app()
