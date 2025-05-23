#!/usr/bin/env python3
# {{{ Header notes.

"""
gits.py - Python version of 'gits' repository management script, with icons.

Features:
  - Pre-flight YAML validation (clear errors for malformed config)
  - Clone, delete, pull, clean, convert encoding, list stashes, and more
  - All repo directories are in $HOME/group/alias
  - Parallel actions, dry-run and verbose support
  - Beautiful, informative icons for every status/action

Author: Traap
Date: 2025-05-18
"""

# -------------------------------------------------------------------------- }}}
# {{{ Import statements

import argparse
import sys
import os
import yaml
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------------------------------------------------- }}}
# {{{ ICONS

ICON_CLEAN    = "🧹"
ICON_CLONE    = "➡️"
ICON_CONVERT  = "🔄"
ICON_DELETE   = "❌"
ICON_DONE     = "✅"
ICON_ERROR    = "❌"
ICON_INFO     = "ℹ️"
ICON_PULL     = "⬆️"
ICON_STASH    = "📦"
ICON_SUCCESS  = "✅"
ICON_TIME     = "⏱️"
ICON_WARNING  = "⚠️"

# -------------------------------------------------------------------------- }}}
# {{{ Options class holds all CLI options.

class Options:
    """
    Holds all CLI options parsed from argparse.
    Makes it easy to pass all user settings to helpers.
    """
    def __init__(self, args):
        for k, v in vars(args).items():
            setattr(self, k, v)

        # If no CLI options were set, defalt to -s (status).
        if not any(vars(self).values()):
           self.s = True

#  ------------------------------------------------------------------------- }}}
# {{{ Parse arguments

def parse_args():
    """
    Set up argument parser for CLI options and return the parsed args.
    """
    parser = argparse.ArgumentParser(add_help=False, usage=argparse.SUPPRESS)
    parser.add_argument('-h', action='store_true')
    parser.add_argument('-l', action='store_true')
    parser.add_argument('-r', metavar='name', type=str)
    parser.add_argument('-d', action='store_true')
    parser.add_argument('-s', action='store_true')
    parser.add_argument('-u', action='store_true')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-x', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', action='store_true')
    group.add_argument('-p', action='store_true')
    parser.add_argument('-n', action='store_true')
    args = parser.parse_args()
    return args

# -------------------------------------------------------------------------- }}}
# {{{ Load Repository Yaml File

def load_repos_yaml(filepath):
    """
    Load the repository locations YAML file.
    """
    if not os.path.exists(filepath):
        print(f"{ICON_ERROR} Repo locations file not found: {filepath}")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

#  ------------------------------------------------------------------------- }}}
# {{{ Validate Repository Yaml File

def validate_repo_data(repo_data):
    """
    Ensures every entry in repo_data is a dict with 'alias' and 'url' keys.
    Checks that 'do_not_delete' is optional and if present is a bool.
    Raises ValueError if not.
    """
    for group, entries in repo_data.items():
        if not isinstance(entries, list):
            raise ValueError(f"Group '{group}' is not a list.")
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f"Entry {idx+1} in group '{group}' is not a dict: {entry}")
            missing = [key for key in ("alias", "url") if key not in entry]
            if missing:
                raise ValueError(f"Entry {idx+1} in group '{group}' missing {', '.join(missing)}: {entry}")
            # Check do_not_delete if present
            if "do_not_delete" in entry and not isinstance(entry["do_not_delete"], bool):
                raise ValueError(
                    f"Entry {idx+1} in group '{group}' has 'do_not_delete' but it is not true/false: {entry['do_not_delete']!r}"
                )

# -------------------------------------------------------------------------- }}}
# {{{ Print help.

def print_help():
    """
    Show CLI usage.
    """
    print(f"{ICON_INFO} Usage: gits [-h -l] [-r name -d -s -u -v -x] [-c | -p] [-n]\n")
    print("Options:")
    print("  -h          Show help")
    print("  -l          List repository locations")
    print("Repository Locations")
    print("  -r name")
    print("Modifiers")
    print("  -d          Delete repository location")
    print("  -s          List repositories with stash entries")
    print("  -u          Convert UTF-16 files to UTF-8")
    print("  -v          Verbose output")
    print("  -x          Clean untracked files")
    print("Mutually exclusive actions")
    print("  -c          Clone repositories defined in repository locations array")
    print("  -p          Pull repositories with safe stashing")
    print("Dry-run")
    print("  -n          Dry-run (simulate actions)")

