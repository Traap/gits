### Gits

**Gits** is a simple tool to manage groups of git repositories.

### Features
- Clone multiple repositories into categorized folders
- Pull updates across repositories
- Define custom repo sets using an external config
- Compact CLI with short options (`-c`, `-r`, etc.)

### Installation
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```

### Removal
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Traap/gits/master/install.sh)"
```

### Use
```concole
Usage: gits [options] [repo-locations...]

Options:
  -h          Show help
  -l          List repository locations
  -c          Clone missing repositories
  -r          Pull latest changes (default)
  -p          Alias for -r (pull)
  -d          Dry-run (simulate)
  -v          Verbose output
```
