from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

import typer
import gits.ui.icons as ICONS
from gits.utils.repos import get_repo_path, filtered_repos

def pull(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r", help="Limit to a specific group."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Run without making changes."),
):
    """Pull changes for all repositories including unlisted ones."""
    def pull_repo(group_name, repo):
        any_output = False
        alias = repo["alias"]
        path = get_repo_path(group_name, alias, repo.get("target_path"))

        if not path.exists():
            if verbose:
                typer.echo(f"   {ICONS.PULL} Not pulled: {alias}")
                any_output = True
            return

        if dry_run:
            typer.echo(f"   {ICONS.PULL} (dry-run) {alias}: would stash and pull")
            any_output = True
            return


        try:
            stash = subprocess.run(
                ["git", "-C", str(path), "stash"],
                capture_output=True,
                text=True,
                check=True,
            )

            pull = subprocess.run(
                ["git", "-C", str(path), "pull"],
                capture_output=True,
                text=True,
                check=True,
            )
            if verbose:
                output = "Stash: " + stash.stdout.rstrip() + ". Pull: " + pull.stdout.rstrip()
                if output:
                    output = "\n".join(f"\t    {line}" for line in output.splitlines())
                    typer.echo(f"   {ICONS.PULL} Pull: {alias}\n{output}")
                else:
                    typer.echo(f"   {ICONS.CLEAN} Clean: {alias}")
            any_output = True

        except subprocess.CalledProcessError:
            typer.echo(f"{ICONS.ERROR} Failed: {alias}")
            any_output = True

        if not any_output:
            typer.echo(f"   {ICONS.INFO} All repositories are clean.")

    with ThreadPoolExecutor(max_workers=4) as executor:
        check_group = ""
        for group_name, repo in filtered_repos(repo_group):
            if group_name != check_group:
                check_group = group_name
                if verbose or dry_run:
                    typer.echo(f"{ICONS.GROUP} {group_name}")
            executor.submit(pull_repo, group_name, repo)

