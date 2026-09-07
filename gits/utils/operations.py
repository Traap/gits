"""Repository operations independent of CLI rendering."""
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from gits.utils.config_loader import Repository


@dataclass(frozen=True)
class Result:
    repo: Repository
    state: str
    output: str = ""


def run_git(path, args, dry_run=False, mutating=False):
    if dry_run and mutating:
        return "(dry-run) git " + " ".join(args)
    completed = subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


def git_operation(repo, commands, dry_run=False, mutating=False):
    if not repo.path.exists():
        return Result(repo, "skipped", "Not cloned")
    output = [run_git(repo.path, args, dry_run, mutating) for args in commands]
    return Result(repo, "planned" if dry_run and mutating else "success", "\n".join(filter(None, output)))


def clone_repo(repo, dry_run=False):
    if repo.path.exists():
        return Result(repo, "skipped", "Already exists")
    if dry_run:
        return Result(repo, "planned", f"(dry-run) clone {repo.url} {repo.path}")
    repo.path.parent.mkdir(parents=True, exist_ok=True)
    output = run_git(repo.path.parent, ["clone", repo.url, str(repo.path)])
    return Result(repo, "success", output)


def convert_repo(repo, dry_run=False):
    if not repo.path.exists():
        return Result(repo, "skipped", "Not cloned")
    converted = []
    for file in repo.path.rglob("*"):
        if ".git" in file.relative_to(repo.path).parts or file.is_symlink() or not file.is_file():
            continue
        with file.open("rb") as stream:
            if stream.read(2) not in (b"\xff\xfe", b"\xfe\xff"):
                continue
        content = file.read_text(encoding="utf-16")
        if not dry_run:
            file.write_text(content, encoding="utf-8")
        converted.append(f"{'(dry-run) would convert' if dry_run else 'Converted'} {file}")
    return Result(repo, "planned" if dry_run else "success", "\n".join(converted))


def execute(repos, operation, workers=1):
    def checked(repo):
        try:
            return operation(repo)
        except subprocess.CalledProcessError as error:
            return Result(repo, "failed", (error.stderr or error.stdout or str(error)).strip())
        except (OSError, UnicodeError, ValueError) as error:
            return Result(repo, "failed", str(error))
    if workers == 1:
        return [checked(repo) for repo in repos]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(checked, repos))
