import os
import subprocess
import typer
import yaml

import gits.icons as ICONS
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
from gits.config_loader import load_repos

gits = typer.Typer()

@gits.command()
def clean(ctx: typer.Context):
    """Remove untracked files and directories (git clean -fd)."""
    repos = load_repos()
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)

    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                if verbose:
                    typer.echo(f"{ICONS.INFO} Skipping clean, not cloned: {repo['alias']}")
                continue
            if dry_run:
                typer.echo(f"{ICONS.INFO} [dry-run] Would clean: {repo['alias']}")
            else:
                try:
                    subprocess.run(["git", "-C", str(path), "clean", "-fd"], check=True)
                    typer.echo(f"{ICONS.SUCCESS} Cleaned: {repo['alias']}")
                except subprocess.CalledProcessError:
                    typer.echo(f"{ICONS.ERROR} Failed to clean: {repo['alias']}")

@gits.command()
def clone(ctx: typer.Context):
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)

    repos = load_repos()
    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if path.exists():
                if verbose:
                    typer.echo(f"{ICONS.INFO} Skipping clone, exists: {path}")
                continue
            if dry_run:
                typer.echo(f"{ICONS.INFO} [dry-run] Would clone: {repo['alias']}")
            else:
                try:
                    subprocess.run(["git", "clone", repo["url"], str(path)], check=True)
                    typer.echo(f"{ICONS.SUCCESS} {ICONS.CLONE} Cloned: {repo['alias']}")
                except subprocess.CalledProcessError:
                    typer.echo(f"{ICONS.ERROR} Failed to clone: {repo['alias']}")

@gits.command()
def convert(ctx: typer.Context):
    """Add explicit target_path to each repo and rewrite the YAML file."""
    config_file = "repository_locations.yml"
    home = os.environ.get("HOME", "~")
    lock = Lock()
    changed = False

    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)
    max_workers = 4  # Optional: add global support later

    with open(config_file, "r") as f:
        data: Dict[str, Any] = yaml.safe_load(f)

    def process_repo(group_name, repo, root_dir):
        nonlocal changed
        if "target_path" not in repo:
            resolved_root = root_dir or os.path.join(home, group_name)
            repo["target_path"] = os.path.join(resolved_root, repo["alias"])
            with lock:
                changed = True
                if verbose:
                    typer.echo(f"{ICONS.SUCCESS} Added target_path for {group_name}/{repo['alias']}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for group_name, group_repos in data.items():
            if repo_group and group_name != repo_group:
                continue

            root_dir = None

            for entry in group_repos:
                if isinstance(entry, dict) and "root_dir" in entry:
                    root_dir = os.path.expanduser(entry["root_dir"])

            for entry in group_repos:
                if isinstance(entry, dict) and "repositories" in entry:
                    for repo in entry["repositories"]:
                        executor.submit(process_repo, group_name, repo, root_dir)

    if dry_run:
        typer.echo(f"{ICONS.INFO} Dry run — no file written.")
    elif changed:
        with open(config_file, "w") as f:
            yaml.dump(data, f, sort_keys=False)
        typer.echo(f"{ICONS.SUCCESS} Updated {config_file}")
    else:
        typer.echo(f"{ICONS.INFO} No changes made — all target_path values present")

@gits.command()
def delete(ctx: typer.Context):
    """Delete cloned repositories listed in YAML, respecting 'do_not_delete'."""
    from shutil import rmtree

    repos = load_repos()
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)
    home = os.path.expanduser("~")

    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue

        group_dir = Path(home) / group["group_name"]
        aliases_in_yaml = {entry['alias'] for entry in group["repositories"]}
        deleted = []

        for entry in group["repositories"]:
            alias = entry["alias"]
            do_not_delete = entry.get("do_not_delete", False)
            repo_path = group_dir / alias

            if do_not_delete:
                typer.echo(f"{ICONS.WARNING} {group['group_name']}/{alias}: marked do_not_delete, skipping.")
                continue

            if repo_path.is_dir():
                typer.echo(f"{ICONS.DELETE} {repo_path}")
                if dry_run:
                    typer.echo(f"    {ICONS.INFO} (Dry-run; not removed)")
                else:
                    try:
                        rmtree(repo_path)
                        typer.echo(f"    {ICONS.DONE} Removed.")
                    except Exception as e:
                        typer.echo(f"    {ICONS.ERROR} Error removing: {e}")
                deleted.append(alias)
            else:
                if verbose:
                    typer.echo(f"{ICONS.WARNING} [NOT FOUND] {repo_path}")

        # Show any unlisted (not in YAML) directories
        if group_dir.is_dir():
            for alias in os.listdir(group_dir):
                if alias not in aliases_in_yaml:
                    extra_path = group_dir / alias
                    if extra_path.is_dir():
                        typer.echo(f"{ICONS.WARNING} {group['group_name']}/{alias} is unlisted and was NOT deleted.")

        # Remove group dir only if empty
        if group_dir.is_dir() and not any(group_dir.iterdir()):
            if dry_run:
                typer.echo(f"{ICONS.INFO} (Dry-run) Would remove empty group directory: {group_dir}")
            else:
                try:
                    group_dir.rmdir()
                    typer.echo(f"{ICONS.DONE} Removed empty group directory: {group_dir}")
                except Exception as e:
                    typer.echo(f"{ICONS.ERROR} Error removing group dir: {e}")

