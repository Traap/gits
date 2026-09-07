from gits.utils.config_loader import Repository, load_repos


def selected_groups(repo_group=None):
    groups = load_repos()
    if repo_group is None:
        return groups
    selected = [group for group in groups if group.name == repo_group]
    if not selected:
        raise ValueError(f"Unknown repository group: {repo_group}")
    return selected


def discover_repos(group):
    """Discover immediate Git working directories, including worktrees."""
    if not group.root.is_dir():
        return []
    known = {repo.path.resolve() for repo in group.repositories}
    return [
        Repository(group.name, path.name, path, unlisted=True)
        for path in sorted(group.root.iterdir())
        if path.is_dir() and (path / ".git").exists() and path.resolve() not in known
    ]


def filtered_repos(repo_group=None, include_unlisted=False):
    return [
        repo
        for group in selected_groups(repo_group)
        for repo in (*group.repositories, *(discover_repos(group) if include_unlisted else ()))
    ]
