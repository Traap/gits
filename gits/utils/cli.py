from dataclasses import dataclass

import typer
import yaml
import gits.ui.icons as ICONS
from gits.utils.repos import filtered_repos
from gits.utils.operations import execute


@dataclass(frozen=True)
class Options:
    repo_group: str = None
    verbose: bool = False
    dry_run: bool = False


def options(ctx, repo_group=None, verbose=False, dry_run=False):
    parent = ctx.obj if ctx is not None and isinstance(ctx.obj, Options) else Options()
    return Options(repo_group if repo_group is not None else parent.repo_group,
                   verbose or parent.verbose, dry_run or parent.dry_run)


def configured(action):
    try:
        return action()
    except (OSError, ValueError) as error:
        raise typer.BadParameter(str(error)) from error
    except yaml.YAMLError as error:
        raise typer.BadParameter(f"Invalid YAML: {error}") from error


def report(results, verbose=False, always=False):
    group = None
    for result in results:
        visible = verbose or result.state in ("failed", "planned") or (always and result.state == "success")
        if not visible:
            continue
        if result.repo.group_name != group:
            group = result.repo.group_name
            typer.echo(f"{ICONS.GROUP} {group}")
        icon = ICONS.ERROR if result.state == "failed" else ICONS.INFO
        typer.echo(f"   {icon} {result.repo.alias}: {result.state}")
        if result.output:
            typer.echo("\n".join(f"      {line}" for line in result.output.splitlines()))
    if any(result.state == "failed" for result in results):
        raise typer.Exit(1)


def run(opts, operation, workers=1, include_unlisted=False, always=False):
    repos = configured(lambda: filtered_repos(opts.repo_group, include_unlisted))
    report(execute(repos, operation, workers), opts.verbose, always)
