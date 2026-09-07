import os
import shutil
import stat
from typing import Optional

import typer
from gits.utils.cli import configured, options, report
from gits.utils.operations import Result, execute
from gits.utils.repos import selected_groups


def on_rm_error(func, path, exc_info):
    if not isinstance(exc_info[1], PermissionError):
        raise exc_info[1]
    os.chmod(path, os.stat(path).st_mode | stat.S_IWRITE)
    func(path)


def delete(
    ctx: typer.Context,
    repo_group: Optional[str] = typer.Option(None, "--repo-group", "-r"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
):
    """Delete configured repositories unless protected by do_not_delete."""
    opts = options(ctx, repo_group, verbose, dry_run)

    def remove(repo):
        if repo.do_not_delete:
            return Result(repo, "skipped", "Protected by do_not_delete")
        if not repo.path.exists():
            return Result(repo, "skipped", "Not cloned")
        if opts.dry_run:
            return Result(repo, "planned", f"(dry-run) would remove {repo.path}")
        shutil.rmtree(repo.path, onerror=on_rm_error)
        return Result(repo, "success", f"Deleted {repo.path}")

    results = []
    for group in configured(lambda: selected_groups(opts.repo_group)):
        results.extend(execute(group.repositories, remove))
        if not opts.dry_run and group.root.is_dir():
            try:
                if not any(group.root.iterdir()):
                    group.root.rmdir()
            except OSError as error:
                typer.echo(f"Failed to remove group root {group.root}: {error}", err=True)
                raise typer.Exit(1) from error
    report(results, opts.verbose, always=True)
