import typer
from typing import Optional

from gits.commands.clean import clean
from gits.commands.clone import clone
from gits.commands.convert import convert
from gits.commands.delete import delete
from gits.commands.doctor import doctor
from gits.commands.list import list
from gits.commands.pull import pull
from gits.commands.stash import stash
from gits.commands.pop import pop
from gits.commands.status import status

app = typer.Typer(help="Manage git repositories defined in YAML configuration.")

for command in (clean, clone, convert, delete, doctor, list, pop, pull, stash, status):
    app.command()(command)

@app.callback(invoke_without_command=True)
def default_command(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
):
    from gits.utils.cli import Options

    ctx.obj = Options(repo_group, verbose, dry_run)
    if ctx.invoked_subcommand is None:
        status(ctx=ctx, repo_group=repo_group, verbose=verbose, dry_run=dry_run)