@gits.command()
def list(ctx: typer.Context):
    """List configured repository groups (and optionally their repos)."""
    repos = load_repos()

    verbose = ctx.obj.get("verbose", False)
    repo_group = ctx.obj.get("repo_group", None)

    matched = False
    for group in repos:
        group_name = group["group_name"]

        if repo_group and group_name != repo_group:
            continue

        matched = True
        typer.echo(f"{ICONS.INFO} Group: {group_name}")

        if verbose:
            for repo in group["repositories"]:
                typer.echo(f"  - {repo['alias']}: {repo['url']}")

    if not matched:
        typer.echo(f"{ICONS.ERROR} No matching group found.")

@gits.command()
def pull(ctx: typer.Context):
    """Stash local changes and pull latest changes in all cloned repositories."""
    repos = load_repos()
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)

    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                if verbose:
                    typer.echo(f"{ICONS.INFO} Skipping pull, not cloned: {repo['alias']}")
                continue
            if dry_run:
                typer.echo(f"{ICONS.INFO} [dry-run] Would stash and pull: {repo['alias']}")
                continue
            try:
                # Check for uncommitted changes
                result = subprocess.run(
                    ["git", "-C", str(path), "status", "--porcelain"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    if verbose:
                        typer.echo(f"{ICONS.INFO} Changes detected, stashing: {repo['alias']}")
                    subprocess.run(["git", "-C", str(path), "stash"], check=True)

                subprocess.run(["git", "-C", str(path), "pull"], check=True)
                typer.echo(f"{ICONS.SUCCESS} {ICONS.PULL} Pulled: {repo['alias']}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICONS.ERROR} Failed to pull: {repo['alias']}")

@gits.command()
def status(ctx: typer.Context):
    """Print status for all repositories."""
    repos = load_repos()
    verbose = ctx.obj.get("verbose", False)
    dry_run = ctx.obj.get("dry_run", False)
    repo_group = ctx.obj.get("repo_group", None)

    for group in repos:
        if repo_group and group["group_name"] != repo_group:
            continue
        for repo in group["repositories"]:
            path = Path(repo["target_path"])
            if not path.exists():
                typer.echo(f"{ICONS.STATUS} {repo['alias']}: not cloned")
                continue
            try:
                result = subprocess.run(
                    ["git", "-C", str(path), "status", "--short"],
                    capture_output=True,
                    text=True
                )
                status = result.stdout.strip() or "clean"
                typer.echo(f"{ICONS.STATUS} {repo['alias']}: {status}")
            except subprocess.CalledProcessError:
                typer.echo(f"{ICONS.ERROR} {repo['alias']}: failed to get status")

@gits.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Establish global options and default to 'status'."""
    ctx.ensure_object(dict)  # Ensures ctx.obj is a dict
    ctx.obj["repo_group"] = repo_group
    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run

    if ctx.invoked_subcommand is None:
        ctx.invoke(status, ctx=ctx)

