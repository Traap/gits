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

        known_aliases = {repo["alias"] for repo in group["repositories"]}
        root_dir = group["root_dir"]

        # Avoid adding subdirectories of listed repositories
        listed_paths = {
            os.path.realpath(os.path.join(root_dir, repo["alias"]))
            for repo in group["repositories"]
        }

        if root_dir and os.path.isdir(root_dir):
            for entry in os.scandir(root_dir):
                entry_path = os.path.realpath(entry.path)
                if (
                    entry.is_dir()
                    and entry.name not in known_aliases
                    and entry_path not in listed_paths
                ):
                    group["repositories"].append({
                        "alias": entry.name,
                        "target_path": entry_path,
                        "unlisted": True
                    })

        result.append(group)

    return result
