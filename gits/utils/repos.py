from pathlib import Path
from typing import Optional

from gits.utils.config_loader import load_repos

def get_repo_path(group_name: str, alias: str, target_path: Optional[str]) -> Path:
    return Path(target_path or f"{Path.home()}/{group_name}/{alias}")

def filtered_repos(repo_group):
    return [
        (group["group_name"], repo)
        for group in load_repos()
        if not repo_group or group["group_name"] == repo_group
        for repo in group["repositories"]
    ]

