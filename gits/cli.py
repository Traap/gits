import sys
import typer

from gits.commands.clean import clean
from gits.commands.clone import clone
from gits.commands.convert import convert
from gits.commands.delete import delete
from gits.commands.list import list
from gits.commands.pull import pull
from gits.commands.status import status

import gits.icons as ICONS

app = typer.Typer(help="Manage git repositories defined in YAML configuration.")

# Register each command
app.command()(clean)
app.command()(clone)
app.command()(convert)
app.command()(delete)
app.command()(list)  # Aliased to avoid keyword conflict
app.command()(pull)
app.command()(status)


def main():
    known_commands = {"clean", "clone", "convert", "delete", "list", "pull", "status"}
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if not args or args[0] not in known_commands:
        typer.echo(f"{ICONS.STATUS} Defaulting to: gits status")
        sys.argv.insert(1, "status")

    app()


if __name__ == "__main__":
    main()
