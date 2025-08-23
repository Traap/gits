import sys
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

known_commands = {
    "clean",
    "clone",
    "convert",
    "delete",
    "doctor",
    "list",
    "pop",
    "pull",
    "stash",
    "status"
    }

# Register each command
app.command()(clean)
app.command()(clone)
app.command()(convert)
app.command()(delete)
app.command()(doctor)
app.command()(list)
app.command()(pop)
app.command()(pull)
app.command()(stash)
app.command()(status)

@app.callback(invoke_without_command=True)
def default_command(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
):
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    if not args or args[0] not in known_commands:
        status(ctx=ctx, repo_group=repo_group, verbose=verbose, dry_run=dry_run)

