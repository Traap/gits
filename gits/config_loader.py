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
        for entry in entries:
            if "root_dir" in entry:
                group["root_dir"] = os.path.expanduser(entry["root_dir"])
            elif "repositories" in entry:
                group["repositories"].extend(entry["repositories"])
        result.append(group)
    return result
