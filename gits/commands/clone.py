from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import typer

import gits.ui.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos


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
        messages = []

        # Skip existing repos
        if path.exists():
            if verbose:
                messages.append(f"   {ICONS.WARNING} Exists: {alias}")
            return (group_name, alias, "SKIPPED", messages)

        # Dry-run mode
        if dry_run:
            messages.append(f"   {ICONS.CLONE} (dry-run) clone {url} {path}")
            return (group_name, alias, "DRY-RUN", messages)

        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ["git", "clone", "-v", url, str(path)],
                capture_output=True,
                text=True,
                check=True,
            )

            if verbose:
                messages.append(f"  {ICONS.CLONE} Clone: {alias} {url} {path}")
            else:
               messages.append(f"   {ICONS.CLEAN} Clone: {alias}")
            return (group_name, alias, "SUCCESS", messages)

        except subprocess.CalledProcessError as e:
            err_output = (e.stdout or "") + (e.stderr or "")
            messages.append(f"   {ICONS.ERROR} Failed: {alias}")
            if verbose and err_output.strip():
                formatted = "\n".join(f"\t{line}" for line in err_output.splitlines())
                messages.append(formatted)
            return (group_name, alias, "FAIL", messages)

    # --- main thread ---
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        seen_group = ""
        for group_name, repo in filtered_repos(repo_group):
            if group_name != seen_group:
                seen_group = group_name
                typer.echo(f"{ICONS.GROUP} {group_name}")
            futures.append(executor.submit(clone_repo, group_name, repo))

        # print results sequentially
        for future in as_completed(futures):
            group, alias, status, messages = future.result()
            for line in messages:
                typer.echo(line)

