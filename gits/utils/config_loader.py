import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import yaml

CONFIG_FILE = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "gits" / "repository_locations.yml"


@dataclass(frozen=True)
class Repository:
    group_name: str
    alias: str
    path: Path
    url: Optional[str] = None
    do_not_delete: bool = False
    unlisted: bool = False


@dataclass(frozen=True)
class Group:
    name: str
    root: Path
    repositories: Tuple[Repository, ...]


def load_repos(config_file=None):
    """Parse and validate configuration without scanning the filesystem."""
    with open(config_file or CONFIG_FILE, encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError("Repository configuration must be a mapping of groups.")
    groups = []
    for name, entries in raw.items():
        if not isinstance(name, str) or not isinstance(entries, list):
            raise ValueError("Each group must have a name and a list of entries.")
        root = Path.home() / name
        configured = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"{name}: entries must be mappings.")
            if "root_dir" in entry:
                if not isinstance(entry["root_dir"], str) or not entry["root_dir"]:
                    raise ValueError(f"{name}: root_dir must be a nonempty string.")
                root = Path(entry["root_dir"]).expanduser().absolute()
            if "repositories" in entry:
                if not isinstance(entry["repositories"], list):
                    raise ValueError(f"{name}: repositories must be a list.")
                configured.extend(entry["repositories"])
        repos = []
        aliases = set()
        for repo in configured:
            if not isinstance(repo, dict):
                raise ValueError(f"{name}: repository entries must be mappings.")
            alias, url = repo.get("alias"), repo.get("url")
            if not isinstance(alias, str) or not alias or alias in aliases:
                raise ValueError(f"{name}: aliases must be nonempty and unique.")
            if not isinstance(url, str) or not url:
                raise ValueError(f"{name}/{alias}: url is required.")
            target = repo.get("target_path")
            if target is not None and (not isinstance(target, str) or not target):
                raise ValueError(f"{name}/{alias}: target_path must be a nonempty string.")
            protected = repo.get("do_not_delete", False)
            if not isinstance(protected, bool):
                raise ValueError(f"{name}/{alias}: do_not_delete must be a boolean.")
            path = Path(target).expanduser().absolute() if target else root / alias
            repos.append(Repository(name, alias, path, url, protected))
            aliases.add(alias)
        groups.append(Group(name, root, tuple(repos)))
    return groups