# -------------------------------------------------------------------------- }}}
# {{{ List Repositories

def list_repos(repo_data, options):
    """
    List only the group names found in the YAML.
    """
    if not options.r:
        print(f"{ICON_INFO} Repository locations:\n")
        for group in repo_data.keys():
            print(f"  {ICON_INFO} {group}")
        print()
    else:
        group = options.r
        if group not in repo_data:
            print(f"{ICON_WARNING} Group '{group}' not found.")
            return
        print(f"{ICON_INFO} Repositories in group '{group}':")
        for entry in repo_data[group]:
            alias = entry.get('alias', 'N/A')
            url = entry.get('url', 'N/A')
            print(f"  {ICON_INFO} {alias:15} {url}")

# -------------------------------------------------------------------------- }}}
# {{{ Iterate Over Repositories Directories

def iter_repo_dirs(repo_data, options):
    """
    Yield (group, alias, repo_dir, listed) for each repo dir on disk and/or YAML entry.
    - For each group (or only options.r), yield every subdir in $HOME/group/
      (listed = True if it's in YAML, False if not)
    - Also yield any YAML entries that don't have a directory.
    """
    home = os.path.expanduser("~")
    groups = [options.r] if options.r else list(repo_data.keys())
    for group in groups:
        group_dir = os.path.join(home, group)
        aliases_in_yaml = {entry['alias'] for entry in repo_data.get(group, [])}
        found = set()
        # First: All subdirs on disk
        if os.path.isdir(group_dir):
            for alias in os.listdir(group_dir):
                repo_dir = os.path.join(group_dir, alias)
                if not os.path.isdir(repo_dir):
                    continue
                listed = alias in aliases_in_yaml
                yield group, alias, repo_dir, listed
                found.add(alias)
        # Second: Any YAML-listed aliases that are missing as dirs
        for entry in repo_data.get(group, []):
            alias = entry['alias']
            if alias not in found:
                repo_dir = os.path.join(group_dir, alias)
                yield group, alias, repo_dir, True  # listed, but dir missing


# -------------------------------------------------------------------------- }}}
# {{{ Clone a repository

