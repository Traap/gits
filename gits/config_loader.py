import os
import yaml
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "repository_locations.yml"

def load_repos():
    with open(CONFIG_FILE, 'r') as f:
        raw = yaml.safe_load(f)

    all_groups = []
    for group_name, group_data in raw.items():
        group_root = Path(os.path.expanduser("~")) / group_name
        group_root_override = next((x['root_dir'] for x in group_data if 'root_dir' in x), None)
        if group_root_override:
            group_root = Path(group_root_override).expanduser()

        repos_entry = next((x['repositories'] for x in group_data if 'repositories' in x), [])

        for repo in repos_entry:
            target_path = group_root / repo['alias']
            repo['target_path'] = str(target_path)

        all_groups.append({
            "group_name": group_name,
            "repositories": repos_entry
        })
    return all_groups
