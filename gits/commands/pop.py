from typing import Optional
import subprocess

import typer
import gits.ui.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos


def pop(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Pop stashed entries in all repositories."""
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

        if not path.exists():
            if verbose:
                typer.echo(f"   {ICONS.WARNING} Not cloned: {alias}")
            any_output = True
            continue

        try:
            pop = subprocess.run(
                ["git", "-C", str(path), "stash", "pop"],
                capture_output=True,
                text=True,
                check=True,
            )

            if verbose:
                output = pop.stdout.rstrip()
                if output:
                    output = "\n".join(f"\t{line}" for line in output.splitlines())
                    typer.echo(f"   {ICONS.INFO} Poped: {alias}\n{output}")
                else:
                    typer.echo(f"   {ICONS.CLEAN} Clean: {alias}")

            any_output = True
        except subprocess.CalledProcessError:
            if verbose:
                typer.echo(f"   {ICONS.ERROR} {alias}: is not a git repository")
            any_output = True

    if not any_output:
        typer.echo(f"   {ICONS.INFO} All repositories are clean.")

