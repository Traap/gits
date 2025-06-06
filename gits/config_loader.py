import os
from pathlib import Path
import yaml

CONFIG_FILE = Path(os.getenv("XDG_CONFIG_HOME", f"{Path.home()}/.config")) / "gits" / "repository_locations.yml"

def load_repos():
    with open(CONFIG_FILE, "r") as f:
        raw = yaml.safe_load(f)

    result = []
    for group_name, entries in raw.items():
        group = {"group_name": group_name, "root_dir": None, "repositories": []}

        # Parse the YAML entries for root_dir and listed repositories
        for entry in entries:
            if "root_dir" in entry:
                group["root_dir"] = os.path.expanduser(entry["root_dir"])
            elif "repositories" in entry:
                group["repositories"].extend(entry["repositories"])

        # Track existing aliases to avoid duplicates
        known_aliases = {repo["alias"] for repo in group["repositories"]}
        root_dir = group["root_dir"]

        # Automatically add unlisted subdirectories as new repositories
        if root_dir and os.path.isdir(root_dir):
            for entry in os.scandir(root_dir):
                if entry.is_dir() and entry.name not in known_aliases:
                    group["repositories"].append({
                        "alias": entry.name,
                        "target_path": os.path.join(root_dir, entry.name),
                        "unlisted": True
                    })

        result.append(group)

    return result