def clone_repo(url, alias, group, verbose=False, dry_run=False):
    """
    Clone a single repository.
    """
    home = os.path.expanduser("~")
    dest_dir = os.path.join(home, group, alias)
    if os.path.exists(dest_dir) and os.listdir(dest_dir):
        return (alias, url, dest_dir, "SKIPPED", 0, "Directory not empty")
    if dry_run:
        return (alias, url, dest_dir, "DRY-RUN", 0, "")
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    cmd = ["git", "clone", url, dest_dir]
    try:
        if verbose:
            print(f"{ICON_CLONE} Cloning {url} to {dest_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return (alias, url, dest_dir, "SUCCESS", 0, "")
        else:
            return (alias, url, dest_dir, "FAIL", result.returncode, result.stderr)
    except Exception as e:
        return (alias, url, dest_dir, "FAIL", -1, str(e))

# -------------------------------------------------------------------------- }}}
# {{{ Clone all repository

def clone_all_repos(repo_data, options):
    """
    Clone all repositories (optionally, only in selected group), in parallel.
    """
    max_workers = 4
    jobs = []
    for group, entries in repo_data.items():
        if options.r and group != options.r:
            continue
        for entry in entries:
            jobs.append((entry["url"], entry["alias"], group))
    print(f"{ICON_CLONE} Cloning {len(jobs)} repositories (parallel={max_workers})...\n")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {
            executor.submit(clone_repo, url, alias, group, options.v, options.n): (alias, url, group)
            for url, alias, group in jobs
        }
        for future in as_completed(future_to_job):
            alias, url, dest_dir, status, code, msg = future.result()
            group = dest_dir.split("/")[-2] if "/" in dest_dir else ""
            if status == "SUCCESS":
                icon = ICON_SUCCESS
            elif status == "FAIL":
                icon = ICON_ERROR
            elif status == "SKIPPED":
                icon = ICON_WARNING
            elif status == "DRY-RUN":
                icon = ICON_INFO
            else:
                icon = ICON_INFO
            print(f"{icon} {group}/{alias:12} {url}")
            if status == "FAIL":
                print(f"    {ICON_ERROR} Error: {msg.strip()}")
            if status == "SKIPPED":
                print(f"    {ICON_WARNING} Skipped: {msg.strip()}")
    print(f"\n{ICON_DONE} Clone complete.")

# -------------------------------------------------------------------------- }}}
# {{{ Delete all repository

def delete_all_repos(repo_data, options):
    """
    Delete only listed (YAML) repos unless do_not_delete: true.
    Delete group dir only if empty after.
    Do NOT touch unlisted/orphan directories, but report them.
    """
    home = os.path.expanduser("~")
    for group, entries in repo_data.items():
        if options.r and group != options.r:
            continue
        group_dir = os.path.join(home, group)
        aliases_in_yaml = {entry['alias'] for entry in entries}
        deleted = []
        # 1. Try to delete each listed repo
        for entry in entries:
            alias = entry['alias']
            repo_dir = os.path.join(group_dir, alias)
            do_not_delete = entry.get('do_not_delete', False)
            if do_not_delete:
                print(f"{ICON_WARNING} {group}/{alias}: marked do_not_delete, skipping.")
                continue
            if os.path.isdir(repo_dir):
                print(f"{ICON_DELETE} {repo_dir}")
                if not options.n:
                    try:
                        shutil.rmtree(repo_dir)
                        print(f"    {ICON_DONE} Removed.")
                    except Exception as e:
                        print(f"    {ICON_ERROR} Error removing: {e}")
                else:
                    print(f"    {ICON_INFO} (Dry-run; not removed)")
                deleted.append(alias)
            else:
                if options.v:
                    print(f"{ICON_WARNING} [NOT FOUND] {repo_dir}")
        # 2. Report any unlisted directories not in YAML
        if os.path.isdir(group_dir):
            for alias in os.listdir(group_dir):
                if alias not in aliases_in_yaml:
                    repo_dir = os.path.join(group_dir, alias)
                    if os.path.isdir(repo_dir):
                        print(f"{ICON_WARNING} {group}/{alias} is unlisted (not in YAML) and was NOT deleted.")
        # 3. Remove group dir only if empty after deletes
        if os.path.isdir(group_dir) and not os.listdir(group_dir):
            if not options.n:
                try:
                    os.rmdir(group_dir)
                    print(f"{ICON_DONE} Removed empty group directory: {group_dir}")
                except Exception as e:
                    print(f"{ICON_ERROR} Error removing group dir: {e}")
            else:
                print(f"{ICON_INFO} (Dry-run) Would remove empty group directory: {group_dir}")

# -------------------------------------------------------------------------- }}}
# {{{ Pull a repository

def pull_repo(group, alias, repo_dir, listed, options):
    if not os.path.isdir(repo_dir):
        return (group, alias, "NOT_FOUND", None, listed)
    if options.n:
        return (group, alias, "DRY-RUN", None, listed)
    try:
        changed = subprocess.run(
            ["git", "-C", repo_dir, "status", "--porcelain"],
            capture_output=True, text=True)
        stashed = False
        if changed.stdout.strip():
            stash = subprocess.run(
                ["git", "-C", repo_dir, "stash"], capture_output=True, text=True)
            stashed = "No local changes" not in stash.stdout
            if options.v:
                print(f"{ICON_STASH} [{group}/{alias}] Stashed local changes")
        pull = subprocess.run(
            ["git", "-C", repo_dir, "pull"], capture_output=True, text=True)
        if pull.returncode != 0:
            return (group, alias, "FAIL", pull.stderr, listed)
        if stashed:
            subprocess.run(
                ["git", "-C", repo_dir, "stash", "pop"], capture_output=True, text=True)
            if options.v:
                print(f"{ICON_STASH} [{group}/{alias}] Popped stash after pull")
        return (group, alias, "SUCCESS", None, listed)
    except Exception as e:
        return (group, alias, "FAIL", str(e), listed)

# -------------------------------------------------------------------------- }}}
# {{{ Pull all repositories

def pull_all_repos(repo_data, options):
    """
    Pull changes for all repositories (or just a group), with safe stashing.
    Annotates unlisted (not in YAML) repos in the output.
    """
    jobs = list(iter_repo_dirs(repo_data, options))
    print(f"{ICON_PULL} Pulling {len(jobs)} repositories...\n")

    results = []
    max_workers = 4
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {
            executor.submit(pull_repo, group, alias, repo_dir, listed, options): (group, alias, listed)
            for group, alias, repo_dir, listed in jobs
        }
        for future in as_completed(future_to_job):
            group, alias, status, msg, listed = future.result()
            label = f"{group}/{alias}"
            extra = f" {ICON_WARNING}(unlisted, not in YAML)" if not listed else ""
            if status == "SUCCESS":
                icon = ICON_SUCCESS
            elif status == "FAIL":
                icon = ICON_ERROR
            elif status == "DRY-RUN":
                icon = ICON_INFO
            elif status == "NOT_FOUND":
                icon = ICON_WARNING
            else:
                icon = ICON_INFO
            print(f"{icon} {label}{extra}")
            if msg and status == "FAIL":
                print(f"    {ICON_ERROR} Error: {msg.strip()}")

    print(f"\n{ICON_DONE} Pull complete.")

# -------------------------------------------------------------------------- }}}
# {{{ List repositories status.

def list_status_repos(repo_data, options):
    """
    Show git status for each repo in the selected group (or all).
    Lists:
      - stashed entries
      - edited/changed files
      - deleted files
      - untracked files
    """
    jobs = list(iter_repo_dirs(repo_data, options))
    any_status = False
    for group, alias, repo_dir, listed in jobs:
        if not os.path.isdir(repo_dir):
            continue

        stashed = subprocess.run(
            ["git", "-C", repo_dir, "stash", "list"],
            capture_output=True, text=True)
        status = subprocess.run(
            ["git", "-C", repo_dir, "status", "--short"],
            capture_output=True, text=True)
        output_lines = []

        if stashed.stdout.strip():
            output_lines.append(f"{ICON_STASH}  stash: {len(stashed.stdout.strip().splitlines())} entry/entries")

        if status.stdout.strip():
            for line in status.stdout.strip().splitlines():
                parts = line.split(maxsplit=1)
                status_code = parts[0] if parts else ""
                filename = parts[1] if len(parts) > 1 else ""
                if status_code == "??":
                    output_lines.append(f"{ICON_WARNING}  untracked: {filename}")
                elif "M" in status_code:
                    output_lines.append(f"{ICON_CONVERT}  modified: {filename}")
                elif "D" in status_code:
                    output_lines.append(f"{ICON_DELETE}  deleted: {filename}")
                else:
                    output_lines.append(f"{ICON_INFO}  {filename}")

        if output_lines:
            if not listed:
                print(f"{ICON_WARNING} {group}/{alias} (unlisted, not in YAML)")
            else:
                print(f"{ICON_INFO} {group}/{alias}:")
            for ol in output_lines:
                print(" ", ol)
            print()
            any_status = True
    if not any_status:
        print(f"{ICON_DONE} All repositories are clean.")


# -------------------------------------------------------------------------- }}}
# {{{ Clean a repository untracked files.

def clean_repo(group, alias, repo_dir, listed, options):
    """
    Remove all untracked files from a repo (git clean -fd).
    """
    if not os.path.isdir(repo_dir):
        return (group, alias, "NOT_FOUND", None, listed)
    if options.n:
        return (group, alias, "DRY-RUN", None, listed)
    result = subprocess.run(
        ["git", "-C", repo_dir, "clean", "-fd"],
        capture_output=True, text=True)
    if result.returncode == 0:
        return (group, alias, "CLEANED", None, listed)
    else:
        return (group, alias, "FAIL", result.stderr, listed)


# -------------------------------------------------------------------------- }}}
# {{{ Clean all repositories untracked files.

def clean_all_repos(repo_data, options):
    """
    Remove untracked files from all repositories (or a group).
    Annotates unlisted (not in YAML) repos in the output.
    """
    jobs = list(iter_repo_dirs(repo_data, options))
    print(f"{ICON_CLEAN} Cleaning untracked files in {len(jobs)} repositories...\n")

    results = []
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {
            executor.submit(clean_repo, group, alias, repo_dir, listed, options): (group, alias, listed)
            for group, alias, repo_dir, listed in jobs
        }
        for future in as_completed(future_to_job):
            group, alias, status, msg, listed = future.result()
            label = f"{group}/{alias}"
            extra = f" {ICON_WARNING}(unlisted, not in YAML)" if not listed else ""
            if status == "CLEANED":
                icon = ICON_DONE
            elif status == "FAIL":
                icon = ICON_ERROR
            elif status == "DRY-RUN":
                icon = ICON_INFO
            elif status == "NOT_FOUND":
                icon = ICON_WARNING
            else:
                icon = ICON_INFO
            print(f"{icon} {label}{extra}")
            if msg and status == "FAIL":
                print(f"    {ICON_ERROR} Error: {msg.strip()}")

    print(f"\n{ICON_DONE} Clean complete.")

# -------------------------------------------------------------------------- }}}
# {{{ Convert uft16 to utf8 files in a repository.

def convert_utf16_to_utf8_in_repo(group, alias, repo_dir, listed, options):
    """
    Recursively convert UTF-16 files to UTF-8 in a repo.
    Only files with UTF-16 BOM (little/big endian) are converted.
    Returns: (group, alias, status, converted_files_count, listed)
    """
    if not os.path.isdir(repo_dir):
        return (group, alias, "NOT_FOUND", 0, listed)
    converted_files = 0
    for root, _, files in os.walk(repo_dir):
        for fname in files:
            path = os.path.join(root, fname)
            try:
                with open(path, "rb") as f:
                    raw = f.read(4)
                    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
                        if options.n:
                            converted_files += 1
                            if options.v:
                                print(f"{ICON_CONVERT} (Dry-run) Would convert: {path}")
                            continue
                        with open(path, "r", encoding="utf-16") as fi:
                            data = fi.read()
                        with open(path, "w", encoding="utf-8") as fo:
                            fo.write(data)
                        converted_files += 1
                        if options.v:
                            print(f"{ICON_CONVERT} Converted: {path}")
            except Exception as e:
                if options.v:
                    print(f"{ICON_WARNING} Failed to check/convert {path}: {e}")
    return (group, alias, "CONVERTED", converted_files, listed)


# -------------------------------------------------------------------------- }}}
# {{{ Convert uft16 to utf8 files in all repository.

def convert_all_utf16(repo_data, options):
    """
    Convert all UTF-16 files to UTF-8 in all repositories (parallel).
    Annotates unlisted (not in YAML) repos in output.
    """
    jobs = list(iter_repo_dirs(repo_data, options))
    print(f"{ICON_CONVERT} Checking for UTF-16 files in {len(jobs)} repositories...\n")

    results = []
    max_workers = 4
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_job = {
            executor.submit(convert_utf16_to_utf8_in_repo, group, alias, repo_dir, listed, options): (group, alias, listed)
            for group, alias, repo_dir, listed in jobs
        }
        for future in as_completed(future_to_job):
            group, alias, status, converted, listed = future.result()
            label = f"{group}/{alias}"
            extra = f" {ICON_WARNING}(unlisted, not in YAML)" if not listed else ""
            icon = ICON_DONE if converted else ICON_INFO
            print(f"{icon} {label}{extra} files converted: {converted}")
    print(f"\n{ICON_DONE} UTF-16 to UTF-8 conversion complete.")

# -------------------------------------------------------------------------- }}}
# {{{ Load and validae repository location file.

def load_and_validate_repo_data():
    """
    Loads and validates the repository_locations.yml config file.
    Exits with a clear error message if missing or malformed.
    Returns:
        repo_data (dict): Validated repo data from YAML.
    """
    repository_locations_path = os.path.expanduser("~/.config/gits/repository_locations.yml")
    repo_data = load_repos_yaml(repository_locations_path)
    try:
        validate_repo_data(repo_data)
    except ValueError as err:
        print(f"{ICON_ERROR} YAML validation error: {err}")
        sys.exit(1)
    return repo_data

# -------------------------------------------------------------------------- }}}
# {{{ CLI dispatch with match/case

def dispatch_command(repo_data, options):
    """
    Dispatch CLI command using Python 3.10+ match/case for clarity and future extensibility.
    """
    max_workers = 4

    match True:
        case _ if options.h:
            print_help()
            sys.exit(0)

        case _ if options.l:
            list_repos(repo_data, options)
            sys.exit(0)

        case _ if options.c:
            clone_all_repos(repo_data, options)
            sys.exit(0)

        case _ if options.d:
            delete_all_repos(repo_data, options)
            sys.exit(0)

        case _ if options.p:
            pull_all_repos(repo_data, options)
            sys.exit(0)

        case _ if options.s:
            list_status_repos(repo_data, options)
            sys.exit(0)

        case _ if options.x:
            clean_all_repos(repo_data, options)
            sys.exit(0)

        case _ if options.u:
            convert_all_utf16(repo_data, options)
            sys.exit(0)

# -------------------------------------------------------------------------- }}}
# {{{ Main orchestrates the show.

def main():
    options = Options(parse_args())
    repo_data = load_and_validate_repo_data()
    dispatch_command(repo_data, options)

if __name__ == '__main__':
    main()

# -------------------------------------------------------------------------- }}}
